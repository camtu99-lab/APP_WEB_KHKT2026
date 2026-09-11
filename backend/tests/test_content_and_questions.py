from tests.helpers import auth_header, register_and_login


def _build_full_hierarchy(client, teacher_token: str) -> str:
    """Tạo Subject -> Grade -> Chapter -> Lesson -> KnowledgePoint, trả về knowledge_point_id."""
    h = auth_header(teacher_token)

    subject = client.post("/api/v1/subjects", json={"name": "Hóa học", "description": ""}, headers=h).json()
    grade = client.post(
        "/api/v1/grades", json={"subject_id": subject["id"], "name": "Lớp 12"}, headers=h
    ).json()
    chapter = client.post(
        "/api/v1/chapters", json={"grade_id": grade["id"], "name": "Ester - Lipit", "order": 1}, headers=h
    ).json()
    lesson = client.post(
        "/api/v1/lessons",
        json={"chapter_id": chapter["id"], "name": "Bài 1: Ester", "content": "", "order": 1},
        headers=h,
    ).json()
    kp = client.post(
        "/api/v1/knowledge-points", json={"lesson_id": lesson["id"], "name": "Phản ứng este hóa"}, headers=h
    ).json()
    return kp["id"]


def test_content_hierarchy_creation_and_fk_validation(client):
    teacher_token = register_and_login(client, "teacher1@chemgenie.vn", role="TEACHER")
    kp_id = _build_full_hierarchy(client, teacher_token)
    assert kp_id

    # Tạo grade với subject_id không tồn tại -> phải bị từ chối rõ ràng, không lỗi 500
    r = client.post(
        "/api/v1/grades",
        json={"subject_id": "not-exist-id", "name": "Lớp 10"},
        headers=auth_header(teacher_token),
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "SUBJECT_NOT_FOUND"


def test_content_write_requires_teacher_or_admin(client):
    student_token = register_and_login(client, "student_content@chemgenie.vn", role="STUDENT")
    r = client.post(
        "/api/v1/subjects", json={"name": "Vật lý", "description": ""}, headers=auth_header(student_token)
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "ROLE_NOT_ALLOWED"


def test_student_can_read_content(client):
    teacher_token = register_and_login(client, "teacher2@chemgenie.vn", role="TEACHER")
    _build_full_hierarchy(client, teacher_token)

    student_token = register_and_login(client, "student_read@chemgenie.vn", role="STUDENT")
    r = client.get("/api/v1/subjects", headers=auth_header(student_token))
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_create_single_choice_question_success(client):
    teacher_token = register_and_login(client, "teacher3@chemgenie.vn", role="TEACHER")
    kp_id = _build_full_hierarchy(client, teacher_token)

    payload = {
        "content": "Công thức tổng quát của este no đơn chức mạch hở là gì?",
        "type": "SINGLE_CHOICE",
        "difficulty": "RECOGNITION",
        "knowledge_point_id": kp_id,
        "options": [
            {"content": "CnH2nO2", "is_correct": True, "order": 1},
            {"content": "CnH2nO", "is_correct": False, "order": 2},
            {"content": "CnH2n+2O2", "is_correct": False, "order": 3},
            {"content": "CnH2n-2O2", "is_correct": False, "order": 4},
        ],
    }
    r = client.post("/api/v1/questions", json=payload, headers=auth_header(teacher_token))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "DRAFT"
    assert len(body["options"]) == 4


def test_create_question_no_correct_answer_rejected(client):
    teacher_token = register_and_login(client, "teacher4@chemgenie.vn", role="TEACHER")
    kp_id = _build_full_hierarchy(client, teacher_token)

    payload = {
        "content": "Câu hỏi không có đáp án đúng",
        "type": "SINGLE_CHOICE",
        "difficulty": "RECOGNITION",
        "knowledge_point_id": kp_id,
        "options": [
            {"content": "A", "is_correct": False, "order": 1},
            {"content": "B", "is_correct": False, "order": 2},
        ],
    }
    r = client.post("/api/v1/questions", json=payload, headers=auth_header(teacher_token))
    assert r.status_code == 422  # Pydantic validation error


def test_create_question_multiple_correct_for_single_choice_rejected(client):
    teacher_token = register_and_login(client, "teacher5@chemgenie.vn", role="TEACHER")
    kp_id = _build_full_hierarchy(client, teacher_token)

    payload = {
        "content": "Câu SINGLE_CHOICE nhưng có 2 đáp án đúng",
        "type": "SINGLE_CHOICE",
        "difficulty": "RECOGNITION",
        "knowledge_point_id": kp_id,
        "options": [
            {"content": "A", "is_correct": True, "order": 1},
            {"content": "B", "is_correct": True, "order": 2},
        ],
    }
    r = client.post("/api/v1/questions", json=payload, headers=auth_header(teacher_token))
    assert r.status_code == 422


def test_create_question_invalid_knowledge_point_rejected(client):
    teacher_token = register_and_login(client, "teacher6@chemgenie.vn", role="TEACHER")
    payload = {
        "content": "Câu hỏi với knowledge_point không tồn tại",
        "type": "SHORT_ANSWER",
        "difficulty": "APPLICATION",
        "knowledge_point_id": "not-exist",
        "correct_answer": "42",
    }
    r = client.post("/api/v1/questions", json=payload, headers=auth_header(teacher_token))
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "KNOWLEDGE_POINT_NOT_FOUND"


def test_student_cannot_see_unpublished_question(client):
    teacher_token = register_and_login(client, "teacher7@chemgenie.vn", role="TEACHER")
    kp_id = _build_full_hierarchy(client, teacher_token)
    q = client.post(
        "/api/v1/questions",
        json={
            "content": "Câu hỏi chưa publish",
            "type": "SHORT_ANSWER",
            "difficulty": "APPLICATION",
            "knowledge_point_id": kp_id,
            "correct_answer": "abc",
        },
        headers=auth_header(teacher_token),
    ).json()

    student_token = register_and_login(client, "student_q@chemgenie.vn", role="STUDENT")
    r = client.get(f"/api/v1/questions/{q['id']}", headers=auth_header(student_token))
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "QUESTION_NOT_FOUND"


def test_teacher_publish_then_student_can_see_and_search(client):
    teacher_token = register_and_login(client, "teacher8@chemgenie.vn", role="TEACHER")
    kp_id = _build_full_hierarchy(client, teacher_token)
    q = client.post(
        "/api/v1/questions",
        json={
            "content": "Câu hỏi sẽ được publish",
            "type": "SHORT_ANSWER",
            "difficulty": "APPLICATION",
            "knowledge_point_id": kp_id,
            "correct_answer": "abc",
        },
        headers=auth_header(teacher_token),
    ).json()

    r_status = client.patch(
        f"/api/v1/questions/{q['id']}/status",
        json={"status": "PUBLISHED"},
        headers=auth_header(teacher_token),
    )
    assert r_status.status_code == 200
    assert r_status.json()["status"] == "PUBLISHED"

    student_token = register_and_login(client, "student_pub@chemgenie.vn", role="STUDENT")
    r_get = client.get(f"/api/v1/questions/{q['id']}", headers=auth_header(student_token))
    assert r_get.status_code == 200

    r_search = client.get("/api/v1/questions", headers=auth_header(student_token))
    assert r_search.status_code == 200
    assert any(item["id"] == q["id"] for item in r_search.json())


def test_student_cannot_update_question_status(client):
    teacher_token = register_and_login(client, "teacher9@chemgenie.vn", role="TEACHER")
    kp_id = _build_full_hierarchy(client, teacher_token)
    q = client.post(
        "/api/v1/questions",
        json={
            "content": "Câu hỏi test RBAC duyệt",
            "type": "SHORT_ANSWER",
            "difficulty": "APPLICATION",
            "knowledge_point_id": kp_id,
            "correct_answer": "abc",
        },
        headers=auth_header(teacher_token),
    ).json()

    student_token = register_and_login(client, "student_rbac2@chemgenie.vn", role="STUDENT")
    r = client.patch(
        f"/api/v1/questions/{q['id']}/status",
        json={"status": "PUBLISHED"},
        headers=auth_header(student_token),
    )
    assert r.status_code == 403
