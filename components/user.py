from components.auth import hash_password
from components.database import get_connection
from components.auth import verify_password


def create_user(username: str, email: str, password: str):
    password_hash = hash_password(password)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (username, email, password_hash),
        )

        connection.commit()

        return cursor.lastrowid


def get_user_by_email(email: str):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, username, email, password_hash, created_at
            FROM users
            WHERE email = ?
            """,
            (email,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "password_hash": row[3],
            "created_at": row[4],
        }


def get_user_by_username(username: str):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, username, email, password_hash, created_at
            FROM users
            WHERE username = ?
            """,
            (username,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "password_hash": row[3],
            "created_at": row[4],
        }


def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)

    if user is None:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
    }