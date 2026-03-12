import uuid
from datetime import datetime
from typing import Optional
from app.core.database import get_db
from app.models.schemas import UserSession, ResponseRecord


SESSIONS_COLLECTION = "user_sessions"


async def create_session(max_questions: int = 10) -> UserSession:
    db = get_db()
    session = UserSession(
        session_id=str(uuid.uuid4()),
        ability_score=0.5,
        max_questions=max_questions,
    )
    await db[SESSIONS_COLLECTION].insert_one(session.dict())
    return session


async def get_session(session_id: str) -> Optional[UserSession]:
    db = get_db()
    doc = await db[SESSIONS_COLLECTION].find_one({"session_id": session_id})
    if not doc:
        return None
    doc.pop("_id", None)
    return UserSession(**doc)


async def update_session(session: UserSession) -> None:
    db = get_db()
    session.updated_at = datetime.utcnow()
    await db[SESSIONS_COLLECTION].update_one(
        {"session_id": session.session_id},
        {"$set": session.dict()},
    )


async def append_response(session_id: str, record: ResponseRecord) -> None:
    db = get_db()
    await db[SESSIONS_COLLECTION].update_one(
        {"session_id": session_id},
        {
            "$push": {"responses": record.dict()},
            "$set": {"updated_at": datetime.utcnow()},
        },
    )
