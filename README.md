# CHEMGENIE

Nền tảng Web + Mobile hỗ trợ học tập và luyện thi Hóa học THPT, tích hợp AI Tutor (RAG), sinh câu hỏi tự động có kiểm định (Chemistry Question Validator), luyện đề, phân tích năng lực và cá nhân hóa lộ trình học tập.

> Tài liệu này được cập nhật dần theo từng PHASE triển khai. Hiện tại đã hoàn tất **PHASE 0 (System Analysis)** và **PHASE 1 (Backend Foundation)**.

## 1. Project overview
CHEMGENIE gồm 3 vai trò (Student/Teacher/Admin), backend FastAPI, web Next.js, mobile Flutter, cùng các module AI (Tutor, RAG, Question Generator, Validator). Xem chi tiết phân tích tại `docs/phase0-system-analysis.md`.

## 2. Features (đã có tính đến hiện tại)
- Đăng ký / đăng nhập (JWT access + refresh token, rotation, revoke).
- RBAC theo 3 role: STUDENT / TEACHER / ADMIN.
- Chuẩn hóa response lỗi `{success:false, error:{code, message}}`.
- Kiến trúc layered: route → service → repository → ORM.

## 3. Architecture
Xem `docs/phase0-system-analysis.md` mục 3 (System Architecture) và mục 4 (ERD).

## 4. Requirements
- Python 3.12+
- PostgreSQL 16+ (dùng SQLite chỉ khi chạy test)
- Redis 7+
- Docker & Docker Compose (khuyến nghị)

## 5. Installation
```bash
git clone <repo>
cd chemgenie
cp .env.example .env   # rồi điền JWT_SECRET và các giá trị cần thiết
```

## 6. Environment variables
Xem `.env.example` ở thư mục gốc — không commit file `.env` thật.

## 7. Database migration
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
```

## 8. Seed data
```bash
cd backend
python -m scripts.seed_roles   # tạo 3 role STUDENT/TEACHER/ADMIN — bắt buộc trước khi register user
```

## 9. Running backend
```bash
cd backend
uvicorn app.main:app --reload
# Swagger UI: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

## 10. Running web
Sẽ bổ sung ở PHASE 4.

### 10.1 Streamlit API Tester
Có sẵn 1 giao diện Streamlit đơn giản để test API backend tại `streamlit_app/`.
```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```
Xem chi tiết (bao gồm hướng dẫn deploy lên Streamlit Community Cloud) tại `streamlit_app/README.md`.

## 11. Running Flutter
Sẽ bổ sung ở PHASE 5.

## 12. Testing
```bash
cd backend
pytest -v
```
Hiện tại: 9/9 test pass (health check, register/login/me, RBAC, refresh token rotation, logout).

## 13. Docker
```bash
docker compose up --build
```
Compose khởi động Postgres + Redis + Backend (tự chạy migration + seed roles trước khi start server).

## 14. AI configuration
Sẽ bổ sung ở PHASE 6–9 (RAG, AI Tutor, Question Generator, Validator).

## 15. Troubleshooting
- Lỗi `ROLE_NOT_FOUND` khi register → chưa chạy `python -m scripts.seed_roles`.
- Lỗi kết nối DB → kiểm tra `DATABASE_URL` trong `.env` và Postgres đã chạy (`docker compose ps`).
- Refresh token bị `REFRESH_TOKEN_REVOKED` sau khi gọi `/refresh` một lần → đúng hành vi (rotation), phải dùng refresh token mới nhất được trả về.

---

## Phase log

### PHASE 0 — System Analysis
Xem `docs/phase0-system-analysis.md`.

### PHASE 1 — Backend Foundation ✅
- **Implemented:** FastAPI app, PostgreSQL models (User/Role/RefreshToken), Alembic migration, JWT auth (access + refresh + rotation + revoke), RBAC dependency, chuẩn hóa error response, Docker Compose (Postgres/Redis/Backend healthcheck), seed script, pytest suite.
- **Files created:** `backend/app/**`, `backend/alembic/**`, `backend/tests/**`, `backend/scripts/seed_roles.py`, `Dockerfile`, `docker-compose.yml`, `.env.example`, `.gitignore`, `pytest.ini`.
- **Dependencies:** xem `backend/requirements.txt` (đã cài và test thành công).
- **Database migrations:** `alembic/versions/b0be38a94f39_init_users_roles_refresh_tokens.py` — tạo bảng `roles`, `users`, `refresh_tokens`. Đã verify apply thành công trên SQLite (giả lập); production dùng Postgres qua cùng migration.
- **API:** `/health`, `/api/v1/auth/{register,login,refresh,logout}`, `/api/v1/users/{me,""}` (list — admin only).
- **Tests:** `backend/tests/test_auth.py` — 9 test, bao phủ register/login/me, duplicate email, sai mật khẩu, RBAC (student bị chặn, admin được phép), refresh token rotation + reuse rejected, logout revoke, truy cập không token. Chạy ổn định 5 lần liên tiếp không flaky.
- **Known issues:** Chưa test thực tế trên Postgres/Redis thật (môi trường sandbox không có mạng tới Docker Hub) — migration đã verify logic đúng qua SQLite, cấu trúc SQL tương thích Postgres (dùng kiểu chuẩn, không dùng tính năng riêng của SQLite). Cần chạy `docker compose up` ở môi trường có Docker để xác nhận lần cuối.
- **Next phase:** PHASE 2 — Content + Question Bank (subjects/grades/chapters/lessons/questions CRUD).
