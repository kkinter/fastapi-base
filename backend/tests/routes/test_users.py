from app.schemas import UserPublic


def test_create_user(client):
    resp = client.post(
        "/users/",
        json={"username": "wook", "email": "wook@wook.com", "password": "wook"},
    )
    assert resp.status_code == 201
    assert resp.json() == {
        "username": "wook",
        "email": "wook@wook.com",
        "id": 1,
    }


def test_read_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == []


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users/")
    assert response.json() == [user_schema]


def test_update_user(client, user, token):
    resp = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "woos", "email": "wook@wook.com", "password": "wwwwww"},
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "username": "woos",
        "email": "wook@wook.com",
        "id": user.id,
    }


def test_delete_user(client, user, token):
    resp = client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"message": "User deleted"}


def test_update_user_with_wrong_user(client, other_user, token):
    resp = client.put(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "woos", "email": "wook@wook.com", "password": "<PASSWORD>"},
    )

    assert resp.status_code == 400
    assert resp.json() == {"detail": "권한이 없습니다."}


def test_delete_user_wrong_user(client, other_user, token):
    resp = client.delete(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": "권한이 없습니다."}
