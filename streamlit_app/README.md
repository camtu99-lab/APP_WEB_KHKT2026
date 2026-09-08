# ChemGenie API Tester (Streamlit)

Giao diện Streamlit đơn giản để test các API của backend ChemGenie (đăng ký, đăng nhập,
xem thông tin cá nhân, danh sách user cho admin, refresh token).

## Chạy local

1. Chạy backend trước (xem `../backend/README` hoặc mục 9 trong README gốc):
   ```bash
   cd ../backend
   uvicorn app.main:app --reload
   ```
2. Cài & chạy Streamlit:
   ```bash
   cd streamlit_app
   pip install -r requirements.txt
   streamlit run app.py
   ```
3. Mặc định app sẽ gọi `http://localhost:8000`. Có thể đổi trong ô "Backend API URL"
   ở sidebar, hoặc set biến môi trường trước khi chạy:
   ```bash
   export CHEMGENIE_API_URL="http://localhost:8000"
   ```

## Deploy lên Streamlit Community Cloud

**Lưu ý quan trọng:** Streamlit Cloud chỉ host được phần giao diện Streamlit này —
nó KHÔNG chạy được backend FastAPI + PostgreSQL + Redis. Bạn cần deploy backend
ở một nơi khác trước (Render, Railway, Fly.io, VPS, v.v.), rồi trỏ Streamlit app
tới URL backend đó.

Các bước:
1. Push repo này lên GitHub (repo phải public, hoặc bạn dùng tài khoản Streamlit
   có quyền truy cập private repo).
2. Deploy backend FastAPI lên một dịch vụ hỗ trợ Docker/Postgres (ví dụ Render,
   Railway) và lấy URL public, ví dụ `https://chemgenie-api.onrender.com`.
3. Vào [streamlit.io/cloud](https://streamlit.io/cloud) → "New app" → chọn repo
   → **Main file path:** `streamlit_app/app.py`.
4. Trong phần "Advanced settings" → "Secrets", thêm:
   ```toml
   CHEMGENIE_API_URL = "https://chemgenie-api.onrender.com"
   ```
   (Streamlit Cloud set secrets này thành biến môi trường khi chạy app.)
5. Deploy. App sẽ tự lấy `CHEMGENIE_API_URL` làm URL backend mặc định.
