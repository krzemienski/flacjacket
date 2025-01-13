import json
import pytest
from app import create_app

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def auth_token(client):
    """Get authentication token."""
    response = client.post('/api/auth/login', json={
        'username': 'test_user',
        'password': 'test_password'
    })
    return json.loads(response.data)['access_token']

def test_analyze_endpoint(client, auth_token):
    """Test the analysis endpoint."""
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.post('/api/analysis', json={
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'source': 'youtube'
    }, headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'id' in data
    assert 'status' in data

def test_analysis_status_endpoint(client, auth_token):
    """Test getting analysis status."""
    # First create an analysis
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.post('/api/analysis', json={
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'source': 'youtube'
    }, headers=headers)
    analysis_id = json.loads(response.data)['id']
    
    # Then check its status
    response = client.get(f'/api/analysis/{analysis_id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert 'results' in data

def test_tracks_endpoint(client, auth_token):
    """Test getting track details."""
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    # First create and complete an analysis
    response = client.post('/api/analysis', json={
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'source': 'youtube'
    }, headers=headers)
    analysis_id = json.loads(response.data)['id']
    
    # Wait for analysis to complete
    import time
    max_wait = 60  # seconds
    while max_wait > 0:
        response = client.get(f'/api/analysis/{analysis_id}', headers=headers)
        if json.loads(response.data)['status'] == 'completed':
            break
        time.sleep(1)
        max_wait -= 1
    
    # Get tracks from the analysis
    response = client.get(f'/api/tracks/{analysis_id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    if len(data) > 0:
        track = data[0]
        assert 'id' in track
        assert 'title' in track
        assert 'start_time' in track
        assert 'end_time' in track

def test_track_download_endpoint(client, auth_token):
    """Test downloading a track."""
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    # First create and complete an analysis
    response = client.post('/api/analysis', json={
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'source': 'youtube'
    }, headers=headers)
    analysis_id = json.loads(response.data)['id']
    
    # Wait for analysis to complete
    import time
    max_wait = 60  # seconds
    while max_wait > 0:
        response = client.get(f'/api/analysis/{analysis_id}', headers=headers)
        if json.loads(response.data)['status'] == 'completed':
            break
        time.sleep(1)
        max_wait -= 1
    
    # Get track ID
    response = client.get(f'/api/tracks/{analysis_id}', headers=headers)
    tracks = json.loads(response.data)
    if len(tracks) > 0:
        track_id = tracks[0]['id']
        
        # Download track
        response = client.get(f'/api/tracks/{track_id}/download', headers=headers)
        assert response.status_code == 200
        assert response.headers['Content-Type'].startswith('audio/')
        assert int(response.headers['Content-Length']) > 0
