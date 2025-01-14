import pytest
from app import create_app
from app.extensions import db
from app.models import Analysis, Track
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_start_analysis(client):
    # Test starting a new analysis
    response = client.post('/api/analyze', json={
        'url': 'https://www.youtube.com/watch?v=test'
    })
    assert response.status_code == 202
    data = response.get_json()
    assert data['url'] == 'https://www.youtube.com/watch?v=test'
    assert data['status'] == 'pending'

def test_get_analysis(client):
    # Create a test analysis
    analysis = Analysis(url='https://test.com/audio')
    db.session.add(analysis)
    db.session.commit()

    # Test getting the analysis
    response = client.get(f'/api/analysis/{analysis.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['url'] == 'https://test.com/audio'

def test_list_analyses(client):
    # Create test analyses
    analyses = [
        Analysis(url='https://test.com/1'),
        Analysis(url='https://test.com/2')
    ]
    db.session.add_all(analyses)
    db.session.commit()

    # Test listing all analyses
    response = client.get('/api/analysis')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2

def test_get_track(client):
    # Create a test analysis and track
    analysis = Analysis(url='https://test.com/audio')
    db.session.add(analysis)
    db.session.commit()

    track = Track(
        analysis_id=analysis.id,
        title='Test Track',
        artist='Test Artist',
        start_time=0.0,
        end_time=60.0,
        confidence=0.9
    )
    db.session.add(track)
    db.session.commit()

    # Test getting the track
    response = client.get(f'/api/tracks/{track.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Test Track'
    assert data['artist'] == 'Test Artist'
