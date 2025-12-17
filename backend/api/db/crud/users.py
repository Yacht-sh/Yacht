from sqlalchemy.orm import Session
from passlib.context import CryptContext
from api.db.models import users as models
from api.db.models.settings import TokenBlacklist
from api.db.schemas import users as schemas
from api.settings import Settings
from fastapi.exceptions import HTTPException
from datetime import datetime
import secrets
from api.auth.jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = Settings()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, username: str):
    return (
        db.query(models.User)
        .filter(models.User.username == username.casefold())
        .first()
    )


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    _hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=_hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        perm_start=user.perm_start,
        perm_stop=user.perm_stop,
        perm_restart=user.perm_restart,
        perm_delete=user.perm_delete
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: schemas.UserUpdate, current_user):
    # current_user here is a STRING (username) from jwt subject
    # unless called with user object.
    # The router passes current_user as string usually.
    # But wait, `update_user_admin` in router might pass something else?
    # Let's clarify usage.
    # Standard user self-update: `current_user` is their username.
    # Admin update: we are updating a specific user object/ID.

    # This function seems designed for "self update" primarily or generic update if `current_user` is the user to be updated?
    # Original code: `_user = get_user_by_name(db=db, username=current_user)`
    # This implies it updates the user WHO IS LOGGED IN.

    # We need a separate function or logic for Admin updating OTHER users.

    _hashed_password = get_password_hash(user.password) if user.password else None
    _user = get_user_by_name(db=db, username=current_user)

    if _user and _user.is_active:
        if user.username and _user.username.casefold() != user.username.casefold():
            print("Old Username: {name}".format(name=_user.username))
            print("New Username: {name}".format(name=user.username))
            _user.username = user.username.casefold()

        if user.password:
            _user.hashed_password = _hashed_password

        try:
            db.add(_user)
            db.commit()
            db.refresh(_user)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=exc)
        return _user

def update_user_by_id(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    if user_update.username:
        db_user.username = user_update.username
    if user_update.password:
        db_user.hashed_password = get_password_hash(user_update.password)

    # Update permissions if provided
    if user_update.is_active is not None:
        db_user.is_active = user_update.is_active
    if user_update.is_superuser is not None:
        db_user.is_superuser = user_update.is_superuser
    if user_update.perm_start is not None:
        db_user.perm_start = user_update.perm_start
    if user_update.perm_stop is not None:
        db_user.perm_stop = user_update.perm_stop
    if user_update.perm_restart is not None:
        db_user.perm_restart = user_update.perm_restart
    if user_update.perm_delete is not None:
        db_user.perm_delete = user_update.perm_delete

    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def prune_blacklist(db: Session):
    expired_list = []
    db.query(TokenBlacklist).filter(TokenBlacklist.expires < datetime.utcnow()).delete()
    db.commit()
    return


def blacklist_api_key(key_id, db: Session):
    key = db.query(models.APIKEY).filter(models.APIKEY.id == key_id).first()
    if key:
        access = TokenBlacklist(jti=key.jti, expires=None, revoked=True)
        db.add(access)
        db.delete(key)
        db.commit()
        return {"success": "api key " + str(key_id) + " deleted."}
    return {"error": "Key not found"}


def blacklist_login_token(Authorize, db: Session):
    # This feature is temporarily disabled as we moved away from fastapi-jwt-auth
    # and haven't fully implemented blacklist logic in new system yet.
    return


def get_keys(user, db: Session):
    keys = db.query(models.APIKEY).filter(models.APIKEY.user == user.id).all()
    return keys


def create_key(key_name, user, Authorize, db: Session):
    # Use our custom create_access_token from api.auth.jwt
    # Note: create_access_token returns the encoded string.
    # We need JTI. Our custom implementation puts username in 'sub'.
    # It doesn't generate a JTI by default unless we add it.
    # To support blacklisting, we should add JTI.

    import uuid
    jti = str(uuid.uuid4())

    # We create a long-lived token (or infinite if expires_delta is large)
    # Original used expires_time=False.
    # Our create_access_token uses default 15 mins if not provided.
    from datetime import timedelta
    # 10 years expiration for API key effectively
    expires = timedelta(days=365*10)

    api_key = create_access_token(
        data={"sub": user.username, "jti": jti},
        expires_delta=expires
    )

    _hashed_key = get_password_hash(api_key)

    db_key = models.APIKEY(
        key_name=key_name, user=user.id, hashed_key=_hashed_key, jti=jti
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    db_key.token = api_key
    return db_key.__dict__
