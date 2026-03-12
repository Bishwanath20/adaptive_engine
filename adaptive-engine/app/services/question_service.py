from typing import List, Optional
from app.core.database import get_db

QUESTIONS_COLLECTION = "questions"


async def get_all_questions() -> List[dict]:
    db = get_db()
    cursor = db[QUESTIONS_COLLECTION].find({}, {"_id": 0})
    return await cursor.to_list(length=None)


async def get_question_by_id(question_id: str) -> Optional[dict]:
    db = get_db()
    doc = await db[QUESTIONS_COLLECTION].find_one({"question_id": question_id}, {"_id": 0})
    return doc


async def question_count() -> int:
    db = get_db()
    return await db[QUESTIONS_COLLECTION].count_documents({})
