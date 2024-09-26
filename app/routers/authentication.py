# Standard library imports for time calculations
from datetime import timedelta, \
    datetime  # timedelta for specifying token expiration, datetime for current time operations

# Type hinting and dependency annotations
from typing import Annotated  # Annotated allows combining a type with additional metadata

# FastAPI imports for creating API routes, handling dependencies, and raising HTTP exceptions
from fastapi import APIRouter, Depends, HTTPException

# Pydantic for defining data models for request/response validation
from pydantic import BaseModel

# SQLAlchemy for ORM database session management
from sqlalchemy.orm import Session

# FastAPI's OAuth2 modules for form authentication and bearer token authentication
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

# JWT handling using the `python-jose` library for encoding and decoding tokens
from jose import jwt, JWTError

# Local application imports
from ..database import get_db_session  # Function to get the current DB session (dependency injection)
from ..models import User  # ORM model representing the User table
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES  # Configuration for JWT and token expiration
from passlib.context import CryptContext  # For hashing and verifying user passwords using bcrypt

# Create a router instance to handle all authentication-related endpoints
router = APIRouter(
    prefix='/auth',  # All routes in this router will be prefixed with '/auth'
    tags=['authentication']  # Tags help organize the API documentation
)

# Set up password hashing context using bcrypt
bcrypt_context = CryptContext(schemes=['bcrypt'],
                              deprecated='auto')  # Allows for securely hashing and verifying passwords

# OAuth2PasswordBearer is used for retrieving the bearer token from incoming requests
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')  # `tokenUrl` is the endpoint where clients can get a token

# Annotated dependency for getting a DB session for each request
db_dependency = Annotated[Session, Depends(get_db_session)]


# Request schema for creating a new user, used to validate incoming request data for user creation
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

    class Config:
        arbitrary_types_allowed = True  # Allows arbitrary (non-Pydantic) types in the model, like `Session`


# Response schema for token generation, representing the structure of the access token response
class Token(BaseModel):
    access_token: str  # The JWT token string
    token_type: str  # Type of token (usually "bearer")


def authenticate_user(username: str, password: str, db: Session):
    """
    Authenticate user by verifying their password against the stored hashed password in the database.

    Parameters:
    - username (str): Username of the user attempting to log in.
    - password (str): Plain text password provided by the user.
    - db (Session): The current database session.

    Returns:
    - User object if authentication is successful; None otherwise.
    """
    # Retrieve user from the database by username
    user = db.query(User).filter(User.username == username).first()
    # Verify password against hashed password stored in the database
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    """
    Create a JWT token for authenticated users with an expiration time.

    Parameters:
    - data (dict): User data to encode in the JWT.
    - expires_delta (timedelta): Time duration after which the token expires.

    Returns:
    - Encoded JWT token string.
    """
    # Create a copy of the data and add expiration information
    encode = data.copy()
    expire = datetime.utcnow() + expires_delta  # Calculate the expiration time
    encode.update({"exp": expire})
    # Encode the token with the secret key and algorithm
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    """
    Decode JWT token to retrieve user information from the database.

    Parameters:
    - token (str): JWT access token provided in the request header.
    - db (Session): The current database session.

    Returns:
    - Dictionary with user information (id, username, role) if token is valid.

    Raises:
    - HTTPException: If token is invalid or user is not found.
    """
    try:
        # Decode JWT token to extract the payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Retrieve user from the database based on username in the payload
        user = db.query(User).filter(User.username == payload.get("sub")).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid user")
        # Return a dictionary of user information
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/", response_model=None, status_code=201)
def create_user(user_request: CreateUserRequest, db: db_dependency):
    """
    Register a new user account in the database.

    Parameters:
    - user_request (CreateUserRequest): The data model for creating a user, validated by Pydantic.
    - db (Session): The current database session.

    Process:
    - Hashes the user's password before saving it to the database.
    - Adds a new user record to the database.
    """
    # Hash the user's plain text password for secure storage
    hashed_password = bcrypt_context.hash(user_request.password)
    # Create a new User model instance
    user_model = User(
        username=user_request.username,
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=hashed_password,
        role=user_request.role,
        phone_number=user_request.phone_number
    )
    # Add and commit the new user to the database
    db.add(user_model)
    db.commit()


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    """
    Handle user login and return an access token if authentication is successful.

    Parameters:
    - form_data (OAuth2PasswordRequestForm): The OAuth2 form data containing `username` and `password`.
    - db (Session): The current database session.

    Process:
    - Authenticates the user.
    - Creates and returns an access token.

    Returns:
    - JSON response with access token and token type.

    Raises:
    - HTTPException: If authentication fails.
    """
    # Authenticate the user with provided credentials
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Calculate token expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Create the JWT access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    # Return the token and its type (bearer)
    return {"access_token": access_token, "token_type": "bearer"}
