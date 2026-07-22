"""Tests for authentication endpoints."""
import pytest
import requests

BASE = "http://localhost:8000"

def test_health():
    r = requests.get(f"{BASE}/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"

def test_auth_flow():
    # Test login con credenciales existentes
    r = requests.post(f"{BASE}/api/auth/login", json={
        "email": "test@iztack.com",
        "password": "test1234"
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    token = data["access_token"]
    assert len(token) > 50

    # Test /api/dashboard con token
    r = requests.get(f"{BASE}/api/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    dashboard = r.json()
    assert "kpi" in dashboard

    # Test /api/chat/history con token
    r = requests.get(f"{BASE}/api/chat/history", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code in [200, 401]

if __name__ == "__main__":
    test_health()
    test_auth_flow()
    print("✅ All auth tests passed")
