from datetime import UTC, datetime, timedelta

import jwt

from app.config import get_settings


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert "created_at" in data
    assert "password_hash" not in data
    assert "password" not in data


def test_register_duplicate_email(client):
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "StrongPassword123!",
    }

    first_response = client.post("/auth/register", json=payload)
    second_response = client.post(
        "/auth/register",
        json={
            **payload,
            "username": "anotheruser",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_success(client):
    client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": "StrongPassword123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "username": "wrongpassuser",
            "email": "wrongpass@example.com",
            "password": "StrongPassword123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "IncorrectPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_register_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "invalidemail",
            "email": "not-an-email",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 422


def test_registration_normalizes_username_and_email(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "Vishesh_Patel",
            "email": "Vishesh.Patel@Example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "vishesh_patel"
    assert response.json()["email"] == "vishesh.patel@example.com"


def test_registration_rejects_invalid_username(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "invalid-name",
            "email": "invalid-name@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 422


def test_register_duplicate_username(client):
    payload = {
        "username": "duplicateuser",
        "email": "first@example.com",
        "password": "StrongPassword123!",
    }

    assert client.post("/auth/register", json=payload).status_code == 201

    response = client.post(
        "/auth/register",
        json={
            **payload,
            "email": "second@example.com",
        },
    )

    assert response.status_code == 409


def test_login_with_different_email_capitalization(client):
    client.post(
        "/auth/register",
        json={
            "username": "caseuser",
            "email": "caseuser@example.com",
            "password": "StrongPassword123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "CaseUser@Example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 200


def test_password_shorter_than_eight_characters(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "shortpass",
            "email": "shortpass@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_login_unknown_email_returns_same_error(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_auth_me_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_with_garbage_token(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer garbage.token.value"},
    )

    assert response.status_code == 401


def test_auth_me_with_expired_token(client):
    settings = get_settings()
    token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_register_login_me_flow_and_response_security(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "flowuser",
            "email": "flow@example.com",
            "password": "StrongPassword123!",
        },
    )
    assert register_response.status_code == 201
    assert "password_hash" not in register_response.json()

    login_response = client.post(
        "/auth/login",
        json={
            "email": "flow@example.com",
            "password": "StrongPassword123!",
        },
    )
    assert login_response.status_code == 200
    assert "password_hash" not in login_response.json()

    token = login_response.json()["access_token"]
    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "flowuser"
    assert "password_hash" not in me_response.json()
