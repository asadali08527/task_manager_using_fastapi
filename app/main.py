from fastapi import FastAPI  # FastAPI application instance creation
from app.models import Base  # Importing Base class for models
from app.database import engine  # Import the engine to bind to models
from app.routers import authentication, tasks, manager, users  # Updated router imports

# Create FastAPI instance
app = FastAPI(
    title="Taskify API",
    description="An API for managing tasks and user accounts",
    version="1.0.0"
)

# Create the database tables based on the models
Base.metadata.create_all(bind=engine)


@app.get("/health", status_code=200)
def health_check():
    """
    Health check endpoint to confirm that the API is running.
    """
    return {'status': 'healthy'}


# Include routers for different modules
app.include_router(authentication.router)
app.include_router(tasks.router)
app.include_router(manager.router)
app.include_router(users.router)
