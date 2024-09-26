# Import necessary modules and libraries
from typing import Annotated  # Used for type annotations and dependency metadata

from pydantic import BaseModel, Field  # Pydantic models for data validation and serialization
from sqlalchemy.orm import Session  # ORM session for database interactions
from fastapi import APIRouter, Depends, HTTPException, \
    Path  # FastAPI modules for routing, dependencies, and exception handling
from starlette import status  # Standard HTTP status codes

# Local application imports
from ..models import Task  # ORM model representing a task in the database
from ..database import get_db_session  # Function to get a database session (dependency injection)
from .authentication import get_current_user  # Function to retrieve the current authenticated user

# Initialize the router for task-related routes
router = APIRouter(
    prefix='/tasks',  # Prefix for all routes in this router
    tags=['tasks']  # Tag for grouping routes in API documentation
)

# Dependency for injecting a database session into route handlers
db_dependency = Annotated[Session, Depends(get_db_session)]
# Dependency for injecting the current authenticated user's information
user_dependency = Annotated[dict, Depends(get_current_user)]


# Pydantic schema for creating and updating tasks
class TaskRequest(BaseModel):
    title: str = Field(min_length=3)  # Task title, minimum length of 3 characters
    description: str = Field(min_length=3, max_length=100)  # Task description, length between 3 and 100 characters
    priority: int = Field(gt=0, lt=6)  # Task priority, must be between 1 and 5
    completed: bool = Field(default=False)  # Task completion status, defaults to False


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_tasks(user: user_dependency, db: db_dependency):
    """
    Retrieve all tasks belonging to the authenticated user.

    Parameters:
    - **user**: The authenticated user's data (as a dictionary with id, username, role).
    - **db**: The current database session for querying tasks.

    Returns:
    - A list of `Task` objects that belong to the authenticated user.

    Raises:
    - HTTP 401: If the user is not authenticated.
    """
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    # Query and return all tasks associated with the authenticated user
    return db.query(Task).filter(Task.owner_id == user['id']).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(user: user_dependency, db: db_dependency, task_request: TaskRequest):
    """
    Create a new task for the authenticated user.

    Parameters:
    - **user**: The authenticated user's data (as a dictionary with id, username, role).
    - **db**: The current database session for saving the new task.
    - **task_request**: Data for the new task, validated using the `TaskRequest` model.

    Process:
    - Creates a new `Task` object with the provided details.
    - Saves the new task to the database.

    Raises:
    - HTTP 401: If the user is not authenticated.
    """
    # Create a new `Task` object with the request data and the user's ID as the owner
    task_model = Task(**task_request.dict(), owner_id=user['id'])
    # Add the new task to the session and commit it to the database
    db.add(task_model)
    db.commit()


@router.put("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task(user: user_dependency, db: db_dependency, task_request: TaskRequest, task_id: int = Path(gt=0)):
    """
    Update a task's details based on its ID.

    Parameters:
    - **user**: The authenticated user's data (as a dictionary with id, username, role).
    - **db**: The current database session for updating the task.
    - **task_request**: Data to update the task, validated using the `TaskRequest` model.
    - **task_id**: The ID of the task to be updated (must be greater than 0).

    Process:
    - Finds the task by its ID and the user's ID.
    - Updates the task's details.

    Raises:
    - HTTP 404: If the task is not found.
    """
    # Query the task from the database based on task ID and user's ownership
    task_model = db.query(Task).filter(Task.id == task_id, Task.owner_id == user['id']).first()

    # If task is not found, raise a 404 HTTP exception
    if task_model is None:
        raise HTTPException(status_code=404, detail='Task not found')

    # Update the task's fields with the new values from `task_request`
    for key, value in task_request.dict().items():
        setattr(task_model, key, value)

    # Add the updated task to the session and commit changes to the database
    db.add(task_model)
    db.commit()


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(user: user_dependency, db: db_dependency, task_id: int = Path(gt=0)):
    """
    Delete a task based on its ID.

    Parameters:
    - **user**: The authenticated user's data (as a dictionary with id, username, role).
    - **db**: The current database session for deleting the task.
    - **task_id**: The ID of the task to be deleted (must be greater than 0).

    Process:
    - Finds the task by its ID and the user's ID.
    - Deletes the task from the database.

    Raises:
    - HTTP 404: If the task is not found.
    """
    # Query the task from the database based on task ID and user's ownership
    task_model = db.query(Task).filter(Task.id == task_id, Task.owner_id == user['id']).first()

    # If task is not found, raise a 404 HTTP exception
    if task_model is None:
        raise HTTPException(status_code=404, detail='Task not found')

    # Delete the task and commit the transaction to the database
    db.delete(task_model)
    db.commit()


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task(user: user_dependency, db: db_dependency, task_id: int = Path(gt=0)):
    """
    Get a task's details based on its ID.

    Parameters:
    - **user**: The authenticated user's data (as a dictionary with id, username, role).
    - **db**: The current database session for updating the task.
    - **task_request**: Data to update the task, validated using the `TaskRequest` model.
    - **task_id**: The ID of the task to be updated (must be greater than 0).

    Process:
    - Finds the task by its ID and the user's ID.

    Raises:
    - HTTP 404: If the task is not found.
    """
    # Query the task from the database based on task ID and user's ownership
    task_model = db.query(Task).filter(Task.id == task_id, Task.owner_id == user['id']).first()

    # If task is not found, raise a 404 HTTP exception
    if task_model is None:
        raise HTTPException(status_code=404, detail='Task not found')

    return task_model
