from app.models import Todo, User
from sqlalchemy import select


def test_create_user(session):
    new_user = User(username="alice", password="secret", email="teste@test")
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == "alice"))

    assert user.username == "alice"


def test_create_todo(session, user):
    todo = Todo(
        title="Test Todo",
        description="Test Desc",
        state="draft",
        user_id=user.id,
    )

    session.add(todo)
    session.commit()
    session.refresh(todo)

    user = session.query(User).filter(User.id == user.id).first()

    assert todo in user.todos
