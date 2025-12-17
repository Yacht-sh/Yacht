import ipaddress
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from api.db.models.settings import SMTPSettings
from api.db.models.users import LoginAttempt, User

def is_private_ip(ip: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False # Invalid IP, treat as public/unsafe

def send_security_alert(db: Session, ip_address: str, reason: str, username: str = None):
    settings = db.query(SMTPSettings).first()
    if not settings:
        print("SMTP Settings not found, cannot send alert.")
        return

    admin_user = db.query(User).filter(User.username == settings.sender_email).first() # Fallback to sender email if admin email not stored explicitly
    # Better: Use the ADMIN_EMAIL from env or find superuser
    admin = db.query(User).filter(User.is_superuser == True).first()
    recipient = admin.username if admin else settings.sender_email

    subject = f"Security Alert: {reason}"
    body = f"""
    Security Alert for Yacht Server.

    Reason: {reason}
    IP Address: {ip_address}
    Username Attempted: {username or 'Unknown'}
    Timestamp: {datetime.utcnow()}

    This IP has been blocked or restricted.
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = settings.sender_email
    msg['To'] = recipient

    try:
        if settings.use_tls:
            server = smtplib.SMTP(settings.server, settings.port)
            server.starttls()
        else:
            server = smtplib.SMTP(settings.server, settings.port)

        if settings.username and settings.password:
            server.login(settings.username, settings.password)

        server.sendmail(settings.sender_email, recipient, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send security alert: {e}")

def check_ip_restriction(request: Request, db: Session, username: str = None):
    # Support X-Forwarded-For if running behind proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For: <client>, <proxy1>, <proxy2>
        # We take the first one as client ip
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host

    # 1. Check IP Restriction (Allow only private IPs by default?)
    # For now, let's hardcode this policy or check a setting if we had one.
    # The requirement: "blocks by default all non private ip adresses"
    if not is_private_ip(client_ip):
         send_security_alert(db, client_ip, "Non-Private IP Login Attempt Blocked", username)
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied from public IP.")

    # 2. Check Failed Attempts (Fail2Ban logic)
    # limit: 5 failed attempts in last 15 minutes
    time_threshold = datetime.utcnow() - timedelta(minutes=15)
    failed_attempts = db.query(LoginAttempt).filter(
        LoginAttempt.ip_address == client_ip,
        LoginAttempt.success == False,
        LoginAttempt.timestamp >= time_threshold
    ).count()

    if failed_attempts >= 5:
        send_security_alert(db, client_ip, "Too many failed login attempts (Fail2Ban)", username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="IP blocked due to too many failed login attempts.")

    return client_ip

def record_login_attempt(db: Session, ip_address: str, username: str, success: bool):
    attempt = LoginAttempt(ip_address=ip_address, username=username, success=success)
    db.add(attempt)
    db.commit()
