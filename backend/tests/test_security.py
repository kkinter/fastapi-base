from app.config import settings
from app.security import create_access_token, create_confirmation_token
from jwt import decode


def test_create_access_token():
    data = {"test": "test"}
    token = create_access_token(data)

    decoded_token = decode(token, settings.SECRET_KEY, algorithms=["HS256"])

    assert decoded_token["test"] == "test"
    assert decoded_token["type"] == "access"


def test_create_confirmation_token():
    data = {"test": "test"}
    token = create_confirmation_token(data)

    decoded_token = decode(token, settings.SECRET_KEY, algorithms=["HS256"])

    assert decoded_token["test"] == "test"
    assert decoded_token["type"] == "confirmation"
