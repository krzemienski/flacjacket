import os
import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    # Setup app context
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='session')
def client(app):
    """Test client for the application."""
    return app.test_client()

@pytest.fixture(scope='session')
def runner(app):
    """Test CLI runner for the application."""
    return app.test_cli_runner()
