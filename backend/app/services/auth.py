# backend/app/services/auth.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..config import settings
import hashlib

# KORISTI pbkdf2_sha256 UMESTO bcrypt - nema problema sa verzijama
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "django_argon2", "django_bcrypt"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    # pbkdf2_sha256 nema limit od 72 bytes i stabilniji je
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any]) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, is_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        if is_refresh:
            secret_key = settings.REFRESH_SECRET_KEY
            payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
            if payload.get("type") != "refresh":
                return None
        else:
            secret_key = settings.SECRET_KEY
            payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
            if payload.get("type") != "access":
                return None

        # Provjeri je li token istekao
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            return None

        return payload
    except JWTError:
        return None