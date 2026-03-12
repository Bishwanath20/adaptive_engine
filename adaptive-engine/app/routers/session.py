from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.schemas import (
    StartSessionRequest, StartSessionResponse,
    NextQuestionResponse, SubmitAnswerRequest,
    SubmitAnswerResponse, StudyPlanResponse,
    ResponseRecord,
)
from app.services import session_service, question_service
from app.services.adaptive import (
    update_ability, select_best_question,
    theta_to_display, display_to_theta,
    analyze_performance,
)
from app.services.llm import generate_study_plan

router = APIRouter()


@router.post("/session/start", response_model=StartSessionResponse)
async def start_session(body: StartSessionRequest):
    """Create a new adaptive test session."""
    session = await session_service.create_session(max_questions=body.max_questions)
    return StartSessionResponse(
        session_id=session.session_id,
        message=f"Session started! You will be asked up to {body.max_questions} questions.",
    )


@router.get("/next-question", response_model=NextQuestionResponse)
async def next_question(session_id: str):
    """Return the next best question for the current ability estimate."""
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.is_complete:
        raise HTTPException(status_code=400, detail="Session is already complete. Fetch your study plan.")

    questions = await question_service.get_all_questions()
    theta = display_to_theta(session.ability_score)

    best_q = select_best_question(theta, questions, session.questions_asked)
    if not best_q:
        raise HTTPException(status_code=404, detail="No more questions available.")

    # Track question as asked
    session.questions_asked.append(best_q["question_id"])
    await session_service.update_session(session)

    return NextQuestionResponse(
        session_id=session_id,
        question_number=len(session.questions_asked),
        total_questions=session.max_questions,
        question_id=best_q["question_id"],
        text=best_q["text"],
        options=best_q["options"],
        topic=best_q["topic"],
        difficulty=best_q["difficulty"],
    )


@router.post("/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(body: SubmitAnswerRequest):
    """Submit an answer, update ability score, and check if session is complete."""
    session = await session_service.get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.is_complete:
        raise HTTPException(status_code=400, detail="Session is already complete.")

    question = await question_service.get_question_by_id(body.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    is_correct = body.selected_answer.upper() == question["correct_answer"].upper()

    # IRT ability update
    theta_before = display_to_theta(session.ability_score)
    theta_after = update_ability(
        theta=theta_before,
        is_correct=is_correct,
        difficulty=question["difficulty"],
        discrimination=question.get("discrimination", 1.0),
        guessing=question.get("guessing", 0.25),
    )
    new_ability = theta_to_display(theta_after)

    # Record response
    record = ResponseRecord(
        question_id=body.question_id,
        topic=question["topic"],
        difficulty=question["difficulty"],
        is_correct=is_correct,
        ability_before=session.ability_score,
        ability_after=new_ability,
        timestamp=datetime.utcnow(),
    )
    session.responses.append(record)
    session.ability_score = new_ability

    questions_answered = len(session.responses)
    is_done = questions_answered >= session.max_questions

    if is_done:
        session.is_complete = True

    await session_service.update_session(session)

    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=question["correct_answer"],
        ability_score=new_ability,
        questions_remaining=max(0, session.max_questions - questions_answered),
        session_complete=is_done,
        message="Great job!" if is_correct else f"Incorrect. The correct answer was {question['correct_answer']}.",
    )


@router.get("/study-plan", response_model=StudyPlanResponse)
async def get_study_plan(session_id: str):
    """Generate and return a personalized AI study plan for a completed session."""
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if not session.is_complete:
        raise HTTPException(status_code=400, detail="Session is not yet complete.")

    correct_count = sum(1 for r in session.responses if r.is_correct)
    performance = analyze_performance(session.responses)

    # Generate and cache plan only once — avoids redundant LLM calls
    if not session.study_plan:
        plan = generate_study_plan(
            ability_score=session.ability_score,
            topic_breakdown=performance["topic_breakdown"],
            weak_topics=performance["weak_topics"],
            total_questions=len(session.responses),
            correct_answers=correct_count,
        )
        session.study_plan = plan
        await session_service.update_session(session)

    return StudyPlanResponse(
        session_id=session_id,
        ability_score=session.ability_score,
        total_questions=len(session.responses),
        correct_answers=correct_count,
        accuracy=round(correct_count / len(session.responses), 2) if session.responses else 0,
        weak_topics=performance["weak_topics"],
        study_plan=session.study_plan,
    )
