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
    assert data["is_active"] is True
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
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


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
