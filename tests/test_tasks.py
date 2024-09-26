# test_tasks.py

from fastapi import status  # Import HTTP status codes for response validation
from app.routers.tasks import get_db_session, get_current_user  # Import necessary dependencies
from utils import *  # Import test utilities and fixtures

# Override the dependencies for test isolation
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db_session] = override_get_db


def test_read_all_tasks_authenticated(test_task):
    """
    Test to read all tasks for the authenticated user.
    """
    # Send a GET request to fetch all tasks
    response = client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK  # Assert status code is 200 OK
    assert response.json() == [{'completed': False, 'title': 'Learn to Code',
                                'description': 'Need to learn everyday', 'id': 1,
                                'priority': 5, 'owner_id': 1}]  # Check response content matches expected data


def test_read_one_task_authenticated(test_task):
    """
    Test to read a specific task by its ID for the authenticated user.
    """
    # Send a GET request to fetch a task by ID
    response = client.get("/tasks/1")
    assert response.status_code == status.HTTP_200_OK  # Assert status code is 200 OK
    assert response.json() == {'completed': False, 'title': 'Learn to Code',
                               'description': 'Need to learn everyday', 'id': 1,
                               'priority': 5, 'owner_id': 1}  # Check response content matches expected data


def test_read_one_task_not_found(test_task):
    """
    Test retrieving a non-existent task by ID for the authenticated user.
    """
    # Send a GET request to fetch a non-existent task
    response = client.get("/tasks/99")
    assert response.status_code == status.HTTP_404_NOT_FOUND  # Assert status code is 404 Not Found
    assert response.json() == {'detail': 'Task not found'}  # Verify the correct error message


def test_create_task(test_task):
    """
    Test creating a new task for the authenticated user.
    """
    request_data = {
        'title': 'New Task!',
        'description': 'New Task description',
        'priority': 5,
        'completed': False
    }
    # Send a POST request to create a new task
    response = client.post("/tasks/", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED  # Assert status code is 201 Created

    # Verify that the task has been created in the database
    db = TestingSessionLocal()
    model = db.query(Task).filter(Task.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.completed == request_data.get('completed')


def test_update_task(test_task):
    """
    Test updating an existing task's details.
    """
    request_data = {
        'title': 'Updated Task!',
        'description': 'Updated Task description',
        'priority': 5,
        'completed': True
    }
    # Send a PUT request to update a task
    response = client.put("/tasks/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT  # Assert status code is 204 No Content

    # Verify that the task details have been updated in the database
    db = TestingSessionLocal()
    model = db.query(Task).filter(Task.id == 1).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.completed == request_data.get('completed')


def test_update_task_not_found(test_task):
    """
    Test updating a non-existent task.
    """
    request_data = {
        'title': 'Updated Task!',
        'description': 'Updated Task description',
        'priority': 5,
        'completed': False
    }
    # Send a PUT request to update a non-existent task
    response = client.put("/tasks/99", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND  # Assert status code is 404 Not Found
    assert response.json() == {'detail': 'Task not found'}  # Verify the correct error message


def test_delete_task(test_task):
    """
    Test deleting an existing task by its ID.
    """
    # Send a DELETE request to delete a task
    response = client.delete("/tasks/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT  # Assert status code is 204 No Content

    # Verify that the task has been deleted from the database
    db = TestingSessionLocal()
    model = db.query(Task).filter(Task.id == 1).first()
    assert model is None


def test_delete_task_not_found(test_task):
    """
    Test deleting a non-existent task.
    """
    # Send a DELETE request to delete a non-existent task
    response = client.delete("/tasks/9")
    assert response.status_code == status.HTTP_404_NOT_FOUND  # Assert status code is 404 Not Found
    assert response.json() == {'detail': 'Task not found'}  # Verify the correct error message
