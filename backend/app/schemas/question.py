from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.models.question import Difficulty, QuestionStatus, QuestionType


class QuestionOptionCreate(BaseModel):
    content: str = Field(min_length=1)
    is_correct: bool = False
    order: int = 0


class QuestionOptionResponse(BaseModel):
    id: str
    content: str
    is_correct: bool
    order: int

    model_config = {"from_attributes": True}


class QuestionCreate(BaseModel):
    content: str = Field(min_length=1)
    type: QuestionType
    difficulty: Difficulty
    knowledge_point_id: str
    correct_answer: str = ""  # bắt buộc với SHORT_ANSWER / NUMERICAL
    explanation: str = ""
    solution: str = ""
    source: str = ""
    options: list[QuestionOptionCreate] = []  # bắt buộc với SINGLE_CHOICE / MULTIPLE_CHOICE / TRUE_FALSE

    @model_validator(mode="after")
    def validate_business_rules(self) -> "QuestionCreate":
        # Layer 2 (rule-based validation) tối thiểu — áp dụng ngay khi tạo thủ công,
        # không chỉ dành riêng cho câu hỏi AI sinh ra (mục XLI của tài liệu gốc).
        needs_options = self.type in (
            QuestionType.SINGLE_CHOICE,
            QuestionType.MULTIPLE_CHOICE,
            QuestionType.TRUE_FALSE,
        )
        if needs_options:
            if len(self.options) < 2:
                raise ValueError("Câu hỏi trắc nghiệm cần tối thiểu 2 lựa chọn")
            correct_count = sum(1 for o in self.options if o.is_correct)
            if correct_count == 0:
                raise ValueError("Không có đáp án đúng — câu hỏi không hợp lệ")
            if self.type == QuestionType.SINGLE_CHOICE and correct_count > 1:
                raise ValueError("SINGLE_CHOICE chỉ được có đúng 1 đáp án đúng, tìm thấy nhiều hơn 1")
        else:
            if not self.correct_answer.strip():
                raise ValueError("SHORT_ANSWER/NUMERICAL cần trường correct_answer")
        return self


class QuestionUpdateStatus(BaseModel):
    status: QuestionStatus


class QuestionResponse(BaseModel):
    id: str
    content: str
    type: QuestionType
    difficulty: Difficulty
    status: QuestionStatus
    knowledge_point_id: str
    correct_answer: str
    explanation: str
    solution: str
    source: str
    created_by: Optional[str]
    options: list[QuestionOptionResponse]

    model_config = {"from_attributes": True}


class QuestionSearchParams(BaseModel):
    knowledge_point_id: Optional[str] = None
    type: Optional[QuestionType] = None
    difficulty: Optional[Difficulty] = None
    status: Optional[QuestionStatus] = None
    keyword: Optional[str] = None
