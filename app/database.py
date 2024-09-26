from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import DATABASE_URL  # Importing from config

# Connect to the database specified in the config
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

# Create a sessionmaker bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the base class for the database models
Base = declarative_base()


# Dependency to get a database session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
