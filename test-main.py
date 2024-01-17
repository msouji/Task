import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_user_without_authentication():
    response = client.get("/validate_user/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_read_user_with_authentication():
    # Assuming a valid token for testing purposes
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcwNTUwMDI3Ny45OTA1NTc0fQ.kg4l3O_n-im-cTIvpTLdeIuofX6CSJuRUFhSRK6Qm5g"
    response = client.get("/validate_user/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"msg": "Welcome"}

def test_get_list_without_authentication():
    response = client.get("/get_list/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_get_list_with_authentication():
    # Assuming a valid token for testing purposes
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcwNTUwMDI3Ny45OTA1NTc0fQ.kg4l3O_n-im-cTIvpTLdeIuofX6CSJuRUFhSRK6Qm5g"
    response = client.get("/get_list/?int1=2&int2=5&limit=10&str1=foo&str2=bar", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == ["1", "foo", "3", "foo", "bar", "foo", "7", "foo", "9", "foobar"]

def test_login_with_valid_credentials():
    response = client.post("/login", data={"username": "johndoe", "password": "secret"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_with_invalid_credentials():
    response = client.post("/login", data={"username": "invaliduser", "password": "invalidpassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect username or password"}
