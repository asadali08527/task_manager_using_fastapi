
# FastAPI Tutorial: Building a Task Manager Application

## Overview
This tutorial aims to provide an in-depth guide to getting started with FastAPI, a modern, fast (high-performance), web framework for building APIs with Python. We'll walk you through the essential concepts of FastAPI by building a real-world task manager application.

## What We Will Cover
1. **Understanding FastAPI:** What it is, its prerequisites, and why you should use it.
2. **Setting Up the Environment:** Installing necessary libraries and tools.
3. **Creating a Task Manager Application:**
   - **Building CRUD APIs with FastAPI.**
   - **Using Pydantic for data validation and serialization.**
   - **Setting up SQLAlchemy ORM for database operations.**
   - **Handling authentication and authorization.**
   - **Utilizing Alembic for database migrations.**
4. **Testing and Running the Application.**

## Prerequisites
Before diving into FastAPI, it's essential to have:
- **Basic knowledge of Python.**
- **Familiarity with Object-Oriented Programming (OOP).**
- **Some understanding of RESTful APIs (not mandatory but helpful).**

## What is FastAPI?
FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. It's designed to be easy to use and offers automatic interactive documentation for your APIs.

### Why Use FastAPI?
- **Automatic Docs:** FastAPI provides automatic generation of API documentation with **Swagger UI** and **ReDoc**.
- **High Performance:** It's one of the fastest Python frameworks thanks to its use of **ASGI** (Asynchronous Server Gateway Interface).
- **Type Safety:** Enforces type checking with **Pydantic**, which ensures data validation and serialization.
- **Modern Features:** Includes support for WebSockets, Background Tasks, Dependency Injection, OAuth2, and JWT token handling.

### FastAPI vs Flask
| Feature            | FastAPI                          | Flask                   |
|--------------------|----------------------------------|-------------------------|
| **Performance**    | High (async support)             | Medium                  |
| **Type Safety**    | Enforced with Pydantic           | No built-in support     |
| **Automatic Docs** | Yes (Swagger, ReDoc)             | No                      |
| **Best Use Cases** | REST APIs, Microservices         | Small apps, Prototyping |

Use **FastAPI** when you need to build a scalable, high-performance API quickly with automatic documentation and type safety.

## Project Introduction: Task Manager Application
In this tutorial, we will cover various FastAPI concepts using a task manager application. This will include creating users, handling authentication, and performing CRUD operations on tasks.

## Project Setup
### 1. **Setting Up the Environment**
- **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
- **Install FastAPI and Other Dependencies:**
    ```bash
    pip install fastapi uvicorn sqlalchemy pydantic alembic passlib python-jose
    ```

### 2. **Project Structure**
```
task_manager/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── config.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── authentication.py
│   │   ├── tasks.py
│   │   ├── manager.py
│   │   └── users.py
├── alembic/
│   └── versions/
├── alembic.ini
└── README.md
```

### 3. **FastAPI Core Concepts**
**Creating a FastAPI App:**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```
- **`app = FastAPI()`** creates the FastAPI application.
- **Routes** are defined using decorators like `@app.get("/route")`.

## Step-by-Step Implementation

### **1. Configuration File (`config.py`)**
- Stores environment configurations like `DATABASE_URL`, `SECRET_KEY`, and token expiration settings.
- **Key Concepts:** Managing configurations securely, using environment variables.

### **2. Database Setup (`database.py`)**
- **SQLAlchemy ORM:** A library for connecting to and interacting with databases in Python.
- **Engine and Session:** Create a `SessionLocal` to interact with the database and an `engine` to connect.
- **FastAPI Dependency:** Uses a `get_db_session` function to inject database sessions into route handlers.

**Example:**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

### **3. Models (`models.py`)**
- **Pydantic Models vs SQLAlchemy Models:**
  - **Pydantic** is used for request/response data validation.
  - **SQLAlchemy** defines how data is stored in the database.

**Example User Model:**
```python
from app.database import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
```

### **4. Routers & CRUD Operations (`routers/`)**
Each file in `routers/` defines endpoints for a specific module.
- **Authentication Router (`authentication.py`):** Handles user registration and JWT-based authentication.
- **Tasks Router (`tasks.py`):** Handles CRUD operations for tasks (Create, Read, Update, Delete).
- **Manager Router (`manager.py`):** Allows manager-specific actions (e.g., view all tasks).
- **Users Router (`users.py`):** Allows users to update their profile or change their password.

### **5. JWT Authentication**
**Library:** `python-jose`
- **Purpose:** Securely encode and decode JSON Web Tokens.
- **Usage:** Used in `authentication.py` for user authentication, ensuring that users can only access their own data.

### **6. Using Alembic for Database Migrations**
- **Why Alembic?** To handle database schema changes, such as creating tables or modifying columns without losing data.
- **Initialize Alembic:**
    ```bash
    alembic init alembic
    ```
- **Configure `alembic.ini`:** Update `sqlalchemy.url` with `DATABASE_URL` from `config.py`.
- **Create a Migration Script:**
    ```bash
    alembic revision --autogenerate -m "Initial migration"
    ```
- **Apply Migrations:**
    ```bash
    alembic upgrade head
    ```

### **7. Running the Application**
- **Start the FastAPI server:**
    ```bash
    uvicorn app.main:app --reload
    ```
- By default, the server will run on `http://127.0.0.1:8000`.

### **8. Automatic API Documentation**
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) - Interactive API documentation.
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) - Alternative API documentation.

## Sample APIs
### 1. **Register a User**
- **POST /auth/**  
**Request Body:**
```json
{
    "username": "user1",
    "email": "user1@example.com",
    "password": "password"
}
```

### 2. **Create a Task**
- **POST /tasks/**  
**Request Body:**
```json
{
    "title": "Buy groceries",
    "description": "Milk, Bread, Eggs",
    "priority": 2
}
```

**Response:**
```json
{
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, Bread, Eggs",
    "priority": 2,
    "completed": false
}
```

### 3. **Update Task**
- **PUT /tasks/{task_id}**  
**Request Body:**
```json
{
    "title": "Buy groceries and fruits",
    "priority": 1,
    "completed": true
}
```

### 4. **Delete Task**
- **DELETE /tasks/{task_id}**  
**Response:** Status Code 204 No Content

## Final Notes
- **Third-Party Libraries Used:**
  - **`fastapi`:** Web framework for building APIs.
  - **`uvicorn`:** ASGI server to run FastAPI applications.
  - **`sqlalchemy`:** ORM for database interactions.
  - **`pydantic`:** Data validation and serialization.
  - **`alembic`:** Database migrations.
  - **`passlib`:** Secure password hashing.
  - **`python-jose`:** Handling JWT tokens for authentication.

This tutorial should give you a comprehensive understanding of building a FastAPI application while focusing on practical implementation. Explore, experiment, and happy coding!
