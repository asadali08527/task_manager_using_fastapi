# Import necessary modules and libraries
from typing import Annotated  # Used for type annotations for dependencies

from pydantic import BaseModel, Field  # Pydantic used for data validation and modeling
from sqlalchemy.orm import Session  # ORM session for DB operations
from fastapi import APIRouter, Depends, HTTPException, Path  # FastAPI modules for routing and dependency injection
from starlette import status  # HTTP status codes

from ..models import Task  # Updated from Todos to Task for the new context
from ..database import get_db_session  # Updated to general-purpose DB session dependency
from .authentication import get_current_user  # Dependency to fetch the current authenticated user

# Set up the router for admin operations (renamed to 'manager')
router = APIRouter(
    prefix='/manager',
    tags=['manager']  # Updated tag for better clarity in Swagger docs
)

# Define a dependency to get the database session
db_dependency = Annotated[Session, Depends(get_db_session)]
# Define a dependency to get the current user (ensures user authentication)
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/tasks", status_code=status.HTTP_200_OK)
async def get_all_tasks(user: user_dependency, db: db_dependency):
    """
    Fetch all tasks in the system. Restricted to users with the 'manager' role.

    - **user**: The currently authenticated user information.
    - **db**: Database session.
    """
    # Check if the user has manager privileges
    print(user.get('role'))
    if user is None or user.get('role') != 'manager':
        raise HTTPException(status_code=401, detail='Authentication failed: Only managers are authorized.')

    # Retrieve and return all tasks from the database
    return db.query(Task).all()


@router.delete("/task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(user: user_dependency, db: db_dependency, task_id: int = Path(gt=0)):
    """
    Delete a specific task by its ID. Only users with 'manager' role can perform this action.

    - **task_id**: The ID of the task to delete.
    """
    # Check if the user has manager privileges
    if user is None or user.get('role') != 'manager':
        raise HTTPException(status_code=401, detail='Authentication failed: Only managers are authorized.')

    # Query the task by its ID
    task_model = db.query(Task).filter(Task.id == task_id).first()

    # If the task is not found, raise a 404 error
    if task_model is None:
        raise HTTPException(status_code=404, detail='Task not found')

    # Delete the task and commit the transaction
    db.delete(task_model)
    db.commit()
