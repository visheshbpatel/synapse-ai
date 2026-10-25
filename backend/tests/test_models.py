from sqlalchemy import func, select

from app.models import APIKey, Chunk, Conversation, Document, User
from app.security import hash_password


def test_user_deletion_cascades_to_all_child_rows(db_session):
    user = User(
        username="cascadeuser",
        email="cascade@example.com",
        password_hash=hash_password("StrongPassword123!"),
    )
    db_session.add(user)
    db_session.flush()

    document = Document(
        user_id=user.id,
        filename="test.pdf",
        content_hash="a" * 64,
        size_bytes=100,
        status="ready",
    )
    db_session.add(document)
    db_session.flush()

    chunk = Chunk(
        document_id=document.id,
        user_id=user.id,
        chunk_index=0,
        content="Test chunk content",
        embedding=[0.0] * 384,
    )
    conversation = Conversation(user_id=user.id, title="Test conversation")
    api_key = APIKey(
        user_id=user.id,
        name="Test key",
        key_hash="b" * 64,
        prefix="testkey1",
    )
    db_session.add_all([chunk, conversation, api_key])
    db_session.flush()

    db_session.delete(user)
    db_session.commit()

    for model in (User, Document, Chunk, Conversation, APIKey):
        count = db_session.scalar(select(func.count()).select_from(model))
        assert count == 0, f"{model.__tablename__} rows remain after user deletion"
