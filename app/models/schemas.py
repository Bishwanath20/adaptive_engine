from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Topic(str, Enum):
    ALGEBRA = "Algebra"
    GEOMETRY = "Geometry"
    ARITHMETIC = "Arithmetic"
    VOCABULARY = "Vocabulary"
    READING_COMPREHENSION = "Reading Comprehension"
    STATISTICS = "Statistics"


class Question(BaseModel):
    question_id: str
    text: str
    options: Dict[str, str]          # {"A": "...", "B": "...", ...}
    correct_answer: str              # "A", "B", "C", or "D"
    difficulty: float = Field(..., ge=0.1, le=1.0)
    topic: Topic
    tags: List[str]
    discrimination: float = Field(default=1.0)   # IRT parameter (a)
    guessing: float = Field(default=0.25)        # IRT parameter (c)


class QuestionInDB(Question):
    id: Optional[str] = None


class ResponseRecord(BaseModel):
    question_id: str
    topic: str
    difficulty: float
    is_correct: bool
    ability_before: float
    ability_after: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserSession(BaseModel):
    session_id: str
    ability_score: float = 0.5          # theta (θ) — starts at baseline
    questions_asked: List[str] = []     # list of question_ids
    responses: List[ResponseRecord] = []
    is_complete: bool = False
    study_plan: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    max_questions: int = 10


# Request / Response schemas

class StartSessionRequest(BaseModel):
    max_questions: int = Field(default=10, ge=5, le=20)


class StartSessionResponse(BaseModel):
    session_id: str
    message: str


class NextQuestionResponse(BaseModel):
    session_id: str
    question_number: int
    total_questions: int
    question_id: str
    text: str
    options: Dict[str, str]
    topic: str
    difficulty: float


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    selected_answer: str


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    ability_score: float
    questions_remaining: int
    session_complete: bool
    message: str


class StudyPlanResponse(BaseModel):
    session_id: str
    ability_score: float
    total_questions: int
    correct_answers: int
    accuracy: float
    weak_topics: List[str]
    study_plan: str
