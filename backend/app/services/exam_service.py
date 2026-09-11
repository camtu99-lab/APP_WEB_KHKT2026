import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.exam import AttemptStatus, Exam, ExamStatus
from app.models.question import QuestionStatus, QuestionType
from app.repositories.exam_repository import ExamRepository
from app.schemas.exam import (
    AnswerResultView,
    AnswerSubmit,
    AttemptQuestionView,
    AttemptResultResponse,
    AttemptStartResponse,
    ExamCreate,
    ExamQuestionAdd,
)

CHOICE_TYPES = {QuestionType.SINGLE_CHOICE, QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE}


class ExamService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ExamRepository(db)

    def create_exam(self, data: ExamCreate, created_by: str) -> Exam:
        return self.repo.create_exam(
            title=data.title, description=data.description, duration_minutes=data.duration_minutes,
            created_by=created_by,
        )

    def add_question(self, exam_id: str, data: ExamQuestionAdd) -> Exam:
        exam = self.repo.get_exam(exam_id)
        if exam is None:
            raise NotFoundError(code="EXAM_NOT_FOUND", message="Đề thi không tồn tại")
        if exam.status != ExamStatus.DRAFT:
            raise ConflictError(code="EXAM_NOT_EDITABLE", message="Chỉ có thể thêm câu hỏi khi đề còn ở trạng thái DRAFT")

        question = self.repo.get_question(data.question_id)
        if question is None:
            raise NotFoundError(code="QUESTION_NOT_FOUND", message="Câu hỏi không tồn tại")
        if question.status != QuestionStatus.PUBLISHED:
            raise ConflictError(
                code="QUESTION_NOT_PUBLISHED", message="Chỉ được thêm câu hỏi đã PUBLISHED vào đề thi"
            )

        self.repo.add_question(exam, question_id=data.question_id, order=data.order, points=data.points)
        return self.repo.get_exam(exam_id)

    def publish_exam(self, exam_id: str) -> Exam:
        exam = self.repo.get_exam(exam_id)
        if exam is None:
            raise NotFoundError(code="EXAM_NOT_FOUND", message="Đề thi không tồn tại")
        if not exam.exam_questions:
            raise ConflictError(code="EXAM_EMPTY", message="Không thể publish đề thi chưa có câu hỏi nào")
        return self.repo.publish_exam(exam)

    def get_exam(self, exam_id: str) -> Exam:
        exam = self.repo.get_exam(exam_id)
        if exam is None:
            raise NotFoundError(code="EXAM_NOT_FOUND", message="Đề thi không tồn tại")
        return exam

    def list_exams(self, *, is_student: bool) -> list[Exam]:
        return self.repo.list_exams(only_published=is_student)

    def start_attempt(self, exam_id: str, student_id: str) -> AttemptStartResponse:
        exam = self.repo.get_exam(exam_id)
        if exam is None:
            raise NotFoundError(code="EXAM_NOT_FOUND", message="Đề thi không tồn tại")
        if exam.status != ExamStatus.PUBLISHED:
            raise ConflictError(code="EXAM_NOT_PUBLISHED", message="Đề thi chưa được publish")

        started_at = datetime.now(timezone.utc)
        attempt = self.repo.create_attempt(exam_id=exam_id, student_id=student_id, started_at=started_at)

        questions_view = []
        for eq in exam.exam_questions:
            q = eq.question
            # KHÔNG trả is_correct cho client — chỉ trả nội dung để hiển thị.
            options = [{"id": o.id, "content": o.content, "order": o.order} for o in q.options]
            questions_view.append(
                AttemptQuestionView(
                    question_id=q.id, content=q.content, type=q.type.value, points=eq.points, options=options
                )
            )

        return AttemptStartResponse(
            attempt_id=attempt.id,
            exam_id=exam.id,
            status=attempt.status.value,
            started_at=attempt.started_at,
            duration_minutes=exam.duration_minutes,
            questions=questions_view,
        )

    def submit_attempt(self, attempt_id: str, student_id: str, answers: list[AnswerSubmit]) -> AttemptResultResponse:
        attempt = self.repo.get_attempt(attempt_id)
        if attempt is None:
            raise NotFoundError(code="ATTEMPT_NOT_FOUND", message="Attempt không tồn tại")
        if attempt.student_id != student_id:
            raise ForbiddenError(code="NOT_YOUR_ATTEMPT", message="Bạn không có quyền nộp bài này")
        if attempt.status == AttemptStatus.SUBMITTED:
            raise ConflictError(code="ATTEMPT_ALREADY_SUBMITTED", message="Bài thi này đã được nộp trước đó")

        exam = self.repo.get_exam(attempt.exam_id)

        total_score = 0.0
        max_score = sum(eq.points for eq in exam.exam_questions)
        result_views: list[AnswerResultView] = []

        answers_by_question = {a.question_id: a for a in answers}

        for eq in exam.exam_questions:
            question = eq.question
            submitted = answers_by_question.get(question.id)
            selected_ids = submitted.selected_option_ids if submitted else []
            answer_text = submitted.answer_text if submitted else ""

            is_correct, points_earned = self._grade_single(question, eq.points, selected_ids, answer_text)
            total_score += points_earned

            self.repo.save_answer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_option_ids_json=json.dumps(selected_ids),
                answer_text=answer_text,
                is_correct=is_correct,
                points_earned=points_earned,
            )

            result_views.append(
                AnswerResultView(
                    question_id=question.id,
                    is_correct=is_correct,
                    points_earned=points_earned,
                    points_possible=eq.points,
                    correct_option_ids=[o.id for o in question.options if o.is_correct],
                    correct_answer=question.correct_answer,
                    explanation=question.explanation,
                )
            )

        submitted_at = datetime.now(timezone.utc)
        attempt = self.repo.finalize_attempt(attempt, score=total_score, submitted_at=submitted_at)

        return AttemptResultResponse(
            attempt_id=attempt.id,
            exam_id=exam.id,
            status=attempt.status.value,
            score=attempt.score,
            max_score=max_score,
            submitted_at=attempt.submitted_at,
            answers=result_views,
        )

    def get_result(self, attempt_id: str, requester_id: str, requester_is_privileged: bool) -> AttemptResultResponse:
        attempt = self.repo.get_attempt(attempt_id)
        if attempt is None:
            raise NotFoundError(code="ATTEMPT_NOT_FOUND", message="Attempt không tồn tại")
        if attempt.student_id != requester_id and not requester_is_privileged:
            raise ForbiddenError(code="NOT_YOUR_ATTEMPT", message="Bạn không có quyền xem kết quả này")
        if attempt.status != AttemptStatus.SUBMITTED:
            raise ConflictError(code="ATTEMPT_NOT_SUBMITTED", message="Bài thi chưa được nộp")

        exam = self.repo.get_exam(attempt.exam_id)
        answers_by_question = {a.question_id: a for a in attempt.answers}

        max_score = sum(eq.points for eq in exam.exam_questions)
        result_views = []
        for eq in exam.exam_questions:
            question = eq.question
            ans = answers_by_question.get(question.id)
            result_views.append(
                AnswerResultView(
                    question_id=question.id,
                    is_correct=ans.is_correct if ans else False,
                    points_earned=ans.points_earned if ans else 0.0,
                    points_possible=eq.points,
                    correct_option_ids=[o.id for o in question.options if o.is_correct],
                    correct_answer=question.correct_answer,
                    explanation=question.explanation,
                )
            )

        return AttemptResultResponse(
            attempt_id=attempt.id,
            exam_id=exam.id,
            status=attempt.status.value,
            score=attempt.score,
            max_score=max_score,
            submitted_at=attempt.submitted_at,
            answers=result_views,
        )

    @staticmethod
    def _grade_single(question, points: float, selected_ids: list[str], answer_text: str) -> tuple[bool, float]:
        """
        Chấm điểm 1 câu — LUÔN dựa vào dữ liệu đáp án đúng lưu trong DB (server-side),
        không bao giờ tin dữ liệu "đúng/sai" do client tự gửi lên.
        """
        if question.type in CHOICE_TYPES:
            correct_ids = {o.id for o in question.options if o.is_correct}
            submitted_ids = set(selected_ids)
            is_correct = submitted_ids == correct_ids and len(submitted_ids) > 0
            return is_correct, (points if is_correct else 0.0)
        else:
            # SHORT_ANSWER / NUMERICAL — so khớp chuỗi đã chuẩn hóa (chưa hỗ trợ dung sai số học, xem Known issues).
            is_correct = answer_text.strip().lower() == question.correct_answer.strip().lower()
            return is_correct, (points if is_correct else 0.0)
