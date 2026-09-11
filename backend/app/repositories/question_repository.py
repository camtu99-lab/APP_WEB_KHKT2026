from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.question import Difficulty, Question, QuestionOption, QuestionStatus, QuestionType


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        content: str,
        type: QuestionType,
        difficulty: Difficulty,
        knowledge_point_id: str,
        correct_answer: str,
        explanation: str,
        solution: str,
        source: str,
        created_by: Optional[str],
        options: list[dict],
        status: QuestionStatus = QuestionStatus.DRAFT,
    ) -> Question:
        question = Question(
            content=content,
            type=type,
            difficulty=difficulty,
            knowledge_point_id=knowledge_point_id,
            correct_answer=correct_answer,
            explanation=explanation,
            solution=solution,
            source=source,
            created_by=created_by,
            status=status,
        )
        for opt in options:
            question.options.append(
                QuestionOption(content=opt["content"], is_correct=opt["is_correct"], order=opt["order"])
            )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def get_by_id(self, question_id: str) -> Optional[Question]:
        stmt = (
            select(Question)
            .options(selectinload(Question.options))
            .where(Question.id == question_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def update_status(self, question: Question, status: QuestionStatus) -> Question:
        question.status = status
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def search(
        self,
        *,
        knowledge_point_id: Optional[str] = None,
        type: Optional[QuestionType] = None,
        difficulty: Optional[Difficulty] = None,
        status: Optional[QuestionStatus] = None,
        keyword: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Question]:
        stmt = select(Question).options(selectinload(Question.options))
        if knowledge_point_id:
            stmt = stmt.where(Question.knowledge_point_id == knowledge_point_id)
        if type:
            stmt = stmt.where(Question.type == type)
        if difficulty:
            stmt = stmt.where(Question.difficulty == difficulty)
        if status:
            stmt = stmt.where(Question.status == status)
        if keyword:
            stmt = stmt.where(Question.content.ilike(f"%{keyword}%"))
        stmt = stmt.order_by(Question.created_at.desc()).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def knowledge_point_exists(self, knowledge_point_id: str) -> bool:
        from app.models.content import KnowledgePoint

        return self.db.get(KnowledgePoint, knowledge_point_id) is not None
