import pytest
import requests
from typing import Dict, Any

@pytest.fixture
def api_client(base_url: str) -> requests.Session:
    """Create a session with the API."""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    return session

@pytest.fixture
def auth_token(api_client: requests.Session, base_url: str) -> str:
    """Get an authentication token."""
    response = api_client.post(
        f"{base_url}/api/auth/login",
        json={
            "username": "test_user",
            "password": "test_password"
        }
    )
    assert response.status_code == 200
    return response.json()["token"]

@pytest.fixture
def authenticated_client(api_client: requests.Session, auth_token: str) -> requests.Session:
    """Create an authenticated session."""
    api_client.headers.update({
        'Authorization': f'Bearer {auth_token}'
    })
    return api_client

class TestAuthAPI:
    def test_register_user(self, api_client: requests.Session, base_url: str):
        """Test user registration."""
        response = api_client.post(
            f"{base_url}/api/auth/register",
            json={
                "username": "new_user",
                "email": "new_user@example.com",
                "password": "secure_password123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["username"] == "new_user"
        assert "password" not in data

    def test_login_success(self, api_client: requests.Session, base_url: str):
        """Test successful login."""
        response = api_client.post(
            f"{base_url}/api/auth/login",
            json={
                "username": "test_user",
                "password": "test_password"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert isinstance(data["token"], str)

    def test_login_failure(self, api_client: requests.Session, base_url: str):
        """Test login with invalid credentials."""
        response = api_client.post(
            f"{base_url}/api/auth/login",
            json={
                "username": "test_user",
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_get_profile(self, authenticated_client: requests.Session, base_url: str):
        """Test getting user profile with valid token."""
        response = authenticated_client.get(f"{base_url}/api/auth/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data

    def test_update_profile(self, authenticated_client: requests.Session, base_url: str):
        """Test updating user profile."""
        response = authenticated_client.put(
            f"{base_url}/api/auth/profile",
            json={
                "email": "updated@example.com",
                "full_name": "Updated Name"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"
        assert data["full_name"] == "Updated Name"

    def test_change_password(self, authenticated_client: requests.Session, base_url: str):
        """Test changing user password."""
        response = authenticated_client.post(
            f"{base_url}/api/auth/change-password",
            json={
                "current_password": "test_password",
                "new_password": "new_secure_password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_logout(self, authenticated_client: requests.Session, base_url: str):
        """Test user logout."""
        response = authenticated_client.post(f"{base_url}/api/auth/logout")
        
        assert response.status_code == 200
        
        # Verify token is invalidated
        profile_response = authenticated_client.get(f"{base_url}/api/auth/profile")
        assert profile_response.status_code == 401

    @pytest.mark.parametrize("invalid_data", [
        {"username": "u", "password": "test_password"},  # Username too short
        {"username": "user", "password": "short"},       # Password too short
        {"username": "", "password": "test_password"},   # Empty username
        {"username": "user", "password": ""},           # Empty password
    ])
    def test_login_validation(self, api_client: requests.Session, base_url: str, invalid_data: Dict[str, Any]):
        """Test login input validation."""
        response = api_client.post(
            f"{base_url}/api/auth/login",
            json=invalid_data
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data 