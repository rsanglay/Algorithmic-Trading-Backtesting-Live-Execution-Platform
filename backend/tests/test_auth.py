"""
Authentication API tests
"""
import pytest
from fastapi import status

from app.core.auth import verify_password, get_password_hash
from app.models.user import User


@pytest.mark.api
@pytest.mark.integration
class TestAuthAPI:
    """Test authentication endpoints"""

    @pytest.mark.asyncio
    async def test_register_user(self, async_client, db_session):
        """Test user registration"""
        payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "StrongPass123",
            "full_name": "New User",
        }

        response = await async_client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED, f"Response: {response.text}"
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]

        # Ensure the password was hashed in the database
        created_user = db_session.query(User).filter_by(email=payload["email"]).first()
        assert created_user is not None
        assert verify_password(payload["password"], created_user.hashed_password)

    @pytest.mark.asyncio
    async def test_login_user(self, async_client, db_session):
        """Test user login with valid credentials"""
        # Create user with plain password first
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        hashed = get_password_hash("StrongPass123")
        user = User(
            email="login@example.com",
            username="loginuser",
            hashed_password=hashed,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        payload = {"username": user.username, "password": "StrongPass123"}
        response = await async_client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == user.email

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client, db_session):
        """Test login with invalid password"""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        hashed = get_password_hash("StrongPass123")
        user = User(
            email="invalid@example.com",
            username="invaliduser",
            hashed_password=hashed,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        payload = {"username": "invaliduser", "password": "WrongPassword"}
        response = await async_client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]
