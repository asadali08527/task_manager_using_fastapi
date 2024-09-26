# test_auth.py

from utils import *  # Import utility functions and testing helpers
from app.routers.authentication import get_db_session, authenticate_user, create_access_token, get_current_user
from app.config import SECRET_KEY, ALGORITHM  # Import secret key and algorithm for JWT encoding/decoding
from jose import jwt  # JWT library for encoding and decoding tokens
from datetime import timedelta  # Time delta for token expiration
import pytest  # Pytest framework for testing
from fastapi import HTTPException  # FastAPI HTTP exception for error handling

# Override the database session dependency for testing
app.dependency_overrides[get_db_session] = override_get_db


def test_authenticate_user(test_user):
    """
    Test user authentication with correct and incorrect credentials.
    """
    db = TestingSessionLocal()

    # Test with correct credentials
    authenticated_user = authenticate_user(test_user.username, 'testpassword', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    # Test with incorrect password
    non_authenticated_user = authenticate_user(test_user.username, 'wrongpassword', db)
    assert non_authenticated_user is None  # Should return None if authentication fails

    # Test with non-existent username
    non_existent_user = authenticate_user('nonexistentuser', 'testpassword', db)
    assert non_existent_user is None  # Should return None if user is not found


def test_create_access_token():
    """
    Test JWT token creation with correct payload.
    """
    data = {'sub': 'testuser', 'id': 1, 'role': 'user'}
    expires_delta = timedelta(days=1)  # Token expiration time
    token = create_access_token(data, expires_delta)  # Create access token

    # Decode the token without verifying signature for testing purposes
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})
    assert decoded_token['sub'] == 'testuser'
    assert decoded_token['id'] == 1
    assert decoded_token['role'] == 'user'


@pytest.mark.asyncio
async def test_get_current_user_valid_token(test_user):
    """
    Test retrieving current user with a valid JWT token.
    """
    # Encode token payload with user information
    encode = {'sub': test_user.username, 'id': test_user.id, 'role': test_user.role}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    # Create a test database session
    db = TestingSessionLocal()

    # Get the current user from the token
    user = get_current_user(token=token, db=db)
    assert user == {'id': test_user.id, 'username': test_user.username, 'role': test_user.role}  # Match expected user data


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    """
    Test error handling when JWT token payload is incomplete or invalid.
    """
    # Encode token payload without required fields (e.g., missing 'id' and 'role')
    encode = {'sub': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    # Create a test database session
    db = TestingSessionLocal()

    # Expect an HTTPException due to invalid token payload
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(token=token, db=db)

    # Assert that the exception status code and detail are as expected
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Invalid user'
