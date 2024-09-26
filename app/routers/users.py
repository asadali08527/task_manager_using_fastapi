from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..database import get_db_session
from ..models import User
from .authentication import get_current_user

# Router for user management
router = APIRouter(
    prefix='/user',
    tags=['user']
)

# Dependency for database session
db_dependency = Annotated[Session, Depends(get_db_session)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# Password hashing context
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# Schema for password change request
class UserVerification(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


@router.get("/", status_code=200)
def get_user_profile(user: user_dependency, db: db_dependency):
    """
    Retrieve the profile of the authenticated user.
    """
    return db.query(User).filter(User.id == user['id']).first()


@router.put("/password", status_code=200)
def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    """
    Update the authenticated user's password.
    """
    user_model = db.query(User).filter(User.id == user['id']).first()
    if not bcrypt_context.verify(user_verification.current_password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect current password')

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
