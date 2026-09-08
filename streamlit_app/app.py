"""
ChemGenie API Tester — giao diện Streamlit để test backend FastAPI.

Chạy local:
    streamlit run streamlit_app/app.py

Cấu hình URL backend qua biến môi trường CHEMGENIE_API_URL
(hoặc sửa trực tiếp trong ô "Backend API URL" ở sidebar).
"""

import os
from typing import Optional

import requests
import streamlit as st

DEFAULT_API_URL = os.environ.get("CHEMGENIE_API_URL", "http://localhost:8000")

st.set_page_config(page_title="ChemGenie API Tester", page_icon="🧪", layout="wide")

# ---------- Session state ----------
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None
if "user" not in st.session_state:
    st.session_state.user = None


def api_url() -> str:
    return st.session_state.get("api_url", DEFAULT_API_URL).rstrip("/")


def auth_headers() -> dict:
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}


def handle_response(resp: requests.Response, success_msg: Optional[str] = None):
    """Hiển thị kết quả gọi API theo format {success, data|error} của ChemGenie."""
    try:
        payload = resp.json()
    except ValueError:
        st.error(f"HTTP {resp.status_code}: không parse được JSON — {resp.text[:300]}")
        return None

    if resp.status_code >= 400 or payload.get("success") is False:
        err = payload.get("error", {})
        st.error(f"Lỗi [{err.get('code', resp.status_code)}]: {err.get('message', payload)}")
        return None

    if success_msg:
        st.success(success_msg)
    st.json(payload)
    return payload


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

# ---------- Main tabs ----------
tab_register, tab_login, tab_me, tab_users, tab_refresh = st.tabs(
    ["Đăng ký", "Đăng nhập", "Thông tin của tôi", "Danh sách user (Admin)", "Refresh token"]
)

with tab_register:
    st.subheader("Đăng ký tài khoản")
    with st.form("register_form"):
        email = st.text_input("Email", key="reg_email")
        full_name = st.text_input("Họ và tên", key="reg_full_name")
        password = st.text_input("Mật khẩu (>= 8 ký tự)", type="password", key="reg_password")
        role = st.selectbox("Vai trò", ["STUDENT", "TEACHER", "ADMIN"], key="reg_role")
        submitted = st.form_submit_button("Đăng ký")
    if submitted:
        try:
            r = requests.post(
                f"{api_url()}/api/v1/auth/register",
                json={"email": email, "full_name": full_name, "password": password, "role": role},
                timeout=10,
            )
            handle_response(r, success_msg="Đăng ký thành công! Chuyển sang tab Đăng nhập.")
        except requests.RequestException as e:
            st.error(f"Không kết nối được backend: {e}")

with tab_login:
    st.subheader("Đăng nhập")
    with st.form("login_form"):
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Mật khẩu", type="password", key="login_password")
        login_submitted = st.form_submit_button("Đăng nhập")
    if login_submitted:
        try:
            r = requests.post(
                f"{api_url()}/api/v1/auth/login",
                json={"email": login_email, "password": login_password},
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                st.session_state.access_token = data["access_token"]
                st.session_state.refresh_token = data["refresh_token"]
                me = requests.get(f"{api_url()}/api/v1/users/me", headers=auth_headers(), timeout=10)
                if me.status_code == 200:
                    st.session_state.user = me.json()
                st.success("Đăng nhập thành công!")
                st.rerun()
            else:
                handle_response(r)
        except requests.RequestException as e:
            st.error(f"Không kết nối được backend: {e}")

with tab_me:
    st.subheader("Thông tin tài khoản hiện tại (/users/me)")
    if not st.session_state.access_token:
        st.warning("Bạn cần đăng nhập trước.")
    else:
        if st.button("Lấy thông tin"):
            try:
                r = requests.get(f"{api_url()}/api/v1/users/me", headers=auth_headers(), timeout=10)
                handle_response(r)
            except requests.RequestException as e:
                st.error(f"Không kết nối được backend: {e}")

with tab_users:
    st.subheader("Danh sách toàn bộ user (chỉ ADMIN)")
    if not st.session_state.access_token:
        st.warning("Bạn cần đăng nhập bằng tài khoản ADMIN trước.")
    else:
        if st.button("Lấy danh sách user"):
            try:
                r = requests.get(f"{api_url()}/api/v1/users", headers=auth_headers(), timeout=10)
                handle_response(r)
            except requests.RequestException as e:
                st.error(f"Không kết nối được backend: {e}")

with tab_refresh:
    st.subheader("Làm mới access token")
    if not st.session_state.refresh_token:
        st.warning("Bạn cần đăng nhập trước để có refresh token.")
    else:
        st.caption("Lưu ý: mỗi refresh_token chỉ dùng được 1 lần (rotation).")
        if st.button("Refresh"):
            try:
                r = requests.post(
                    f"{api_url()}/api/v1/auth/refresh",
                    json={"refresh_token": st.session_state.refresh_token},
                    timeout=10,
                )
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
