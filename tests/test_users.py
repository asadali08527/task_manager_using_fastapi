# test_user_management.py

from utils import *  # Import utility functions and test helpers
from app.routers.users import get_db_session, get_current_user  # Import required dependencies for override
from fastapi import status  # FastAPI status codes for HTTP assertions

# Override the dependencies for testing
app.dependency_overrides[get_db_session] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_user_profile(test_user):
    """
    Test retrieving the profile of the authenticated user.
    """
    # Send a GET request to fetch the user's profile
    response = client.get("/user/")
    assert response.status_code == status.HTTP_200_OK  # Assert that the response status code is 200 OK
    user_data = response.json()
    assert user_data['username'] == 'asad'
    assert user_data['email'] == 'asad@test.com'
    assert user_data['first_name'] == 'asad'
    assert user_data['last_name'] == 'ali'
    assert user_data['role'] == 'admin'
    assert user_data['phone_number'] == '0987654321'


def test_change_password_success(test_user):
    """
    Test successfully changing the user's password.
    """
    # Send a PUT request to change the user's password
    response = client.put("/user/password", json={'current_password': 'testpassword', 'new_password': 'testpassword1'})
    assert response.status_code == status.HTTP_200_OK  # Assert that the response status code is 200 OK


def test_change_password_invalid_current_password(test_user):
    """
    Test changing password with an incorrect current password.
    """
    # Send a PUT request with an incorrect current password
    response = client.put("/user/password", json={'current_password': 'wrongpassword', 'new_password': 'testpassword1'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED  # Assert that the response status code is 401 Unauthorized
    assert response.json() == {'detail': 'Incorrect current password'}  # Validate error message


# If the endpoint for changing phone numbers was in the original `users.py`, and is removed in the updated
# `user_management.py`: You should remove the associated test.
