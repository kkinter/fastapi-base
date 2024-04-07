from app.config import settings
from app.security import create_access_token
from jwt import decode


def test_jwt():
    data = {"test": "test"}
    token = create_access_token(data)

    decoded_token = decode(token, settings.SECRET_KEY, algorithms=["HS256"])

    assert decoded_token["test"] == "test"
