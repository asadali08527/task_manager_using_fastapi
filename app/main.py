# Import necessary modules from FastAPI
from fastapi import FastAPI  # FastAPI class for creating an application instance

# Local application imports
from app.models import Base  # Base class for defining all SQLAlchemy models
from app.database import engine  # Database engine to bind models and handle database operations
from app.routers import authentication, tasks, manager, users  # Import routers for different application modules

# Create a FastAPI instance
app = FastAPI(
    title="Taskify API",  # Name of the API
    description="An API for managing tasks and user accounts",  # Description shown in API docs
    version="1.0.0"  # Version of the API
)

# Create all the database tables based on the SQLAlchemy models
# This will create tables if they don't exist, based on the `Base` metadata
Base.metadata.create_all(bind=engine)


@app.get("/health", status_code=200)
def health_check():
    """
    Health check endpoint to confirm that the API is running.

    Returns:
    - A JSON response indicating the health status of the API.
    """
    return {'status': 'healthy'}


# Include routers for different modules to handle various endpoints
# Each router is responsible for a specific section of the API (e.g., authentication, tasks)
app.include_router(authentication.router)  # Handles authentication-related routes
app.include_router(tasks.router)  # Handles task-related routes
app.include_router(manager.router)  # Handles manager-related routes
app.include_router(users.router)  # Handles user management-related routes
