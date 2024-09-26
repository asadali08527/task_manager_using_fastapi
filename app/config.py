# config.py - Configuration settings for the application

# Database configuration
# DATABASE_URL is the connection string for the database.
# It can be retrieved from an environment variable for security and flexibility.
# Default to an SQLite database if no environment variable is provided.
DATABASE_URL = 'sqlite:///./tasksapp.db'  # SQLite database URL (local database file)
# DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./tasksapp.db')  # Default to SQLite

# JWT (JSON Web Token) configuration
# SECRET_KEY is the key used for encoding and decoding JWT tokens.
# It's important to use a secure and random key in production environments.
# Ideally, this value should be set through an environment variable for security.
SECRET_KEY = 'your-secure-random-secret-key'  # Replace with a securely generated key from environment variables
# SECRET_KEY = os.getenv('SECRET_KEY', 'your-secure-random-secret-key')  # Use a secure key in production

# ALGORITHM specifies the cryptographic algorithm used for encoding the JWT.
ALGORITHM = 'HS256'  # HMAC with SHA-256 (secure hash algorithm)

# Access token expiration configuration
# This sets the time duration (in minutes) for which the access token is valid.
# For better control and security, it's recommended to retrieve this from an environment variable.
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expires after 30 minutes
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
