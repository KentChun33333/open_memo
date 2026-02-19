"""Simple authentication with username/password + JWT tokens."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from backend.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class User(BaseModel):
    username: str


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    """Get current user from JWT token. Returns None if not authenticated."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            return None
        return User(username=username)
    except JWTError:
        return None


async def require_auth(user: Optional[User] = Depends(get_current_user)) -> User:
    """Require authentication. Raises 401 if not authenticated."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Hash the admin password at startup
_admin_hash = pwd_context.hash(settings.admin_password)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username and password, returns JWT token."""
    if form_data.username != settings.admin_username or not verify_password(
        form_data.password, _admin_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token(data={"sub": form_data.username})
    return Token(access_token=token)


@router.get("/me", response_model=User)
async def get_me(user: User = Depends(require_auth)):
    """Get current authenticated user."""
    return user
