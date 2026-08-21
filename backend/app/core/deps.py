from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_current_user_optional(token: str = Depends(oauth2_scheme_optional), db = Depends(get_db)):
    if not token or token == "null" or token == "undefined":
        return None
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        uid: str = payload.get("sub")
        if not uid:
            return None
        if db is not None:
            try:
                user = await db["users"].find_one({"uid": uid})
                if user:
                    user["id"] = str(user.get("_id", uid))
                    return user
            except Exception:
                pass
        return {
            "uid": uid,
            "id": uid,
            "role": payload.get("role", "USER"),
            "name": payload.get("name", "User"),
            "email": payload.get("email", ""),
            "phone": payload.get("phone", "")
        }
    except Exception:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    user = await get_current_user_optional(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
