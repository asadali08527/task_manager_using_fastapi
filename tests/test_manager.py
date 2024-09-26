# test_manager.py

from utils import *  # Import utility functions for setting up test environment
from app.routers.manager import get_db_session, get_current_user  # Import necessary dependencies for override
from fastapi import status
from app.models import Task  # Import Task model for database verification

# Override the dependencies for test isolation
app.dependency_overrides[get_db_session] = override_get_db  # Override the database session dependency
app.dependency_overrides[get_current_user] = override_get_current_user  # Override the current user dependency


def test_manager_read_all_authenticated(test_task):
    """
    Test to read all tasks when the user is authenticated as a 'manager'.
    """
    # Send a GET request to fetch all tasks
    response = client.get("/manager/tasks")
    assert response.status_code == status.HTTP_200_OK  # Assert that the response status code is 200 OK
    assert response.json() == [{'completed': False, 'title': 'Learn to Code',
                                'description': 'Need to learn everyday',
                                'id': 1, 'priority': 5, 'owner_id': 1}]  # Check if returned tasks match expected data


def test_manager_delete_task(test_task):
    """
    Test to delete a specific task by its ID when the user is authenticated as a 'manager'.
    """
    # Send a DELETE request to delete the task with ID 1
    response = client.delete("/manager/task/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT  # Assert that the response status code is 204 No Content
    db = TestingSessionLocal()
    model = db.query(Task).filter(Task.id == 1).first()
    assert model is None  # Verify that the task has been deleted from the database


def test_manager_delete_task_not_found(test_task):
    """
    Test to delete a task that does not exist when the user is authenticated as a 'manager'.
    """
    # Send a DELETE request to delete a non-existent task (ID 99)
    response = client.delete("/manager/task/99")
    assert response.status_code == status.HTTP_404_NOT_FOUND  # Assert that the response status code is 404 Not Found
    assert response.json() == {'detail': 'Task not found'}  # Check if the error message is as expected
