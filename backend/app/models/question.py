import enum
import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin


def _uuid_default():
    return str(uuid.uuid4())


class QuestionType(str, enum.Enum):
    SINGLE_CHOICE = "SINGLE_CHOICE"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    TRUE_FALSE = "TRUE_FALSE"
    SHORT_ANSWER = "SHORT_ANSWER"
    NUMERICAL = "NUMERICAL"


class Difficulty(str, enum.Enum):
    RECOGNITION = "RECOGNITION"
    COMPREHENSION = "COMPREHENSION"
    APPLICATION = "APPLICATION"
    ADVANCED_APPLICATION = "ADVANCED_APPLICATION"


class QuestionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    AI_GENERATED = "AI_GENERATED"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_default)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[QuestionType] = mapped_column(SAEnum(QuestionType, name="question_type"), nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(SAEnum(Difficulty, name="question_difficulty"), nullable=False)
    status: Mapped[QuestionStatus] = mapped_column(
        SAEnum(QuestionStatus, name="question_status"), default=QuestionStatus.DRAFT, nullable=False
    )

    knowledge_point_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_points.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    correct_answer: Mapped[str] = mapped_column(Text, default="")  # dùng cho SHORT_ANSWER / NUMERICAL
    explanation: Mapped[str] = mapped_column(Text, default="")
    solution: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(255), default="")

    created_by: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    knowledge_point: Mapped["KnowledgePoint"] = relationship()  # noqa: F821
    options: Mapped[list["QuestionOption"]] = relationship(
        back_populates="question", cascade="all, delete-orphan", order_by="QuestionOption.order"
    )


class QuestionOption(Base, TimestampMixin):
    __tablename__ = "question_options"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_default)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(default=False, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

    question: Mapped["Question"] = relationship(back_populates="options")
