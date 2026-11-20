"""
Pytest Configuration and Fixtures
Sets up an isolated in-memory test database for all test runs.
"""

import sys
from pathlib import Path
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from models import db, Task


@pytest.fixture
def app():
    """Create and configure a Flask application instance for testing."""
    flask_app = create_app('testing')
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client fixture for sending requests to the Flask test app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner fixture for testing Flask custom CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def sample_task(app):
    """Fixture providing a saved sample task in the test database."""
    with app.app_context():
        task = Task(
            title="Setup Jenkins CI/CD Pipeline",
            description="Integrate automated tests and Docker build stages",
            priority="High",
            status="Pending"
        )
        db.session.add(task)
        db.session.commit()
        # Refresh to ensure id is loaded
        db.session.refresh(task)
        return task.to_dict()
