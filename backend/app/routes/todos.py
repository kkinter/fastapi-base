from typing import Annotated

from app.database import get_db
from app.models import Todo, User
from app.schemas import Message, TodoList, TodoPublic, TodoSchema, TodoUpdate
from app.security import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/todos", tags=["todos"])

CurrentUser = Annotated[User, Depends(get_current_user)]
SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=TodoPublic)
def create_todo(todo: TodoSchema, user: CurrentUser, db: Session = Depends(get_db)):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    return db_todo


@router.get("/", response_model=TodoList)
def get_todos(
    db: SessionDep,
    user: CurrentUser,
    title: str = Query(None),
    description: str = Query(None),
    state: str = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
):
    q = db.query(Todo).filter(Todo.user_id == user.id)

    if title:
        q = q.filter(Todo.title.contains(title))

    if description:
        q = q.filter(Todo.description.contains(description))

    if state:
        q = q.filter(Todo.state == state)

    todos = q.offset(offset).limit(limit).all()

    return {"todos": todos}


@router.patch("/{todo_id}", response_model=TodoPublic)
def patch_todo(todo_id: int, db: SessionDep, user: CurrentUser, todo: TodoUpdate):
    db_todo = (
        db.query(Todo).filter(Todo.user_id == user.id, Todo.id == todo_id).scalar()
    )

    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo를 찾을 수 없습니다.")

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    return db_todo


@router.delete("/{todo_id}", response_model=Message)
def delete_todo(todo_id: int, db: SessionDep, user: CurrentUser):
    db_todo = (
        db.query(Todo).filter(Todo.user_id == user.id, Todo.id == todo_id).scalar()
    )

    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo를 찾을 수 없습니다.")

    db.delete(db_todo)
    db.commit()

    return {"message": f"Todo:{todo_id}가 성공적으로 삭제 되었습니다."}
