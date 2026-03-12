from fastapi import APIRouter, HTTPException
from app.services.question_service import get_all_questions, get_question_by_id, question_count

router = APIRouter()


@router.get("/questions")
async def list_questions():
    """List all questions in the question bank (admin/debug endpoint)."""
    questions = await get_all_questions()
    return {"total": len(questions), "questions": questions}


@router.get("/questions/{question_id}")
async def get_question(question_id: str):
    """Fetch a single question by ID."""
    q = await get_question_by_id(question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
    return q


@router.get("/questions-count")
async def count_questions():
    count = await question_count()
    return {"count": count}
