from datetime import timedelta

import pytest

from app.security import (
    InvalidTokenError,
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
    token = create_access_token(user_id=1)

    assert decode_access_token(token) == 1


def test_expired_token_is_rejected():
    expired_token = create_access_token(
        user_id=1,
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(expired_token)


def test_invalid_token_is_rejected():
    with pytest.raises(InvalidTokenError):
        decode_access_token("invalid.token.value")
