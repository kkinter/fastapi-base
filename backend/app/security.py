from datetime import datetime, timedelta
from typing import Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_credentials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_confirmation_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(
        minutes=settings.CONFIRMATION_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "confirmation"})
    encoded_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# 특정 type 에 대한 페이로드의 sub 을 가져온다
def get_subject_for_token_type(token: str, type: Literal["access", "confirmation"]):
    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise create_credentials_exception("토큰이 만료되었습니다.")
    except DecodeError:
        raise create_credentials_exception("토큰이 잘못되었습니다.")

    email = payload.get("sub")

    if not email:
        raise create_credentials_exception("토큰에 Sub 필드가 없습니다.")

    token_type = payload.get("type")

    if token_type is None or token_type != type:
        raise create_credentials_exception("토큰의 타입이 잘못되었습니다.")

    return email


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    email = get_subject_for_token_type(token, "access")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise create_credentials_exception("이 토큰의 사용자를 찾을 수 없습니다.")

    return user
