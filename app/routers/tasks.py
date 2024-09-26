from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status

from ..models import Task
from ..database import get_db_session
from .authentication import get_current_user

# Router for task-related routes
router = APIRouter(
    prefix='/tasks',
    tags=['tasks']
)

# Dependency for database session
db_dependency = Annotated[Session, Depends(get_db_session)]
# Dependency to get the authenticated user
user_dependency = Annotated[dict, Depends(get_current_user)]


# Schema for creating and updating tasks
class TaskRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    completed: bool = Field(default=False)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_tasks(user: user_dependency, db: db_dependency):
    """
    Retrieve all tasks belonging to the authenticated user.
    """
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    return db.query(Task).filter(Task.owner_id == user.id).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(user: user_dependency, db: db_dependency, task_request: TaskRequest):
    """
    Create a new task for the authenticated user.
    """
    task_model = Task(**task_request.dict(), owner_id=user.id)
    db.add(task_model)
    db.commit()


@router.put("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task(user: user_dependency, db: db_dependency, task_request: TaskRequest, task_id: int = Path(gt=0)):
    """
    Update a task's details based on its ID.
    """
    task_model = db.query(Task).filter(Task.id == task_id, Task.owner_id == user['id']).first()
    if task_model is None:
        raise HTTPException(status_code=404, detail='Task not found')

    for key, value in task_request.dict().items():
        setattr(task_model, key, value)

    db.add(task_model)
    db.commit()


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(user: user_dependency, db: db_dependency, task_id: int = Path(gt=0)):
    """
    Delete a task based on its ID.
    """
    task_model = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if task_model is None:
        raise HTTPException(status_code=404, detail='Task not found')

    db.delete(task_model)
    db.commit()
