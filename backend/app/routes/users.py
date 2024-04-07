from typing import Annotated

from app.database import get_db
from app.models import User
from app.schemas import Message, UserPublic, UserSchema
from app.security import get_current_user, get_password_hash
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", status_code=201, response_model=UserPublic)
def create_user(user: UserSchema, db: SessionDep):
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

    return db_user


@router.get("/", response_model=list[UserPublic])
def read_users(db: SessionDep, skip: int = 0, limit: int = 100):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.put("/{user_id}", response_model=UserPublic)
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

    # db_user = db.query(User).filter(User.id == user_id).first()

    # if not db_user:
    #     raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # db.delete(db_user)
    # db.commit()
    db.delete(current_user)
    db.commit()

    return {"message": "User deleted"}
