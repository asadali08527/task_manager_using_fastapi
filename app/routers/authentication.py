from datetime import timedelta, datetime  # Used for token expiration calculations
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException  # FastAPI modules for route creation and dependency injection
from pydantic import BaseModel  # For request/response data validation
from sqlalchemy.orm import Session  # ORM session for DB operations
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer  # OAuth2 modules for authentication
from jose import jwt, JWTError  # JWT library for creating and decoding tokens

from ..database import get_db_session  # Database session dependency
from ..models import User  # Import User model
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES  # Config for security
from passlib.context import CryptContext  # For password hashing

# Router for authentication-related routes
router = APIRouter(
    prefix='/auth',
    tags=['authentication']
)

# Setup password hashing context using bcrypt
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# OAuth2 password bearer setup for token retrieval
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# Dependency for database session
db_dependency = Annotated[Session, Depends(get_db_session)]


# Request schema for creating a new user
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

    class Config:
        arbitrary_types_allowed = True


# Response schema for token
class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db: Session):
    """
    Authenticate user by verifying password against stored hash.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    """
    Create a JWT token for authenticated users.
    """
    encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    """
    Decode JWT token to retrieve user information.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.username == payload.get("sub")).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid user")
        # Return a dictionary instead of the ORM object
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
    Register a new user account.
    """
    hashed_password = bcrypt_context.hash(user_request.password)
    user_model = User(
        username=user_request.username,
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=hashed_password,
        role=user_request.role,
        phone_number=user_request.phone_number
    )
    db.add(user_model)
    db.commit()


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    """
    Handle user login and return access token.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
