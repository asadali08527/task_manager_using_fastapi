# Import necessary modules and libraries
from typing import Annotated  # Used for type annotations and dependency injection metadata

from pydantic import BaseModel, Field  # Pydantic models for data validation and modeling
from sqlalchemy.orm import Session  # ORM session for database operations
from fastapi import APIRouter, Depends, HTTPException, \
    Path  # FastAPI modules for routing, dependencies, and exception handling
from starlette import status  # Standard HTTP status codes

# Import local modules and dependencies
from ..models import Task  # ORM model representing the Task entity in the database
from ..database import get_db_session  # Function to get a database session (dependency injection)
from .authentication import get_current_user  # Authentication function to get the current authenticated user

# Set up the router for manager operations
router = APIRouter(
    prefix='/manager',  # Prefix for all routes in this router
    tags=['manager']  # Tag for organizing routes in the API documentation
)

# Dependency for getting a database session (injected into route handlers)
db_dependency = Annotated[Session, Depends(get_db_session)]
# Dependency for getting the authenticated user (ensures that the user is logged in)
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/tasks", status_code=status.HTTP_200_OK)
async def get_all_tasks(user: user_dependency, db: db_dependency):
    """
    Fetch all tasks in the system. Restricted to users with the 'manager' role.

    Parameters:
    - **user**: The currently authenticated user information (dict with id, username, role).
    - **db**: The current database session for querying tasks.

    Returns:
    - List of all `Task` objects in the database.

    Raises:
    - HTTP 401: If the user is not authorized to access this resource.
    """
    # Debugging line to print the user's role to the console
    print(user.get('role'))

    # Check if the user has the 'manager' role to access all tasks
    if user is None or user.get('role') != 'manager':
        raise HTTPException(status_code=401, detail='Authentication failed: Only managers are authorized.')

    # Retrieve and return all tasks from the database
    return db.query(Task).all()


@router.delete("/task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(user: user_dependency, db: db_dependency, task_id: int = Path(gt=0)):
    """
    Delete a specific task by its ID. Only users with the 'manager' role can perform this action.

    Parameters:
    - **user**: The currently authenticated user information (dict with id, username, role).
    - **db**: The current database session for querying and deleting tasks.
    - **task_id**: The ID of the task to be deleted (must be greater than 0).

    Returns:
    - HTTP 204: If the task is successfully deleted.

    Raises:
    - HTTP 401: If the user is not authorized to delete tasks.
    - HTTP 404: If the task with the given ID is not found.
    """
    # Check if the user has the 'manager' role to delete tasks
    if user is None or user.get('role') != 'manager':
        raise HTTPException(status_code=401, detail='Authentication failed: Only managers are authorized.')

    # Query the database for the task with the given ID
    task_model = db.query(Task).filter(Task.id == task_id).first()

    # If the task is not found, raise a 404 HTTP exception
    if task_model is None:
        raise HTTPException(status_code=404, detail='Task not found')

    # Delete the task and commit the transaction to the database
    db.delete(task_model)
    db.commit()
