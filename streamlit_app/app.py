"""
ChemGenie API Tester — giao diện Streamlit đầy đủ để test toàn bộ backend FastAPI:
Xác thực, Nội dung học (môn/lớp/chương/bài/kiến thức), Ngân hàng câu hỏi,
Đề thi, và Làm bài thi.

Chạy local:
    streamlit run streamlit_app/app.py

Cấu hình URL backend qua biến môi trường CHEMGENIE_API_URL, hoặc qua
st.secrets["CHEMGENIE_API_URL"] khi deploy trên Streamlit Cloud.
"""

import os
from typing import Optional

import requests
import streamlit as st


def _get_default_api_url() -> str:
    try:
        if "CHEMGENIE_API_URL" in st.secrets:
            return st.secrets["CHEMGENIE_API_URL"]
    except Exception:
        pass
    return os.environ.get("CHEMGENIE_API_URL", "http://localhost:8000")


DEFAULT_API_URL = _get_default_api_url()

st.set_page_config(page_title="ChemGenie API Tester", page_icon="🧪", layout="wide")

# ---------- Session state ----------
for key, default in {
    "access_token": None,
    "refresh_token": None,
    "user": None,
    "current_attempt": None,
    "last_result": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def api_url() -> str:
    return st.session_state.get("api_url", DEFAULT_API_URL).rstrip("/")


def auth_headers() -> dict:
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}


def current_role() -> Optional[str]:
    user = st.session_state.get("user")
    return user.get("role") if user else None


def is_teacher_or_admin() -> bool:
    return current_role() in ("TEACHER", "ADMIN")


def handle_response(resp: requests.Response, success_msg: Optional[str] = None):
    """Hiển thị kết quả gọi API. Backend trả lỗi dạng {success:false,error:{...}};
    thành công thì trả thẳng dữ liệu (không bọc), trừ /health."""
    try:
        payload = resp.json()
    except ValueError:
        if resp.status_code == 204:
            if success_msg:
                st.success(success_msg)
            return None
        st.error(f"HTTP {resp.status_code}: không parse được JSON — {resp.text[:300]}")
        return None

    if resp.status_code >= 400 or (isinstance(payload, dict) and payload.get("success") is False):
        err = payload.get("error", {}) if isinstance(payload, dict) else {}
        st.error(f"Lỗi [{err.get('code', resp.status_code)}]: {err.get('message', payload)}")
        return None

    if success_msg:
        st.success(success_msg)
    st.json(payload)
    return payload


def api_get(path: str, params: dict = None):
    return requests.get(f"{api_url()}{path}", headers=auth_headers(), params=params, timeout=15)


def api_post(path: str, json: dict):
    return requests.post(f"{api_url()}{path}", headers=auth_headers(), json=json, timeout=15)


def fetch_options(path: str, params: dict = None) -> list:
    """Gọi API GET danh sách để đổ vào selectbox; trả [] nếu lỗi/chưa đăng nhập."""
    if not st.session_state.access_token:
        return []
    try:
        r = api_get(path, params=params)
        if r.status_code == 200:
            data = r.json()
            return data if isinstance(data, list) else []
    except requests.RequestException:
        pass
    return []


def select_from(label: str, items: list, name_key: str = "name", key: str = None):
    """Selectbox chọn 1 item theo id, hiển thị theo name_key (hoặc 'title'/'content' nếu thiếu). Trả về id hoặc None."""
    if not items:
        st.caption("(Chưa có dữ liệu — tạo trước, hoặc bấm nút tải danh sách ở tab liên quan)")
        return None
    def _label(it):
        text = it.get(name_key) or it.get("title") or it.get("content") or it["id"]
        text = str(text)
        if len(text) > 60:
            text = text[:60] + "..."
        return f"{text}  ·  {it['id'][:8]}"
    labels = [_label(it) for it in items]
    idx = st.selectbox(label, range(len(items)), format_func=lambda i: labels[i], key=key)
    return items[idx]["id"]


# ---------- Sidebar ----------
with st.sidebar:
    st.title("🧪 ChemGenie")
    st.text_input("Backend API URL", value=DEFAULT_API_URL, key="api_url")

    if st.button("🔍 Kiểm tra kết nối (/health)"):
        try:
            r = requests.get(f"{api_url()}/health", timeout=10)
            handle_response(r)
        except requests.RequestException as e:
            st.error(f"Không kết nối được backend: {e}")

    st.divider()

    if st.session_state.access_token:
        st.success("Đã đăng nhập")
        if st.session_state.user:
            st.write(f"**{st.session_state.user.get('full_name')}**")
            st.caption(f"{st.session_state.user.get('email')} · {st.session_state.user.get('role')}")
        if st.button("Đăng xuất"):
            try:
                requests.post(
                    f"{api_url()}/api/v1/auth/logout",
                    json={"refresh_token": st.session_state.refresh_token},
                    timeout=10,
                )
            except requests.RequestException:
                pass
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.session_state.user = None
            st.rerun()
    else:
        st.info("Chưa đăng nhập")
        st.caption("Đăng nhập ở tab 'Xác thực' để dùng các tính năng khác.")

# ---------- Main tabs ----------
tab_auth, tab_content, tab_questions, tab_exams, tab_attempts = st.tabs(
    ["🔐 Xác thực", "📚 Nội dung học", "❓ Ngân hàng câu hỏi", "📝 Đề thi (Giáo viên)", "🎓 Làm bài thi (Học sinh)"]
)

# ============================================================
# TAB: XÁC THỰC
# ============================================================
with tab_auth:
    sub_register, sub_login, sub_me, sub_users, sub_refresh = st.tabs(
        ["Đăng ký", "Đăng nhập", "Thông tin của tôi", "Danh sách user (Admin)", "Refresh token"]
    )

    with sub_register:
        st.subheader("Đăng ký tài khoản")
        with st.form("register_form"):
            email = st.text_input("Email", key="reg_email")
            full_name = st.text_input("Họ và tên", key="reg_full_name")
            password = st.text_input("Mật khẩu (>= 8 ký tự)", type="password", key="reg_password")
            role = st.selectbox("Vai trò", ["STUDENT", "TEACHER", "ADMIN"], key="reg_role")
            submitted = st.form_submit_button("Đăng ký")
        if submitted:
            try:
                r = api_post("/api/v1/auth/register", {"email": email, "full_name": full_name, "password": password, "role": role})
                handle_response(r, success_msg="Đăng ký thành công! Chuyển sang tab Đăng nhập.")
            except requests.RequestException as e:
                st.error(f"Không kết nối được backend: {e}")

    with sub_login:
        st.subheader("Đăng nhập")
        with st.form("login_form"):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Mật khẩu", type="password", key="login_password")
            login_submitted = st.form_submit_button("Đăng nhập")
        if login_submitted:
            try:
                r = api_post("/api/v1/auth/login", {"email": login_email, "password": login_password})
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.access_token = data["access_token"]
                    st.session_state.refresh_token = data["refresh_token"]
                    me = api_get("/api/v1/users/me")
                    if me.status_code == 200:
                        st.session_state.user = me.json()
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    handle_response(r)
            except requests.RequestException as e:
                st.error(f"Không kết nối được backend: {e}")

    with sub_me:
        st.subheader("Thông tin tài khoản hiện tại (/users/me)")
        if not st.session_state.access_token:
            st.warning("Bạn cần đăng nhập trước.")
        else:
            if st.button("Lấy thông tin", key="btn_me"):
                try:
                    handle_response(api_get("/api/v1/users/me"))
                except requests.RequestException as e:
                    st.error(f"Không kết nối được backend: {e}")

    with sub_users:
        st.subheader("Danh sách toàn bộ user (chỉ ADMIN)")
        if not st.session_state.access_token:
            st.warning("Bạn cần đăng nhập bằng tài khoản ADMIN trước.")
        else:
            if st.button("Lấy danh sách user", key="btn_users"):
                try:
                    handle_response(api_get("/api/v1/users"))
                except requests.RequestException as e:
                    st.error(f"Không kết nối được backend: {e}")

    with sub_refresh:
        st.subheader("Làm mới access token")
        if not st.session_state.refresh_token:
            st.warning("Bạn cần đăng nhập trước để có refresh token.")
        else:
            st.caption("Lưu ý: mỗi refresh_token chỉ dùng được 1 lần (rotation).")
            if st.button("Refresh", key="btn_refresh"):
                try:
                    r = api_post("/api/v1/auth/refresh", {"refresh_token": st.session_state.refresh_token})
                    if r.status_code == 200:
                        data = r.json()
                        st.session_state.access_token = data["access_token"]
                        st.session_state.refresh_token = data["refresh_token"]
                        st.success("Đã cấp token mới!")
                        st.json(data)
                    else:
                        handle_response(r)
                except requests.RequestException as e:
                    st.error(f"Không kết nối được backend: {e}")

# ============================================================
# TAB: NỘI DUNG HỌC (subjects → grades → chapters → lessons → knowledge points)
# ============================================================
with tab_content:
    if not st.session_state.access_token:
        st.warning("Bạn cần đăng nhập trước (mọi API nội dung đều yêu cầu xác thực).")
    else:
        if not is_teacher_or_admin():
            st.info("Bạn đang đăng nhập với vai trò STUDENT — chỉ xem được danh sách, không tạo mới được (cần TEACHER/ADMIN).")

        sub_subject, sub_grade, sub_chapter, sub_lesson, sub_kp = st.tabs(
            ["Môn học", "Lớp", "Chương", "Bài học", "Kiến thức"]
        )

        with sub_subject:
            st.subheader("Môn học (Subjects)")
            if is_teacher_or_admin():
                with st.form("create_subject"):
                    name = st.text_input("Tên môn học", key="subj_name")
                    desc = st.text_area("Mô tả", key="subj_desc")
                    if st.form_submit_button("Tạo môn học"):
                        handle_response(api_post("/api/v1/subjects", {"name": name, "description": desc}), "Tạo thành công!")
            if st.button("📄 Tải danh sách môn học", key="list_subjects"):
                handle_response(api_get("/api/v1/subjects"))

        with sub_grade:
            st.subheader("Lớp (Grades)")
            subjects = fetch_options("/api/v1/subjects")
            if is_teacher_or_admin():
                with st.form("create_grade"):
                    subject_id = select_from("Thuộc môn học", subjects, key="grade_subject_sel")
                    name = st.text_input("Tên lớp (vd: Lớp 10)", key="grade_name")
                    if st.form_submit_button("Tạo lớp"):
                        if subject_id:
                            handle_response(api_post("/api/v1/grades", {"subject_id": subject_id, "name": name}), "Tạo thành công!")
                        else:
                            st.error("Cần có ít nhất 1 môn học trước.")
            st.markdown("**Xem danh sách lớp:**")
            filt_subject_id = select_from("Lọc theo môn học (tuỳ chọn)", subjects, key="grade_filter_sel") if subjects else None
            if st.button("📄 Tải danh sách lớp", key="list_grades"):
                handle_response(api_get("/api/v1/grades", params={"subject_id": filt_subject_id} if filt_subject_id else None))

        with sub_chapter:
            st.subheader("Chương (Chapters)")
            subjects = fetch_options("/api/v1/subjects")
            chap_subj_sel = select_from("Môn học", subjects, key="chap_subj_sel") if subjects else None
            grades = fetch_options("/api/v1/grades", params={"subject_id": chap_subj_sel} if chap_subj_sel else None)
            chap_grade_sel = select_from("Lớp", grades, key="chap_grade_sel") if grades else None

            if is_teacher_or_admin():
                with st.form("create_chapter"):
                    st.caption(f"Sẽ tạo chương thuộc lớp đã chọn ở trên.")
                    name = st.text_input("Tên chương", key="chap_name")
                    order = st.number_input("Thứ tự", min_value=0, value=0, key="chap_order")
                    if st.form_submit_button("Tạo chương"):
                        if chap_grade_sel:
                            handle_response(
                                api_post("/api/v1/chapters", {"grade_id": chap_grade_sel, "name": name, "order": order}),
                                "Tạo thành công!",
                            )
                        else:
                            st.error("Cần chọn Lớp ở trên trước (và Lớp đó phải đã tồn tại).")

            st.markdown("**Xem danh sách chương:**")
            if st.button("📄 Tải danh sách chương", key="list_chapters"):
                handle_response(api_get("/api/v1/chapters", params={"grade_id": chap_grade_sel} if chap_grade_sel else None))

        with sub_lesson:
            st.subheader("Bài học (Lessons)")
            subjects = fetch_options("/api/v1/subjects")
            s_sel = select_from("Môn học", subjects, key="lesson_subj_sel") if subjects else None
            grades = fetch_options("/api/v1/grades", params={"subject_id": s_sel} if s_sel else None)
            g_sel = select_from("Lớp", grades, key="lesson_grade_sel") if grades else None
            chapters = fetch_options("/api/v1/chapters", params={"grade_id": g_sel} if g_sel else None)
            c_sel = select_from("Chương", chapters, key="lesson_chapter_sel") if chapters else None

            if is_teacher_or_admin():
                with st.form("create_lesson"):
                    name = st.text_input("Tên bài học", key="lesson_name")
                    content = st.text_area("Nội dung", key="lesson_content")
                    order = st.number_input("Thứ tự", min_value=0, value=0, key="lesson_order")
                    if st.form_submit_button("Tạo bài học"):
                        if c_sel:
                            handle_response(
                                api_post(
                                    "/api/v1/lessons",
                                    {"chapter_id": c_sel, "name": name, "content": content, "order": order},
                                ),
                                "Tạo thành công!",
                            )
                        else:
                            st.error("Cần chọn Chương ở trên trước.")

            st.markdown("**Xem danh sách bài học:**")
            if st.button("📄 Tải danh sách bài học", key="list_lessons"):
                handle_response(api_get("/api/v1/lessons", params={"chapter_id": c_sel} if c_sel else None))

        with sub_kp:
            st.subheader("Kiến thức (Knowledge Points)")
            subjects = fetch_options("/api/v1/subjects")
            s_sel = select_from("Môn học", subjects, key="kp_subj_sel") if subjects else None
            grades = fetch_options("/api/v1/grades", params={"subject_id": s_sel} if s_sel else None)
            g_sel = select_from("Lớp", grades, key="kp_grade_sel") if grades else None
            chapters = fetch_options("/api/v1/chapters", params={"grade_id": g_sel} if g_sel else None)
            c_sel = select_from("Chương", chapters, key="kp_chapter_sel") if chapters else None
            lessons = fetch_options("/api/v1/lessons", params={"chapter_id": c_sel} if c_sel else None)
            l_sel = select_from("Bài học", lessons, key="kp_lesson_sel") if lessons else None

            if is_teacher_or_admin():
                with st.form("create_kp"):
                    name = st.text_input("Tên kiến thức", key="kp_name")
                    if st.form_submit_button("Tạo điểm kiến thức"):
                        if l_sel:
                            handle_response(
                                api_post("/api/v1/knowledge-points", {"lesson_id": l_sel, "name": name}), "Tạo thành công!"
                            )
                        else:
                            st.error("Cần chọn Bài học ở trên trước.")

            st.markdown("**Xem danh sách kiến thức:**")
            if st.button("📄 Tải danh sách kiến thức", key="list_kp"):
                handle_response(api_get("/api/v1/knowledge-points", params={"lesson_id": l_sel} if l_sel else None))

# ============================================================
# TAB: NGÂN HÀNG CÂU HỎI
# ============================================================
with tab_questions:
    if not st.session_state.access_token:
        st.warning("Bạn cần đăng nhập trước.")
    else:
        sub_create_q, sub_search_q = st.tabs(["Tạo câu hỏi (Giáo viên)", "Tìm kiếm / Danh sách"])

        with sub_create_q:
            if not is_teacher_or_admin():
                st.info("Cần vai trò TEACHER/ADMIN để tạo câu hỏi.")
            else:
                st.subheader("Tạo câu hỏi mới")
                subjects = fetch_options("/api/v1/subjects")
                s_sel = select_from("Môn học", subjects, key="q_subj_sel") if subjects else None
                grades = fetch_options("/api/v1/grades", params={"subject_id": s_sel} if s_sel else None)
                g_sel = select_from("Lớp", grades, key="q_grade_sel") if grades else None
                chapters = fetch_options("/api/v1/chapters", params={"grade_id": g_sel} if g_sel else None)
                c_sel = select_from("Chương", chapters, key="q_chapter_sel") if chapters else None
                lessons = fetch_options("/api/v1/lessons", params={"chapter_id": c_sel} if c_sel else None)
                l_sel = select_from("Bài học", lessons, key="q_lesson_sel") if lessons else None
                kps = fetch_options("/api/v1/knowledge-points", params={"lesson_id": l_sel} if l_sel else None)
                kp_id = select_from("Điểm kiến thức", kps, key="q_kp_sel") if kps else None

                q_type = st.selectbox(
                    "Loại câu hỏi", ["SINGLE_CHOICE", "MULTIPLE_CHOICE", "TRUE_FALSE", "SHORT_ANSWER", "NUMERICAL"], key="q_type"
                )
                q_difficulty = st.selectbox(
                    "Độ khó", ["RECOGNITION", "COMPREHENSION", "APPLICATION", "ADVANCED_APPLICATION"], key="q_difficulty"
                )
                content_text = st.text_area("Nội dung câu hỏi", key="q_content")

                options_payload = []
                correct_answer = ""
                if q_type in ("SINGLE_CHOICE", "MULTIPLE_CHOICE", "TRUE_FALSE"):
                    st.caption("Nhập các lựa chọn (tối thiểu 2, tích vào ô 'Đúng' cho đáp án đúng):")
                    n_opts = st.number_input("Số lựa chọn", min_value=2, max_value=8, value=4, key="q_n_opts")
                    for i in range(int(n_opts)):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            opt_text = st.text_input(f"Lựa chọn {i + 1}", key=f"q_opt_text_{i}")
                        with col2:
                            opt_correct = st.checkbox("Đúng", key=f"q_opt_correct_{i}")
                        if opt_text:
                            options_payload.append({"content": opt_text, "is_correct": opt_correct, "order": i})
                else:
                    correct_answer = st.text_input("Đáp án đúng (SHORT_ANSWER/NUMERICAL)", key="q_correct_answer")

                explanation = st.text_area("Giải thích (tuỳ chọn)", key="q_explanation")
                solution = st.text_area("Lời giải chi tiết (tuỳ chọn)", key="q_solution")
                source = st.text_input("Nguồn (tuỳ chọn)", key="q_source")

                if st.button("Tạo câu hỏi", key="btn_create_question"):
                    if not kp_id:
                        st.error("Cần chọn Điểm kiến thức (tạo trước ở tab 'Nội dung học' nếu chưa có).")
                    else:
                        payload = {
                            "content": content_text,
                            "type": q_type,
                            "difficulty": q_difficulty,
                            "knowledge_point_id": kp_id,
                            "correct_answer": correct_answer,
                            "explanation": explanation,
                            "solution": solution,
                            "source": source,
                            "options": options_payload,
                        }
                        handle_response(api_post("/api/v1/questions", payload), "Tạo câu hỏi thành công!")

        with sub_search_q:
            st.subheader("Tìm kiếm câu hỏi")
            col1, col2, col3 = st.columns(3)
            with col1:
                f_type = st.selectbox(
                    "Loại", ["(Tất cả)", "SINGLE_CHOICE", "MULTIPLE_CHOICE", "TRUE_FALSE", "SHORT_ANSWER", "NUMERICAL"], key="fq_type"
                )
            with col2:
                f_diff = st.selectbox(
                    "Độ khó", ["(Tất cả)", "RECOGNITION", "COMPREHENSION", "APPLICATION", "ADVANCED_APPLICATION"], key="fq_diff"
                )
            with col3:
                f_keyword = st.text_input("Từ khoá", key="fq_keyword")

            if st.button("🔍 Tìm kiếm", key="btn_search_questions"):
                params = {}
                if f_type != "(Tất cả)":
                    params["type"] = f_type
                if f_diff != "(Tất cả)":
                    params["difficulty"] = f_diff
                if f_keyword:
                    params["keyword"] = f_keyword
                handle_response(api_get("/api/v1/questions", params=params))

# ============================================================
# TAB: ĐỀ THI (Giáo viên tạo/quản lý)
# ============================================================
with tab_exams:
    if not st.session_state.access_token:
        st.warning("Bạn cần đăng nhập trước.")
    else:
        sub_create_exam, sub_manage_exam, sub_list_exam = st.tabs(["Tạo đề thi", "Thêm câu hỏi / Xuất bản", "Danh sách đề thi"])

        with sub_create_exam:
            if not is_teacher_or_admin():
                st.info("Cần vai trò TEACHER/ADMIN để tạo đề thi.")
            else:
                st.subheader("Tạo đề thi mới")
                with st.form("create_exam"):
                    title = st.text_input("Tiêu đề đề thi", key="exam_title")
                    desc = st.text_area("Mô tả", key="exam_desc")
                    duration = st.number_input("Thời gian làm bài (phút)", min_value=1, max_value=300, value=45, key="exam_duration")
                    if st.form_submit_button("Tạo đề thi"):
                        handle_response(
                            api_post("/api/v1/exams", {"title": title, "description": desc, "duration_minutes": duration}),
                            "Tạo đề thi thành công! (trạng thái DRAFT — sang tab bên cạnh để thêm câu hỏi và xuất bản)",
                        )

        with sub_manage_exam:
            if not is_teacher_or_admin():
                st.info("Cần vai trò TEACHER/ADMIN.")
            else:
                st.subheader("Thêm câu hỏi vào đề thi / Xuất bản")
                exams = fetch_options("/api/v1/exams")
                exam_id = select_from("Chọn đề thi", exams, name_key="title", key="manage_exam_sel") if exams else None

                if exam_id:
                    if st.button("📄 Xem chi tiết đề thi", key="btn_view_exam"):
                        handle_response(api_get(f"/api/v1/exams/{exam_id}"))

                    st.markdown("---")
                    st.write("**Thêm câu hỏi vào đề:**")
                    questions = fetch_options("/api/v1/questions", params={"status_filter": "APPROVED"})
                    if not questions:
                        questions = fetch_options("/api/v1/questions")
                        if questions:
                            st.caption("(Hiện danh sách toàn bộ câu hỏi vì chưa có câu nào ở trạng thái APPROVED)")
                    q_sel = select_from("Chọn câu hỏi", questions, name_key="content", key="exam_q_sel") if questions else None
                    order = st.number_input("Thứ tự trong đề", min_value=0, value=0, key="exam_q_order")
                    points = st.number_input("Điểm", min_value=0.1, value=1.0, step=0.5, key="exam_q_points")
                    if st.button("➕ Thêm câu hỏi vào đề", key="btn_add_q_to_exam"):
                        if q_sel:
                            handle_response(
                                api_post(f"/api/v1/exams/{exam_id}/questions", {"question_id": q_sel, "order": order, "points": points}),
                                "Đã thêm câu hỏi vào đề!",
                            )
                        else:
                            st.error("Cần có ít nhất 1 câu hỏi trong ngân hàng trước.")

                    st.markdown("---")
                    if st.button("🚀 Xuất bản đề thi (PUBLISH)", key="btn_publish_exam"):
                        handle_response(api_post(f"/api/v1/exams/{exam_id}/publish", {}), "Đã xuất bản đề thi!")

        with sub_list_exam:
            st.subheader("Danh sách đề thi")
            if st.button("📄 Tải danh sách đề thi", key="btn_list_exams"):
                handle_response(api_get("/api/v1/exams"))

# ============================================================
# TAB: LÀM BÀI THI (Học sinh)
# ============================================================
with tab_attempts:
    if not st.session_state.access_token:
        st.warning("Bạn cần đăng nhập trước (nên đăng nhập bằng tài khoản STUDENT).")
    else:
        st.subheader("Danh sách đề thi khả dụng")
        exams = fetch_options("/api/v1/exams")
        if st.button("📄 Tải danh sách đề thi", key="btn_list_exams_student"):
            handle_response(api_get("/api/v1/exams"))

        st.markdown("---")
        st.subheader("Bắt đầu làm bài")
        exam_id = select_from("Chọn đề thi để làm", exams, name_key="title", key="attempt_exam_sel") if exams else None
        if exam_id and st.button("▶️ Bắt đầu làm bài (start attempt)", key="btn_start_attempt"):
            r = api_post(f"/api/v1/exams/{exam_id}/start", {})
            payload = handle_response(r, "Đã bắt đầu làm bài!")
            if payload:
                st.session_state["current_attempt"] = payload

        if st.session_state.get("current_attempt"):
            attempt = st.session_state["current_attempt"]
            st.markdown("---")
            st.subheader(f"Bài làm: attempt_id = {attempt['attempt_id'][:8]}...")
            answers = []
            for q in attempt.get("questions", []):
                st.write(f"**{q['content']}**  ({q['points']} điểm)")
                if q.get("options"):
                    opt_labels = [o["content"] for o in q["options"]]
                    chosen = st.multiselect("Chọn đáp án", opt_labels, key=f"attempt_ans_{q['question_id']}")
                    chosen_ids = [o["id"] for o in q["options"] if o["content"] in chosen]
                    answers.append({"question_id": q["question_id"], "selected_option_ids": chosen_ids, "answer_text": ""})
                else:
                    text_ans = st.text_input("Câu trả lời", key=f"attempt_ans_text_{q['question_id']}")
                    answers.append({"question_id": q["question_id"], "selected_option_ids": [], "answer_text": text_ans})
                st.divider()

            if st.button("✅ Nộp bài", key="btn_submit_attempt"):
                r = api_post(f"/api/v1/attempts/{attempt['attempt_id']}/submit", {"answers": answers})
                result = handle_response(r, "Đã nộp bài! Xem kết quả bên dưới.")
                if result:
                    st.session_state["current_attempt"] = None
                    st.session_state["last_result"] = result

        if st.session_state.get("last_result"):
            st.markdown("---")
            st.subheader("Kết quả bài làm gần nhất")
            res = st.session_state["last_result"]
            st.metric("Điểm số", f"{res.get('score')} / {res.get('max_score')}")
            st.json(res)
