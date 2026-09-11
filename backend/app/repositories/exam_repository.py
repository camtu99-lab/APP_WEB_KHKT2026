from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.exam import Answer, Attempt, AttemptStatus, Exam, ExamQuestion, ExamStatus
from app.models.question import Question


class ExamRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_exam(self, *, title: str, description: str, duration_minutes: int, created_by: str) -> Exam:
        exam = Exam(title=title, description=description, duration_minutes=duration_minutes, created_by=created_by)
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def get_exam(self, exam_id: str) -> Optional[Exam]:
        stmt = (
            select(Exam)
            .options(
                selectinload(Exam.exam_questions)
                .selectinload(ExamQuestion.question)
                .selectinload(Question.options)
            )
            .where(Exam.id == exam_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_exams(self, *, only_published: bool) -> list[Exam]:
        stmt = select(Exam)
        if only_published:
            stmt = stmt.where(Exam.status == ExamStatus.PUBLISHED)
        return list(self.db.execute(stmt).scalars().all())

    def add_question(self, exam: Exam, *, question_id: str, order: int, points: float) -> ExamQuestion:
        eq = ExamQuestion(exam_id=exam.id, question_id=question_id, order=order, points=points)
        self.db.add(eq)
        self.db.commit()
        self.db.refresh(eq)
        return eq

    def publish_exam(self, exam: Exam) -> Exam:
        exam.status = ExamStatus.PUBLISHED
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def get_question(self, question_id: str) -> Optional[Question]:
        stmt = select(Question).options(selectinload(Question.options)).where(Question.id == question_id)
        return self.db.execute(stmt).scalar_one_or_none()

    # Attempt
    def create_attempt(self, *, exam_id: str, student_id: str, started_at: datetime) -> Attempt:
        attempt = Attempt(exam_id=exam_id, student_id=student_id, started_at=started_at)
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def get_attempt(self, attempt_id: str) -> Optional[Attempt]:
        stmt = select(Attempt).options(selectinload(Attempt.answers)).where(Attempt.id == attempt_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def save_answer(
        self,
        *,
        attempt_id: str,
        question_id: str,
        selected_option_ids_json: str,
        answer_text: str,
        is_correct: bool,
        points_earned: float,
    ) -> Answer:
        answer = Answer(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_option_ids=selected_option_ids_json,
            answer_text=answer_text,
            is_correct=is_correct,
            points_earned=points_earned,
        )
        self.db.add(answer)
        return answer

    def finalize_attempt(self, attempt: Attempt, *, score: float, submitted_at: datetime) -> Attempt:
        attempt.status = AttemptStatus.SUBMITTED
        attempt.score = score
        attempt.submitted_at = submitted_at
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt
