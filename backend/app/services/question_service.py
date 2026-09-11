from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.question import Question, QuestionStatus
from app.models.role import RoleName
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import QuestionCreate, QuestionSearchParams


class QuestionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = QuestionRepository(db)

    def create_question(self, data: QuestionCreate, created_by: str) -> Question:
        if not self.repo.knowledge_point_exists(data.knowledge_point_id):
            raise NotFoundError(code="KNOWLEDGE_POINT_NOT_FOUND", message="Knowledge point không tồn tại")

        options = [{"content": o.content, "is_correct": o.is_correct, "order": o.order} for o in data.options]
        return self.repo.create(
            content=data.content,
            type=data.type,
            difficulty=data.difficulty,
            knowledge_point_id=data.knowledge_point_id,
            correct_answer=data.correct_answer,
            explanation=data.explanation,
            solution=data.solution,
            source=data.source,
            created_by=created_by,
            options=options,
            status=QuestionStatus.DRAFT,
        )

    def get_question(self, question_id: str, requester_role: RoleName) -> Question:
        question = self.repo.get_by_id(question_id)
        if question is None:
            raise NotFoundError(code="QUESTION_NOT_FOUND", message="Question not found")
        if requester_role == RoleName.STUDENT and question.status != QuestionStatus.PUBLISHED:
            # Học sinh không được xem câu hỏi chưa publish (draft/pending review/AI chưa duyệt).
            raise NotFoundError(code="QUESTION_NOT_FOUND", message="Question not found")
        return question

    def update_status(self, question_id: str, new_status: QuestionStatus, requester_role: RoleName) -> Question:
        if requester_role == RoleName.STUDENT:
            raise ForbiddenError(code="ROLE_NOT_ALLOWED", message="Học sinh không có quyền duyệt câu hỏi")
        question = self.repo.get_by_id(question_id)
        if question is None:
            raise NotFoundError(code="QUESTION_NOT_FOUND", message="Question not found")
        return self.repo.update_status(question, new_status)

    def search(self, params: QuestionSearchParams, requester_role: RoleName) -> list[Question]:
        status = params.status
        if requester_role == RoleName.STUDENT:
            # Học sinh chỉ tìm được câu hỏi đã PUBLISHED, không cho ghi đè bằng status khác.
            status = QuestionStatus.PUBLISHED
        return self.repo.search(
            knowledge_point_id=params.knowledge_point_id,
            type=params.type,
            difficulty=params.difficulty,
            status=status,
            keyword=params.keyword,
        )
