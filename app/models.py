from app.database import Base  # Import base class for models
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey  # SQLAlchemy for ORM mappings


# User model to store user-related information
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)  # Unique ID for each user
    username = Column(String, unique=True, nullable=False)  # User's unique username
    email = Column(String, unique=True, nullable=False)  # User's email, must be unique
    first_name = Column(String, nullable=False)  # First name of the user
    last_name = Column(String, nullable=False)  # Last name of the user
    hashed_password = Column(String, nullable=False)  # Encrypted password
    is_active = Column(Boolean, default=True)  # Active status for the user account
    role = Column(String, nullable=False)  # User's role, e.g., 'user' or 'manager'
    phone_number = Column(String)  # Optional phone number

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, role={self.role})>"


# Task model to store tasks related to users
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)  # Unique ID for each task
    title = Column(String, nullable=False)  # Title of the task
    description = Column(String)  # Task description
    priority = Column(Integer)  # Task priority (1 to 5 scale)
    completed = Column(Boolean, default=False)  # Status of task completion
    owner_id = Column(Integer, ForeignKey('users.id'))  # Owner's user ID, foreign key reference to User table

    def __repr__(self):
        return f"<Task(title={self.title}, priority={self.priority}, completed={self.completed})>"
