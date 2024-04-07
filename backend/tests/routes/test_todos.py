from tests.utils.todo_factory import TodoFactory


def test_create_todo(client, token):
    resp = client.post(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Todo",
            "description": "Test Desc",
            "state": "draft",
        },
    )

    assert resp.json() == {
        "id": 1,
        "title": "Test Todo",
        "description": "Test Desc",
        "state": "draft",
    }


def test_get_todos(session, client, user, token):
    session.bulk_save_objects(TodoFactory.create_batch(10, user_id=user.id))
    session.commit()

    resp = client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(resp.json()["todos"]) == 10


def test_get_todos_pagination(session, client, user, token):
    session.bulk_save_objects(TodoFactory.create_batch(10, user_id=user.id))
    session.commit()

    resp = client.get(
        "/todos/?offset=2&limit=4",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(resp.json()["todos"]) == 4


def test_get_todos_filter_title(session, client, user, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(10, user_id=user.id, title="Test")
    )
    session.commit()

    resp = client.get(
        "/todos/?title=Test",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(resp.json()["todos"]) == 10


def test_get_todos_filter_description(session, client, user, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(10, user_id=user.id, description="Test")
    )
    session.commit()

    resp = client.get(
        "/todos/?description=Test",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(resp.json()["todos"]) == 10


def test_get_todos_filter_state(session, client, user, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(10, user_id=user.id, state="done")
    )
    session.bulk_save_objects(
        TodoFactory.create_batch(10, user_id=user.id, state="draft")
    )
    session.commit()

    resp = client.get(
        "/todos/?state=done",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(resp.json()["todos"]) == 10


def test_patch_todo_error(client, token):
    resp = client.patch(
        "/todos/4",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Todo", "description": "Test Desc", "state": "wrong"},
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo를 찾을 수 없습니다."}


def test_patch_todo(client, token, user, session):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    resp = client.patch(
        f"/todos/{todo.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Todo", "description": "Test Desc"},
    )

    assert resp.status_code == 200
    assert resp.json() == {
        "id": todo.id,
        "title": "Test Todo",
        "description": "Test Desc",
        "state": todo.state,
    }


def test_delete_todo(client, token, user, session):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    resp = client.delete(
        f"/todos/{todo.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    assert resp.json() == {"message": f"Todo:{todo.id}가 성공적으로 삭제 되었습니다."}


def test_delete_todo_error(client, token):
    resp = client.delete(
        "/todos/4",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo를 찾을 수 없습니다."}
