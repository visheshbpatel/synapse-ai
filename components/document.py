from components.database import get_connection


def create_document(user_id: int, filename: str):

    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id
            FROM documents
            WHERE user_id = ? AND filename = ?
            """,
            (user_id, filename),
        )

        existing_document = cursor.fetchone()

        if existing_document:
            return existing_document[0]

        cursor = connection.execute(
            """
            INSERT INTO documents (user_id, filename)
            VALUES (?, ?)
            """,
            (user_id, filename),
        )

        connection.commit()

        return cursor.lastrowid


def get_documents(user_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, filename, created_at
            FROM documents
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )

        return [
            {
                "id": row[0],
                "filename": row[1],
                "created_at": row[2],
            }
            for row in cursor.fetchall()
        ]


def get_document(user_id: int, document_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, filename, created_at
            FROM documents
            WHERE id = ? AND user_id = ?
            """,
            (document_id, user_id),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "filename": row[1],
            "created_at": row[2],
        }


def delete_document(user_id: int, document_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM documents
            WHERE id = ? AND user_id = ?
            """,
            (document_id, user_id),
        )

        connection.commit()

        return cursor.rowcount > 0


def get_document_by_filename(
    user_id: int,
    filename: str,
):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, filename, created_at
            FROM documents
            WHERE user_id = ? AND filename = ?
            """,
            (user_id, filename),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "filename": row[1],
            "created_at": row[2],
        }