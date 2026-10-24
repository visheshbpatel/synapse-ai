from datetime import datetime, timedelta, timezone

import jwt

from app.config import get_settings
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    password = "secure-test-password"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_password_hashes_are_unique():
    password = "secure-test-password"

    assert hash_password(password) != hash_password(password)


def test_access_token_creation_and_decoding():
    token = create_access_token("1")
    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert "exp" in payload


def test_expired_token_is_rejected():
    settings = get_settings()
    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    try:
        decode_access_token(expired_token)
        assert False, "Expected an expired token to be rejected"
    except jwt.ExpiredSignatureError:
        pass


def test_invalid_token_is_rejected():
    try:
        decode_access_token("invalid.token.value")
        assert False, "Expected an invalid token to be rejected"
    except jwt.InvalidTokenError:
        pass
