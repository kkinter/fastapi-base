from typing import Annotated

from app.database import get_db
from app.models import User
from app.schemas import Token
from app.security import create_access_token, get_current_user, verify_password
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2Form,
    db: SessionDep,
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=400, detail="이메일 또는 비밀번호가 틀렸습니다."
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail="이메일 또는 비밀번호가 틀렸습니다."
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="계정이 활성화 되지 않았습니다.")

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh_token", response_model=Token)
def refresh_access_token(
    user: User = Depends(get_current_user),
):
    new_access_token = create_access_token(data={"sub": user.email})

    return {"access_token": new_access_token, "token_type": "bearer"}
