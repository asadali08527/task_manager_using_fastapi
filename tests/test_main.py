# test_main.py

from fastapi.testclient import TestClient  # Import TestClient for testing FastAPI applications
from app.main import app  # Import the main FastAPI app
from fastapi import status  # Import status codes for HTTP assertions

# Initialize the test client with the FastAPI app
client = TestClient(app)


def test_health_check():
    """
    Test the health check endpoint to ensure the API is running.
    """
    # Send a GET request to the /health endpoint
    response = client.get("/health")
    # Assert that the response status code is 200 OK
    assert response.status_code == status.HTTP_200_OK
    # Assert that the response JSON is as expected
    assert response.json() == {'status': 'healthy'}
