from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_signup_login_me():
    email = "test@example.com"
    pw = "password123"

    r = client.post("/auth/signup", json={"email": email, "password": pw})
    assert r.status_code in (201, 409)

    r = client.post("/auth/login", json={"email": email, "password": pw})
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == email