# Import necessary modules and libraries
from typing import Annotated  # Used for type annotations and dependency metadata

from fastapi import APIRouter, Depends, \
    HTTPException  # FastAPI modules for routing, dependencies, and exception handling
from pydantic import BaseModel, Field  # Pydantic models for data validation and serialization
from sqlalchemy.orm import Session  # ORM session for database interactions
from passlib.context import CryptContext  # Password hashing and verification utility

# Local application imports
from ..database import get_db_session  # Function to get a database session (dependency injection)
from ..models import User  # ORM model representing the User entity in the database
from .authentication import get_current_user  # Function to retrieve the current authenticated user

# Initialize the router for user management routes
router = APIRouter(
    prefix='/user',  # Prefix for all routes in this router
    tags=['user']  # Tag for grouping routes in API documentation
)

# Dependency for injecting a database session into route handlers
db_dependency = Annotated[Session, Depends(get_db_session)]
# Dependency for injecting the current authenticated user's information
user_dependency = Annotated[dict, Depends(get_current_user)]

# Set up password hashing context using bcrypt for secure password storage and verification
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# Pydantic schema for password change request
class UserVerification(BaseModel):
    current_password: str  # Current password provided by the user for verification
    new_password: str = Field(min_length=6)  # New password with a minimum length of 6 characters


@router.get("/", status_code=200)
def get_user_profile(user: user_dependency, db: db_dependency):
    """
    Retrieve the profile of the authenticated user.

    Parameters:
    - **user**: The authenticated user's data (as a dictionary with id, username, role).
    - **db**: The current database session for querying the user.

    Returns:
    - User object representing the authenticated user's profile.

    Raises:
    - HTTP 401: If the user is not authenticated.
    """
    # Query and return the authenticated user's profile from the database
    return db.query(User).filter(User.id == user['id']).first()


@router.put("/password", status_code=200)
def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    """
    Update the authenticated user's password.

    Parameters:
    - **user**: The authenticated user's data (as a dictionary with id, username, role).
    - **db**: The current database session for updating the user's password.
    - **user_verification**: Data for verifying and updating the password, validated using the `UserVerification` model.

    Process:
    - Verifies that the provided current password matches the stored hashed password.
    - Hashes the new password and updates it in the database.

    Raises:
    - HTTP 401: If the provided current password is incorrect.
    """
    # Retrieve the user model from the database based on user ID
    user_model = db.query(User).filter(User.id == user['id']).first()

    # Verify that the provided current password matches the stored hashed password
    if not bcrypt_context.verify(user_verification.current_password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect current password')

    # Hash the new password and update the user's password in the database
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    # Save the updated user model to the database
    db.add(user_model)
    db.commit()
