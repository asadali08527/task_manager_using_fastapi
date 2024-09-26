# Import base class for models and necessary SQLAlchemy modules
from app.database import Base  # Base class from which all ORM models will inherit
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey  # SQLAlchemy modules for defining ORM mappings


# Define the User model for storing user-related information
class User(Base):
    __tablename__ = 'users'  # Name of the table in the database

    # Unique ID for each user (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    # Username of the user, must be unique and non-nullable
    username = Column(String, unique=True, nullable=False)
    # User's email address, must be unique and non-nullable
    email = Column(String, unique=True, nullable=False)
    # User's first name, non-nullable
    first_name = Column(String, nullable=False)
    # User's last name, non-nullable
    last_name = Column(String, nullable=False)
    # Hashed password for secure storage, non-nullable
    hashed_password = Column(String, nullable=False)
    # Status indicating if the user's account is active (default is True)
    is_active = Column(Boolean, default=True)
    # Role of the user, e.g., 'user' or 'manager'
    role = Column(String, nullable=False)
    # Optional phone number field
    phone_number = Column(String)

    def __repr__(self):
        """
        Representation method for User objects, useful for debugging.

        Returns:
        - A string containing the username, email, and role of the user.
        """
        return f"<User(username={self.username}, email={self.email}, role={self.role})>"


# Define the Task model for storing task-related information
class Task(Base):
    __tablename__ = 'tasks'  # Name of the table in the database

    # Unique ID for each task (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    # Title of the task, non-nullable
    title = Column(String, nullable=False)
    # Description of the task, nullable
    description = Column(String)
    # Priority of the task (1 to 5 scale), nullable
    priority = Column(Integer)
    # Completion status of the task (default is False)
    completed = Column(Boolean, default=False)
    # Foreign key referencing the user who owns the task
    owner_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        """
        Representation method for Task objects, useful for debugging.

        Returns:
        - A string containing the title, priority, and completion status of the task.
        """
        return f"<Task(title={self.title}, priority={self.priority}, completed={self.completed})>"
