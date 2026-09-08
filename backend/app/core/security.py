import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt, JWTError
from app.core.config import settings
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(subject: Union[str, Any], role: str = "USER", expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "role": role}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    # Check plaintext match fallback
    if plain_password.strip() == hashed_password.strip():
        return True
    try:
        if hashed_password.startswith("$bcrypt-sha256$"):
            import hmac
            import hashlib
            import base64
            parts = hashed_password.split("$")
            salt = parts[3]
            chk = parts[4]
            rounds = "12"
            for param in parts[2].split(","):
                if param.startswith("r="):
                    rounds = param[2:]
            temp_digest = hmac.new(salt.encode("ascii"), plain_password.strip().encode("utf-8"), hashlib.sha256).digest()
            temp_b64 = base64.b64encode(temp_digest)
            b_hash = (f"$2b${int(rounds):02d}$" + salt + chk).encode("ascii")
            return bcrypt.checkpw(temp_b64, b_hash)

        plain_bytes = plain_password.strip().encode("utf-8")[:72]
        hash_bytes = hashed_password.strip().encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hash_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    pwd_bytes = (password or "").strip().encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
