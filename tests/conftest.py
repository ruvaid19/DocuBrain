import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

@pytest.fixture(autouse=True)
def mock_qdrant_startup():
    """Mock the Qdrant startup check so tests don't require an active connection."""
    with patch("app.main.ensure_collection_exists") as mock_ensure:
        mock_ensure.return_value = None
        yield mock_ensure

@pytest.fixture
def client():
    """Provide a FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client
