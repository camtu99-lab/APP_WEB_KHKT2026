def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "ok"


def test_register_login_me_flow(client):
    register_payload = {
        "email": "student1@chemgenie.vn",
        "full_name": "Nguyen Van A",
        "password": "SecurePass123",
        "role": "STUDENT",
    }
    r1 = client.post("/api/v1/auth/register", json=register_payload)
    assert r1.status_code == 201, r1.text
    assert r1.json()["role"] == "STUDENT"

    r2 = client.post(
        "/api/v1/auth/login",
        json={"email": "student1@chemgenie.vn", "password": "SecurePass123"},
    )
    assert r2.status_code == 200, r2.text
    tokens = r2.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    r3 = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert r3.status_code == 200
    assert r3.json()["email"] == "student1@chemgenie.vn"


def test_register_duplicate_email_rejected(client):
    payload = {
        "email": "dup@chemgenie.vn",
        "full_name": "User A",
        "password": "SecurePass123",
        "role": "STUDENT",
    }
    r1 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_login_wrong_password_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@chemgenie.vn",
            "full_name": "User B",
            "password": "CorrectPass123",
            "role": "STUDENT",
        },
    )
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@chemgenie.vn", "password": "WrongPassword"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_rbac_student_cannot_list_users(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "student2@chemgenie.vn",
            "full_name": "Student Two",
            "password": "SecurePass123",
            "role": "STUDENT",
        },
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": "student2@chemgenie.vn", "password": "SecurePass123"}
    ).json()

    r = client.get("/api/v1/users", headers={"Authorization": f"Bearer {login['access_token']}"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "ROLE_NOT_ALLOWED"


def test_rbac_admin_can_list_users(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin1@chemgenie.vn",
            "full_name": "Admin One",
            "password": "SecurePass123",
            "role": "ADMIN",
        },
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": "admin1@chemgenie.vn", "password": "SecurePass123"}
    ).json()

    r = client.get("/api/v1/users", headers={"Authorization": f"Bearer {login['access_token']}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_refresh_token_rotation_and_reuse_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh1@chemgenie.vn",
            "full_name": "Refresh User",
            "password": "SecurePass123",
            "role": "STUDENT",
        },
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": "refresh1@chemgenie.vn", "password": "SecurePass123"}
    ).json()

    r1 = client.post("/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert r1.status_code == 200
    new_tokens = r1.json()
    assert new_tokens["refresh_token"] != login["refresh_token"]

    # Refresh token cũ đã bị revoke (rotation) -> dùng lại phải bị từ chối
    r2 = client.post("/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert r2.status_code == 401
    assert r2.json()["error"]["code"] == "REFRESH_TOKEN_REVOKED"


def test_access_protected_route_without_token_rejected(client):
    r = client.get("/api/v1/users/me")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "MISSING_TOKEN"


def test_logout_revokes_refresh_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "logout1@chemgenie.vn",
            "full_name": "Logout User",
            "password": "SecurePass123",
            "role": "STUDENT",
        },
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": "logout1@chemgenie.vn", "password": "SecurePass123"}
    ).json()

    r1 = client.post("/api/v1/auth/logout", json={"refresh_token": login["refresh_token"]})
    assert r1.status_code == 204

    r2 = client.post("/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert r2.status_code == 401
