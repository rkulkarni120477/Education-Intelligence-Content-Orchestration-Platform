from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
from config import get_settings
from database.models import User
from sqlalchemy.orm import Session
import secrets
import hashlib
import base64

settings = get_settings()

# Use PBKDF2 instead of bcrypt due to compatibility issues
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, int(expires_delta.total_seconds()) if expires_delta else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def decode_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None:
            return None
        token_data = TokenData(user_id=user_id, email=email)
        return token_data
    except JWTError:
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, username: str, full_name: str, password: str) -> User:
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hashed_password,
        email_verified=True  # Auto-verify for now, can be changed to False for email verification flow
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def generate_password_reset_token(db: Session, user: User) -> str:
    """Generate a password reset token for a user"""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    # Token expires in 24 hours
    expires_at = datetime.utcnow() + timedelta(hours=24)

    user.password_reset_token = token_hash
    user.password_reset_token_expires = expires_at
    db.commit()

    return token


def verify_password_reset_token(db: Session, user: User, token: str) -> bool:
    """Verify if the password reset token is valid"""
    if not user.password_reset_token or not user.password_reset_token_expires:
        return False

    # Check if token has expired
    if datetime.utcnow() > user.password_reset_token_expires:
        return False

    # Verify token hash
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return user.password_reset_token == token_hash


def reset_password(db: Session, user: User, new_password: str) -> None:
    """Reset user password and clear reset token"""
    user.hashed_password = get_password_hash(new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None
    db.commit()


def generate_email_verification_token(db: Session, user: User) -> str:
    """Generate email verification token"""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    user.email_verification_token = token_hash
    db.commit()

    return token


def verify_email_token(db: Session, user: User, token: str) -> bool:
    """Verify email verification token"""
    if not user.email_verification_token:
        return False

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if user.email_verification_token == token_hash:
        user.email_verified = True
        user.email_verification_token = None
        db.commit()
        return True

    return False


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def update_last_login(db: Session, user: User) -> None:
    """Update user's last login timestamp"""
    user.last_login = datetime.utcnow()
    db.commit()
