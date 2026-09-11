from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ExamCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    duration_minutes: int = Field(gt=0, le=300)


class ExamQuestionAdd(BaseModel):
    question_id: str
    order: int = 0
    points: float = Field(default=1.0, gt=0)


class ExamQuestionResponse(BaseModel):
    id: str
    question_id: str
    order: int
    points: float

    model_config = {"from_attributes": True}


class ExamResponse(BaseModel):
    id: str
    title: str
    description: str
    duration_minutes: int
    status: str
    created_by: Optional[str]
    exam_questions: list[ExamQuestionResponse]

    model_config = {"from_attributes": True}


class ExamListItem(BaseModel):
    id: str
    title: str
    duration_minutes: int
    status: str

    model_config = {"from_attributes": True}


# ---- Attempt / Answer ----


class AttemptQuestionView(BaseModel):
    """Câu hỏi hiển thị cho học sinh khi làm bài — KHÔNG lộ đáp án đúng."""

    question_id: str
    content: str
    type: str
    points: float
    options: list[dict]  # [{id, content, order}] — không có is_correct


class AttemptStartResponse(BaseModel):
    attempt_id: str
    exam_id: str
    status: str
    started_at: datetime
    duration_minutes: int
    questions: list[AttemptQuestionView]


class AnswerSubmit(BaseModel):
    question_id: str
    selected_option_ids: list[str] = []
    answer_text: str = ""

    @model_validator(mode="after")
    def at_least_one_provided(self) -> "AnswerSubmit":
        return self


class AttemptSubmitRequest(BaseModel):
    answers: list[AnswerSubmit]


class AnswerResultView(BaseModel):
    question_id: str
    is_correct: bool
    points_earned: float
    points_possible: float
    correct_option_ids: list[str] = []
    correct_answer: str = ""
    explanation: str = ""


class AttemptResultResponse(BaseModel):
    attempt_id: str
    exam_id: str
    status: str
    score: Optional[float]
    max_score: float
    submitted_at: Optional[datetime]
    answers: list[AnswerResultView]
