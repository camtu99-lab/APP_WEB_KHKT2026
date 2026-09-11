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
python -m scripts.seed_roles     # tạo 3 role STUDENT/TEACHER/ADMIN — bắt buộc trước khi register user
python -m scripts.seed_content   # tạo dữ liệu DEMO: 1 subject/grade/chapter/lesson/knowledge_point + 1 câu hỏi mẫu
```

## 9. Running backend
```bash
cd backend
uvicorn app.main:app --reload
# Swagger UI: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

## 10. Running web
```bash
cd apps/web
cp .env.local.example .env.local   # chỉnh NEXT_PUBLIC_API_URL nếu backend không chạy ở localhost:8000
npm install
npm run dev
# http://localhost:3000
```

## 11. Running Flutter
Sẽ bổ sung ở PHASE 5.

## 12. Testing
```bash
cd backend
pytest -v
```
Hiện tại: 29/29 test pass (auth + RBAC + content + question bank + exam system + anti-cheat).

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

### PHASE 2 — Content + Question Bank ✅
- **Implemented:** Content hierarchy (Subject → Grade → Chapter → Lesson → KnowledgePoint) với validate FK từng cấp (không tạo Grade nếu Subject không tồn tại, v.v.); Question Bank (Question + QuestionOption) với validate nghiệp vụ ngay ở tầng schema (đủ option, có đúng 1 đáp án đúng cho SINGLE_CHOICE, không được 0 hoặc >1 đáp án đúng, SHORT_ANSWER/NUMERICAL bắt buộc `correct_answer`); search/filter theo knowledge_point/type/difficulty/status/keyword; RBAC nghiệp vụ — Student chỉ thấy câu hỏi `PUBLISHED`, Teacher/Admin mới được tạo nội dung và duyệt câu hỏi.
- **Files created:** `app/models/{content,question}.py`, `app/schemas/{content,question}.py`, `app/repositories/{content_repository,question_repository}.py`, `app/services/{content_service,question_service}.py`, `app/api/v1/{content,questions}.py`, `scripts/seed_content.py`, `tests/{helpers,test_content_and_questions}.py`.
- **Files modified:** `app/models/__init__.py`, `app/main.py` (đăng ký router mới), `docker-compose.yml` (thêm bước seed_content).
- **Dependencies:** không thêm mới, dùng lại `requirements.txt` Phase 1.
- **Database migrations:** `3b22e1b41956_add_content_hierarchy_and_question_bank.py` — thêm 6 bảng (`subjects`, `grades`, `chapters`, `lessons`, `knowledge_points`, `questions`, `question_options`). Verify apply thành công trên SQLite.
- **API:** `POST/GET /api/v1/subjects`, `/grades`, `/chapters`, `/lessons`, `/knowledge-points` (write: Teacher/Admin, read: mọi role đã đăng nhập); `POST /api/v1/questions`, `GET /api/v1/questions` (search/filter), `GET /api/v1/questions/{id}`, `PATCH /api/v1/questions/{id}/status`.
- **Tests:** 10 test mới trong `test_content_and_questions.py` — tổng cộng **19/19 pass**. Bao phủ: tạo đủ hierarchy, từ chối FK không tồn tại (không lỗi 500), RBAC ghi/đọc, tạo câu hỏi hợp lệ, từ chối câu hỏi không có đáp án đúng, từ chối SINGLE_CHOICE có nhiều đáp án đúng, học sinh không thấy câu hỏi chưa publish, luồng publish → học sinh thấy được, học sinh không được đổi status.
- **Known issues:** Chưa có `question_versions` (lịch sử chỉnh sửa câu hỏi) và `question_tags` — để lại cho phase sau khi cần thiết thực tế phát sinh, tránh over-engineer sớm.
- **Next phase:** PHASE 3 — Exam System (tạo đề, làm bài, auto-save, chấm điểm server-side).

### PHASE 3 — Exam System ✅
- **Implemented:** Exam (DRAFT→PUBLISHED, không cho publish đề rỗng), ExamQuestion (chỉ nhận câu hỏi đã PUBLISHED), Attempt/Answer với **chấm điểm hoàn toàn server-side** — client chỉ gửi lựa chọn, không gửi đúng/sai; server so khớp với `is_correct` lưu trong DB. Chặn: nộp bài 2 lần, nộp/xem bài của người khác, bắt đầu làm đề chưa publish, xem kết quả trước khi nộp.
- **Files created:** `app/models/exam.py`, `app/schemas/exam.py`, `app/repositories/exam_repository.py`, `app/services/exam_service.py`, `app/api/v1/exams.py`, `tests/test_exam_system.py`.
- **Files modified:** `app/models/__init__.py`, `app/main.py` (đăng ký router `exams` + `attempts`).
- **Database migrations:** `d3b6bb181da6_add_exam_system.py` — thêm 4 bảng (`exams`, `exam_questions`, `attempts`, `answers`). Verify apply thành công trên SQLite.
- **API:** `POST/GET /api/v1/exams`, `POST /api/v1/exams/{id}/questions`, `POST /api/v1/exams/{id}/publish`, `GET /api/v1/exams/{id}`, `POST /api/v1/exams/{id}/start`, `POST /api/v1/attempts/{id}/submit`, `GET /api/v1/attempts/{id}/result`.
- **Tests:** 10 test mới — tổng **29/29 pass**. Có test "chống gian lận" cố tình gửi field `is_correct: true` giả từ client để xác nhận server luôn tự chấm lại từ DB, không tin client.
- **Known issues:** Chấm NUMERICAL bằng so khớp chuỗi chính xác, chưa có dung sai số học (vd 0.1 vs 0.10) — sẽ cải thiện khi có yêu cầu thực tế; chưa có countdown timer / auto-save phía client (thuộc Phase 4 - Web frontend) — backend đã hỗ trợ đủ dữ liệu (`duration_minutes`, `started_at`) để frontend tự tính đếm ngược.
- **Next phase:** PHASE 4 — Web Frontend (Next.js).

### PHASE 4 — Web Frontend (Next.js) ✅
- **Implemented:** App Router + TypeScript + Tailwind, gọi thẳng backend qua `NEXT_PUBLIC_API_URL` (không dùng token giả, không mock). Auth context lưu JWT ở localStorage, tự lấy `/me` khi load lại trang. Luồng đầy đủ: đăng ký/đăng nhập → dashboard theo role → (Student) chọn đề → làm bài có **đếm ngược thời gian thật + tự nộp bài khi hết giờ** → xem kết quả chi tiết từng câu; (Teacher) tạo câu hỏi (cascading picker Subject→Grade→Chapter→Lesson→KnowledgePoint dùng đúng API Phase 2), tạo đề + tìm câu hỏi PUBLISHED để thêm vào đề + publish.
- **Files created:** toàn bộ `apps/web/` — `app/{login,register,page}.tsx`, `app/student/**`, `app/teacher/**`, `lib/{api,auth-context}.ts`, `components/{Button,Input,Card,Sidebar,KnowledgePointPicker}.tsx`, cấu hình `package.json/tsconfig/tailwind.config/next.config/postcss.config`, `.env.local.example`.
- **Dependencies:** Next.js **14.2.35** (đã chủ động nâng từ 14.2.15 do `npm install` cảnh báo lỗ hổng bảo mật đã biết), React 18.3, Tailwind 3.4. Đã `npm install` thật, không suy đoán.
- **Design:** bảng màu riêng cho CHEMGENIE (xanh "flask" làm accent chính, nền giấy ấm, viền hairline thay vì đổ bóng) — nhất quán với mockup đã duyệt trước đó.
- **Build:** `npm run build` chạy thật — **compile thành công, type-check qua hết 10 route**, không lỗi TypeScript/ESLint.
- **Known issues:** Ban đầu dùng `next/font/google` (Fraunces + Inter) nhưng sandbox không có mạng tới Google Fonts nên build fail — đã sửa bằng cách chuyển sang font hệ thống (system-ui/Georgia) để không phụ thuộc mạng lúc build; ở môi trường có mạng bạn có thể khôi phục Google Fonts nếu muốn. `npm audit` còn báo lỗ hổng ở các tính năng Next.js không dùng trong app này (next/image, Server Actions nâng cao, custom server, i18n middleware) — rủi ro thấp cho MVP nhưng nên theo dõi khi lên production thật. Chưa có trang quản lý content hierarchy (tạo Subject/Grade/Chapter/Lesson) trên UI — hiện phải tạo qua API/Swagger trước, UI mới chỉ có cascading picker để *chọn*, chưa có form để *tạo*.
- **Next phase:** PHASE 5 — Mobile App (Flutter).
