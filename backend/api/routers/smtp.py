from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from api.db.database import SessionLocal
from api.db.models.settings import SMTPSettings
from api.auth.jwt import get_auth_wrapper
from api.auth.auth import auth_check
from typing import Optional

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SMTPSettingsSchema(BaseModel):
    server: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    sender_email: EmailStr
    use_tls: bool = True

class TestEmailSchema(BaseModel):
    recipient: EmailStr

@router.get("/", response_model=SMTPSettingsSchema)
def get_smtp_settings(db: Session = Depends(get_db), Authorize: get_auth_wrapper = Depends(get_auth_wrapper)):
    auth_check(Authorize)
    settings = db.query(SMTPSettings).first()
    if not settings:
        # Return default or empty
        return SMTPSettingsSchema(server="", port=587, sender_email="admin@example.com")
    return settings

@router.post("/", response_model=SMTPSettingsSchema)
def update_smtp_settings(settings: SMTPSettingsSchema, db: Session = Depends(get_db), Authorize: get_auth_wrapper = Depends(get_auth_wrapper)):
    auth_check(Authorize)
    db_settings = db.query(SMTPSettings).first()
    if not db_settings:
        db_settings = SMTPSettings(**settings.dict())
        db.add(db_settings)
    else:
        for key, value in settings.dict().items():
            setattr(db_settings, key, value)
    db.commit()
    db.refresh(db_settings)
    return db_settings

@router.post("/test")
def send_test_email(email_data: TestEmailSchema, db: Session = Depends(get_db), Authorize: get_auth_wrapper = Depends(get_auth_wrapper)):
    auth_check(Authorize)
    settings = db.query(SMTPSettings).first()
    if not settings:
        raise HTTPException(status_code=400, detail="SMTP settings not configured")

    msg = MIMEText("This is a test email from Yacht.")
    msg['Subject'] = 'Yacht Test Email'
    msg['From'] = settings.sender_email
    msg['To'] = email_data.recipient

    try:
        if settings.use_tls:
            server = smtplib.SMTP(settings.server, settings.port)
            server.starttls()
        else:
            server = smtplib.SMTP(settings.server, settings.port)

        if settings.username and settings.password:
            server.login(settings.username, settings.password)

        server.sendmail(settings.sender_email, email_data.recipient, msg.as_string())
        server.quit()
        return {"message": "Test email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
