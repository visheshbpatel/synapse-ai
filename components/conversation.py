from components.database import get_connection


def init_conversations_table():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                thread_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        connection.commit()


def create_conversation(user_id, thread_id, title):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO conversations (user_id, thread_id, title)
            VALUES (?, ?, ?)
            """,
            (user_id, thread_id, title),
        )
        connection.commit()


def get_conversations(user_id):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT thread_id, title, created_at, updated_at
            FROM conversations
            WHERE user_id = ?
            ORDER BY updated_at DESC
            """,
            (user_id,),
        )

        return [
            {
                "thread_id": row[0],
                "title": row[1],
                "created_at": row[2],
                "updated_at": row[3],
            }
            for row in cursor.fetchall()
        ]


def get_conversation(user_id, thread_id):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT thread_id, title, created_at, updated_at
            FROM conversations
            WHERE user_id = ? AND thread_id = ?
            """,
            (user_id, thread_id),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "thread_id": row[0],
            "title": row[1],
            "created_at": row[2],
            "updated_at": row[3],
        }


def update_conversation(user_id, thread_id, title):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE conversations
            SET title = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND thread_id = ?
            """,
            (title, user_id, thread_id),
        )
        connection.commit()


def touch_conversation(user_id, thread_id):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND thread_id = ?
            """,
            (user_id, thread_id),
        )
        connection.commit()


init_conversations_table()
