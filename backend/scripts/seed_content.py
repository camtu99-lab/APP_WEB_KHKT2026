"""
Seed dữ liệu DEMO cho Content + Question Bank.
Đây là DEMO DATA — không phải dữ liệu thực tế, chỉ để hệ thống chạy được ngay.
Chạy: python -m scripts.seed_content
(Yêu cầu đã chạy scripts.seed_roles và có sẵn user teacher/admin trong DB)
"""
from app.db.session import SessionLocal
from app.models.content import Chapter, Grade, KnowledgePoint, Lesson, Subject
from app.models.question import Difficulty, Question, QuestionOption, QuestionStatus, QuestionType


def seed_content() -> None:
    db = SessionLocal()
    try:
        if db.query(Subject).filter(Subject.name == "Hóa học (DEMO)").first():
            print("Demo content đã tồn tại, bỏ qua seed.")
            return

        subject = Subject(name="Hóa học (DEMO)", description="Môn học demo cho CHEMGENIE")
        db.add(subject)
        db.flush()

        grade12 = Grade(subject_id=subject.id, name="Lớp 12")
        db.add(grade12)
        db.flush()

        chapter_ester = Chapter(grade_id=grade12.id, name="Chương: Ester - Lipit (DEMO)", order=1)
        db.add(chapter_ester)
        db.flush()

        lesson1 = Lesson(
            chapter_id=chapter_ester.id,
            name="Bài 1: Ester (DEMO)",
            content="Nội dung demo — sẽ thay bằng nội dung thật.",
            order=1,
        )
        db.add(lesson1)
        db.flush()

        kp1 = KnowledgePoint(lesson_id=lesson1.id, name="Phản ứng este hóa (DEMO)")
        db.add(kp1)
        db.flush()

        q1 = Question(
            content="[DEMO] Công thức tổng quát của este no, đơn chức, mạch hở là gì?",
            type=QuestionType.SINGLE_CHOICE,
            difficulty=Difficulty.RECOGNITION,
            status=QuestionStatus.PUBLISHED,
            knowledge_point_id=kp1.id,
            explanation="Đây là câu hỏi DEMO, cần giáo viên rà soát trước khi dùng thật.",
            source="DEMO",
        )
        q1.options = [
            QuestionOption(content="CnH2nO2 (n≥2)", is_correct=True, order=1),
            QuestionOption(content="CnH2nO", is_correct=False, order=2),
            QuestionOption(content="CnH2n+2O2", is_correct=False, order=3),
            QuestionOption(content="CnH2n-2O2", is_correct=False, order=4),
        ]
        db.add(q1)
        db.commit()
        print("Seed content DEMO thành công.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_content()
