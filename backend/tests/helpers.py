def register_and_login(client, email: str, role: str = "TEACHER", password: str = "SecurePass123") -> str:
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Test User", "password": password, "role": role},
    )
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
