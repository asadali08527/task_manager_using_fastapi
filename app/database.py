# Import necessary modules and libraries for SQLAlchemy
from sqlalchemy import create_engine  # Used to create the database engine
from sqlalchemy.orm import sessionmaker  # Creates a configured session class for database operations
from sqlalchemy.ext.declarative import declarative_base  # Base class for defining ORM models

# Import the database URL configuration from the application's config file
from app.config import DATABASE_URL  # Import the database connection URL from config

# Connect to the database specified in the configuration
# `create_engine` is responsible for setting up the database connection.
# The `check_same_thread` argument is set to False to allow multi-threaded applications to work with SQLite.
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

# Create a session factory bound to the engine
# Sessions are used to interact with the database (e.g., query, add, delete data).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the base class for database models
# All ORM models will inherit from `Base`, which includes metadata and mappings.
Base = declarative_base()


# Dependency to get a database session
def get_db_session():
    """
    Dependency function to get a new SQLAlchemy session for interacting with the database.

    Creates a session using `SessionLocal()` and ensures the session is properly closed
    after the request is finished.

    Yields:
    - db (SessionLocal): A database session object.
    """
    # Create a new database session
    db = SessionLocal()
    try:
        # Yield the session to be used in route handlers
        yield db
    finally:
        # Close the session after the request lifecycle is complete to free up resources
        db.close()
