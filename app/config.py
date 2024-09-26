# config.py

# Database configuration
# DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./tasksapp.db')  # Default to SQLite
DATABASE_URL = 'sqlite:///./tasksapp.db'

# JWT Secret Key & Algorithm
# SECRET_KEY = os.getenv('SECRET_KEY', 'your-secure-random-secret-key')  # Use a secure key in production
SECRET_KEY = 'your-secure-random-secret-key'  # Replace with an environment variable in production
ALGORITHM = 'HS256'

# Token Expiration Configuration
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
ACCESS_TOKEN_EXPIRE_MINUTES = 30
