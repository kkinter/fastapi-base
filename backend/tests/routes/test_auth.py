from datetime import datetime, timedelta

from app.config import settings
from freezegun import freeze_time


def test_get_token(client, user):
    resp = client.post(
        "/auth/token",
        data={"username": user.email, "password": user.clean_password},
    )
    token = resp.json()
    print(token)
    assert resp.status_code == 200
    assert "access_token" in token
    assert "token_type" in token


def test_token_expired_after_time(client, user):
    cur = datetime.now()
    with freeze_time(cur):
        resp = client.post(
            "/auth/token",
            data={"username": user.email, "password": user.clean_password},
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]
    with freeze_time(cur + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1)):
        resp = client.put(
            f"/users/{user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "wrongwrong",
                "email": "wrong@wrong.com",
                "password": "wrong",
            },
        )
        assert resp.status_code == 401
        assert resp.json() == {"detail": "토큰이 만료되었습니다."}


def test_token_wrong_password(client, user):
    resp = client.post(
        "/auth/token",
        data={"username": "no_user@no_domain.com", "password": "testtest"},
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": "이메일 또는 비밀번호가 틀렸습니다."}


def test_token_inexistent_user(client):
    resp = client.post(
        "/auth/token",
        data={"username": "no_user@no_domain.com", "password": "testtest"},
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": "이메일 또는 비밀번호가 틀렸습니다."}


def test_refresh_token(client, user, token):
    resp = client.post(
        "/auth/refresh_token",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = resp.json()

    assert resp.status_code == 200
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_token_expired_dont_refresh(client, user):
    cur = datetime.now()
    with freeze_time(cur):
        resp = client.post(
            "/auth/token",
            data={"username": user.email, "password": user.clean_password},
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]

    with freeze_time(cur + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1)):
        resp = client.post(
            "/auth/refresh_token",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401
        assert resp.json() == {"detail": "토큰이 만료되었습니다."}
