from tests.helpers import auth_header, register_and_login


def _setup_published_question(client, teacher_token: str) -> str:
    h = auth_header(teacher_token)
    subject = client.post("/api/v1/subjects", json={"name": "Hóa", "description": ""}, headers=h).json()
    grade = client.post("/api/v1/grades", json={"subject_id": subject["id"], "name": "Lớp 12"}, headers=h).json()
    chapter = client.post(
        "/api/v1/chapters", json={"grade_id": grade["id"], "name": "Ester", "order": 1}, headers=h
    ).json()
    lesson = client.post(
        "/api/v1/lessons", json={"chapter_id": chapter["id"], "name": "Bài 1", "content": "", "order": 1}, headers=h
    ).json()
    kp = client.post(
        "/api/v1/knowledge-points", json={"lesson_id": lesson["id"], "name": "Ester hóa"}, headers=h
    ).json()

    q = client.post(
        "/api/v1/questions",
        json={
            "content": "1 + 1 = ?",
            "type": "SINGLE_CHOICE",
            "difficulty": "RECOGNITION",
            "knowledge_point_id": kp["id"],
            "options": [
                {"content": "2", "is_correct": True, "order": 1},
                {"content": "3", "is_correct": False, "order": 2},
            ],
        },
        headers=h,
    ).json()
    client.patch(f"/api/v1/questions/{q['id']}/status", json={"status": "PUBLISHED"}, headers=h)
    return q["id"]


def _create_published_exam(client, teacher_token: str, question_id: str) -> str:
    h = auth_header(teacher_token)
    exam = client.post(
        "/api/v1/exams", json={"title": "Đề kiểm tra 15 phút", "duration_minutes": 15}, headers=h
    ).json()
    client.post(
        f"/api/v1/exams/{exam['id']}/questions", json={"question_id": question_id, "order": 1, "points": 10}, headers=h
    )
    client.post(f"/api/v1/exams/{exam['id']}/publish", headers=h)
    return exam["id"]


def test_cannot_add_unpublished_question_to_exam(client):
    teacher_token = register_and_login(client, "t_exam1@chemgenie.vn", role="TEACHER")
    h = auth_header(teacher_token)
    subject = client.post("/api/v1/subjects", json={"name": "Hóa2", "description": ""}, headers=h).json()
    grade = client.post("/api/v1/grades", json={"subject_id": subject["id"], "name": "Lớp 12"}, headers=h).json()
    chapter = client.post(
        "/api/v1/chapters", json={"grade_id": grade["id"], "name": "C1", "order": 1}, headers=h
    ).json()
    lesson = client.post(
        "/api/v1/lessons", json={"chapter_id": chapter["id"], "name": "L1", "content": "", "order": 1}, headers=h
    ).json()
    kp = client.post("/api/v1/knowledge-points", json={"lesson_id": lesson["id"], "name": "KP1"}, headers=h).json()
    q = client.post(
        "/api/v1/questions",
        json={
            "content": "Câu chưa publish",
            "type": "SHORT_ANSWER",
            "difficulty": "APPLICATION",
            "knowledge_point_id": kp["id"],
            "correct_answer": "x",
        },
        headers=h,
    ).json()  # vẫn ở DRAFT, chưa publish

    exam = client.post("/api/v1/exams", json={"title": "Đề test", "duration_minutes": 10}, headers=h).json()
    r = client.post(
        f"/api/v1/exams/{exam['id']}/questions", json={"question_id": q["id"], "order": 1, "points": 5}, headers=h
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "QUESTION_NOT_PUBLISHED"


def test_cannot_publish_empty_exam(client):
    teacher_token = register_and_login(client, "t_exam2@chemgenie.vn", role="TEACHER")
    h = auth_header(teacher_token)
    exam = client.post("/api/v1/exams", json={"title": "Đề rỗng", "duration_minutes": 10}, headers=h).json()
    r = client.post(f"/api/v1/exams/{exam['id']}/publish", headers=h)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "EXAM_EMPTY"


def test_student_cannot_see_draft_exam_in_list(client):
    teacher_token = register_and_login(client, "t_exam3@chemgenie.vn", role="TEACHER")
    client.post("/api/v1/exams", json={"title": "Đề draft", "duration_minutes": 10}, headers=auth_header(teacher_token))

    student_token = register_and_login(client, "s_exam3@chemgenie.vn", role="STUDENT")
    r = client.get("/api/v1/exams", headers=auth_header(student_token))
    assert r.status_code == 200
    assert all(item["status"] == "PUBLISHED" for item in r.json())


def test_full_exam_flow_correct_answer(client):
    teacher_token = register_and_login(client, "t_exam4@chemgenie.vn", role="TEACHER")
    question_id = _setup_published_question(client, teacher_token)
    exam_id = _create_published_exam(client, teacher_token, question_id)

    student_token = register_and_login(client, "s_exam4@chemgenie.vn", role="STUDENT")
    h = auth_header(student_token)

    start = client.post(f"/api/v1/exams/{exam_id}/start", headers=h)
    assert start.status_code == 201
    body = start.json()
    assert len(body["questions"]) == 1
    # Client KHÔNG nhận được is_correct trong option
    assert "is_correct" not in body["questions"][0]["options"][0]

    correct_option_id = next(
        o["id"] for o in body["questions"][0]["options"] if o["content"] == "2"
    )

    submit = client.post(
        f"/api/v1/attempts/{body['attempt_id']}/submit",
        json={"answers": [{"question_id": question_id, "selected_option_ids": [correct_option_id]}]},
        headers=h,
    )
    assert submit.status_code == 200
    result = submit.json()
    assert result["score"] == 10
    assert result["max_score"] == 10
    assert result["answers"][0]["is_correct"] is True


def test_full_exam_flow_wrong_answer_scores_zero(client):
    teacher_token = register_and_login(client, "t_exam5@chemgenie.vn", role="TEACHER")
    question_id = _setup_published_question(client, teacher_token)
    exam_id = _create_published_exam(client, teacher_token, question_id)

    student_token = register_and_login(client, "s_exam5@chemgenie.vn", role="STUDENT")
    h = auth_header(student_token)
    start = client.post(f"/api/v1/exams/{exam_id}/start", headers=h).json()
    wrong_option_id = next(o["id"] for o in start["questions"][0]["options"] if o["content"] == "3")

    submit = client.post(
        f"/api/v1/attempts/{start['attempt_id']}/submit",
        json={"answers": [{"question_id": question_id, "selected_option_ids": [wrong_option_id]}]},
        headers=h,
    ).json()
    assert submit["score"] == 0
    assert submit["answers"][0]["is_correct"] is False


def test_client_cannot_fake_is_correct_when_submitting(client):
    """
    Chống gian lận: client gửi field lạ (is_correct=True) trong payload đáp án sai
    -> server vẫn phải chấm dựa vào DB, không tin field từ client.
    """
    teacher_token = register_and_login(client, "t_exam6@chemgenie.vn", role="TEACHER")
    question_id = _setup_published_question(client, teacher_token)
    exam_id = _create_published_exam(client, teacher_token, question_id)

    student_token = register_and_login(client, "s_exam6@chemgenie.vn", role="STUDENT")
    h = auth_header(student_token)
    start = client.post(f"/api/v1/exams/{exam_id}/start", headers=h).json()
    wrong_option_id = next(o["id"] for o in start["questions"][0]["options"] if o["content"] == "3")

    submit = client.post(
        f"/api/v1/attempts/{start['attempt_id']}/submit",
        json={
            "answers": [
                {
                    "question_id": question_id,
                    "selected_option_ids": [wrong_option_id],
                    "is_correct": True,  # field lạ, schema không nhận -> bị Pydantic bỏ qua
                }
            ]
        },
        headers=h,
    ).json()
    assert submit["score"] == 0
    assert submit["answers"][0]["is_correct"] is False


def test_cannot_submit_same_attempt_twice(client):
    teacher_token = register_and_login(client, "t_exam7@chemgenie.vn", role="TEACHER")
    question_id = _setup_published_question(client, teacher_token)
    exam_id = _create_published_exam(client, teacher_token, question_id)

    student_token = register_and_login(client, "s_exam7@chemgenie.vn", role="STUDENT")
    h = auth_header(student_token)
    start = client.post(f"/api/v1/exams/{exam_id}/start", headers=h).json()
    correct_id = next(o["id"] for o in start["questions"][0]["options"] if o["content"] == "2")
    payload = {"answers": [{"question_id": question_id, "selected_option_ids": [correct_id]}]}

    r1 = client.post(f"/api/v1/attempts/{start['attempt_id']}/submit", json=payload, headers=h)
    assert r1.status_code == 200
    r2 = client.post(f"/api/v1/attempts/{start['attempt_id']}/submit", json=payload, headers=h)
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "ATTEMPT_ALREADY_SUBMITTED"


def test_other_student_cannot_submit_or_view_someone_elses_attempt(client):
    teacher_token = register_and_login(client, "t_exam8@chemgenie.vn", role="TEACHER")
    question_id = _setup_published_question(client, teacher_token)
    exam_id = _create_published_exam(client, teacher_token, question_id)

    owner_token = register_and_login(client, "s_owner8@chemgenie.vn", role="STUDENT")
    intruder_token = register_and_login(client, "s_intruder8@chemgenie.vn", role="STUDENT")

    start = client.post(f"/api/v1/exams/{exam_id}/start", headers=auth_header(owner_token)).json()

    r_submit = client.post(
        f"/api/v1/attempts/{start['attempt_id']}/submit",
        json={"answers": []},
        headers=auth_header(intruder_token),
    )
    assert r_submit.status_code == 403
    assert r_submit.json()["error"]["code"] == "NOT_YOUR_ATTEMPT"


def test_cannot_start_attempt_on_unpublished_exam(client):
    teacher_token = register_and_login(client, "t_exam9@chemgenie.vn", role="TEACHER")
    exam = client.post(
        "/api/v1/exams", json={"title": "Draft only", "duration_minutes": 10}, headers=auth_header(teacher_token)
    ).json()

    student_token = register_and_login(client, "s_exam9@chemgenie.vn", role="STUDENT")
    r = client.post(f"/api/v1/exams/{exam['id']}/start", headers=auth_header(student_token))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "EXAM_NOT_PUBLISHED"


def test_get_result_before_submit_rejected(client):
    teacher_token = register_and_login(client, "t_exam10@chemgenie.vn", role="TEACHER")
    question_id = _setup_published_question(client, teacher_token)
    exam_id = _create_published_exam(client, teacher_token, question_id)

    student_token = register_and_login(client, "s_exam10@chemgenie.vn", role="STUDENT")
    start = client.post(f"/api/v1/exams/{exam_id}/start", headers=auth_header(student_token)).json()

    r = client.get(f"/api/v1/attempts/{start['attempt_id']}/result", headers=auth_header(student_token))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "ATTEMPT_NOT_SUBMITTED"
