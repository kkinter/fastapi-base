from typing import Annotated

from app.database import get_db
from app.models import User
from app.schemas import Message, UserPublic, UserSchema
from app.security import (
    create_confirmation_token,
    get_current_user,
    get_password_hash,
    get_subject_for_token_type,
)
from app.tasks import send_user_registration_email
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Message)
def create_user(
    user: UserSchema,
    db: SessionDep,
    background_tasks: BackgroundTasks,
    request: Request,
):
    db_user = db.query(User).filter(User.username == user.username).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Username이 이미 존재합니다.")

    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    background_tasks.add_task(
        send_user_registration_email,
        db_user.email,
        activation_url=request.url_for(
            "confirm_email",
            token=create_confirmation_token(data={"sub": db_user.email}),
        ),
    )

    return {"message": "유저가 생성되었습니다. 이메일을 확인해주세요."}


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[UserPublic])
def read_users(db: SessionDep, skip: int = 0, limit: int = 100):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    db: SessionDep,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail="권한이 없습니다.")

    current_user.username = user.username
    current_user.password = get_password_hash(user.password)
    current_user.email = user.email

    db.commit()
    db.refresh(current_user)

    return current_user


@router.delete("/{user_id}", response_model=Message)
def delete_user(
    user_id: int,
    db: SessionDep,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail="권한이 없습니다.")

    db.delete(current_user)
    db.commit()

    return {"message": "User deleted"}


@router.get("/confirm/{token}", response_model=Message)
def confirm_email(token: str, db: SessionDep):
    email = get_subject_for_token_type(token, "confirmation")
    db.query(User).filter(User.email == email).update({"is_active": True})
    db.commit()

    return {"message": "Email confirmed"}
