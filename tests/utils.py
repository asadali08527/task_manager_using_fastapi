from sqlalchemy import create_engine, text  # Import engine and SQL text functionalities for database operations
from sqlalchemy.orm import sessionmaker  # Import sessionmaker for database sessions
from sqlalchemy.pool import StaticPool  # Use StaticPool for single-threaded tests
from fastapi.testclient import TestClient  # Import FastAPI's test client for testing
import pytest  # Import pytest for writing test cases

from app.database import Base  # Import Base for model metadata
from app.models import Task, User  # Import Task and User models (updated from Todos and Users)
from app.main import app  # Import the main FastAPI app for testing
from app.routers.authentication import bcrypt_context  # Import bcrypt context for password hashing

# Database URL for testing using an SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

# Create an engine for the test database using SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},  # Specific to SQLite for allowing multiple threads
    poolclass=StaticPool,  # Use StaticPool to ensure connections aren't recycled across tests
)

# Create a session factory for the test database
TestingSessionLocal = sessionmaker(autocommit=False, bind=engine)

# Create all tables in the test database based on model metadata
Base.metadata.create_all(bind=engine)


# Override the database session dependency to use the test session
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db  # Provide the database session to the test
    finally:
        db.close()  # Ensure the session is closed after each test


# Override the current user dependency to return a mock authenticated user
def override_get_current_user():
    # Return a mock user with username 'asad', user_id 1, and role 'admin'
    return {'username': 'asad', 'id': 1, 'role': 'manager'}


# Initialize a test client for the FastAPI app
client = TestClient(app)


# Pytest fixture to provide a test Task object
@pytest.fixture
def test_task():
    """
    Fixture to create and clean up a Task for testing.
    """
    # Create a Task object for testing
    task = Task(
        title="Learn to Code",
        description="Need to learn everyday",
        priority=5,
        completed=False,
        owner_id=1
    )
    db = TestingSessionLocal()
    db.add(task)  # Add the task to the test session
    db.commit()  # Commit the task to the test database
    yield task  # Yield the task for the test function to use

    # Cleanup the Task from the test database after the test is completed
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM tasks;"))
        # connection.commit()


# Pytest fixture to provide a test User object
@pytest.fixture
def test_user():
    """
    Fixture to create and clean up a User for testing.
    """
    # Create a User object for testing
    import uuid
    # Generate a unique username and email for each test run
    unique_suffix = uuid.uuid4()
    user_username = f"testuser_{unique_suffix}"
    user_email = f"{user_username}@test.com"
    user = User(
        username=user_username,
        email=user_email,
        first_name='asad',
        last_name='ali',
        hashed_password=bcrypt_context.hash('testpassword'),
        role='admin',
        phone_number='0987654321',
    )
    db = TestingSessionLocal()
    db.add(user)  # Add the user to the test session
    db.commit()  # Commit the user to the test database
    yield user  # Yield the user for the test function to use

    # Cleanup the User from the test database after the test is completed
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        # connection.commit()
