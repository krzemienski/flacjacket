import json
import pytest
from app import create_app
import os
from werkzeug.datastructures import FileStorage

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

def test_tracks_endpoint(client, auth_token):
    """Test getting track details."""
    # First create an analysis
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.post('/api/analysis', json={
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'source': 'youtube'
    }, headers=headers)
    analysis_id = json.loads(response.data)['id']
    
    # Wait for analysis to complete
    import time
    max_retries = 10
    for _ in range(max_retries):
        response = client.get(f'/api/analysis/{analysis_id}', headers=headers)
        data = json.loads(response.data)
        if data['status'] == 'completed':
            break
        time.sleep(1)
    
    # Then get tracks
    response = client.get(f'/api/analysis/{analysis_id}/tracks', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_track_download_endpoint(client, auth_token):
    """Test downloading a track."""
    # First create an analysis
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.post('/api/analysis', json={
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'source': 'youtube'
    }, headers=headers)
    analysis_id = json.loads(response.data)['id']
    
    # Wait for analysis to complete
    import time
    max_retries = 10
    for _ in range(max_retries):
        response = client.get(f'/api/analysis/{analysis_id}', headers=headers)
        data = json.loads(response.data)
        if data['status'] == 'completed':
            break
        time.sleep(1)
    
    # Get tracks
    response = client.get(f'/api/analysis/{analysis_id}/tracks', headers=headers)
    tracks = json.loads(response.data)
    track_id = tracks[0]['id']
    
    # Download track
    response = client.get(f'/api/tracks/{track_id}/download', headers=headers)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'audio/flac'

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert json.loads(response.data)['status'] == 'healthy'

def test_user_registration(client):
    """Test user registration endpoint"""
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'securepassword123'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert data['username'] == 'newuser'

def test_user_login(client):
    """Test user login endpoint"""
    # First register a user
    client.post('/api/auth/register', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'securepassword123'
    })
    
    # Then try to login
    response = client.post('/api/auth/login', json={
        'username': 'loginuser',
        'password': 'securepassword123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data
    
    # Try with wrong password
    response = client.post('/api/auth/login', json={
        'username': 'loginuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_protected_endpoint(client):
    """Test protected endpoint access"""
    # First register and login
    client.post('/api/auth/register', json={
        'username': 'protecteduser',
        'email': 'protected@example.com',
        'password': 'securepassword123'
    })
    
    response = client.post('/api/auth/login', json={
        'username': 'protecteduser',
        'password': 'securepassword123'
    })
    token = json.loads(response.data)['access_token']
    
    # Try accessing protected endpoint without token
    response = client.get('/api/protected')
    assert response.status_code == 401
    
    # Try with token
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/protected', headers=headers)
    assert response.status_code == 200

def test_upload_audio(client, tmp_path):
    """Test audio file upload endpoint"""
    # First register and login
    register_data = {
        'username': 'uploaduser',
        'email': 'upload@example.com',
        'password': 'securepassword123'
    }
    
    client.post('/api/auth/register',
               data=json.dumps(register_data),
               content_type='application/json')
    
    login_response = client.post('/api/auth/login',
                              data=json.dumps({
                                  'username': 'uploaduser',
                                  'password': 'securepassword123'
                              }),
                              content_type='application/json')
    
    token = login_response.json['access_token']
    
    # Create a test audio file
    test_file_path = tmp_path / "test.flac"
    test_file_path.write_bytes(b'dummy audio content')
    
    with open(test_file_path, 'rb') as f:
        data = {
            'file': (f, 'test.flac'),
            'title': 'Test Song',
            'artist': 'Test Artist'
        }
        response = client.post('/api/audio/upload',
                            headers={'Authorization': f'Bearer {token}'},
                            data=data,
                            content_type='multipart/form-data')
    
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['title'] == 'Test Song'

def test_audio_analysis(client, tmp_path):
    """Test audio analysis endpoint"""
    # First register and login
    register_data = {
        'username': 'analysisuser',
        'email': 'analysis@example.com',
        'password': 'securepassword123'
    }
    
    client.post('/api/auth/register',
               data=json.dumps(register_data),
               content_type='application/json')
    
    login_response = client.post('/api/auth/login',
                              data=json.dumps({
                                  'username': 'analysisuser',
                                  'password': 'securepassword123'
                              }),
                              content_type='application/json')
    
    token = login_response.json['access_token']
    
    # Create and upload a test audio file
    test_file_path = tmp_path / "analysis.flac"
    test_file_path.write_bytes(b'dummy audio content')
    
    with open(test_file_path, 'rb') as f:
        data = {
            'file': (f, 'analysis.flac')
        }
        response = client.post('/api/audio/analyze',
                            headers={'Authorization': f'Bearer {token}'},
                            data=data,
                            content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert 'results' in response.json
    # Results should be a list since we're only using AcoustID
    assert isinstance(response.json['results'], list)
    for track in response.json['results']:
        assert track['method'] == 'acoustid'
        assert 'metadata' in track
        assert 'acoustid_score' in track['metadata']

def test_query_audio(client):
    """Test audio query endpoint"""
    # First register and login
    register_data = {
        'username': 'queryuser',
        'email': 'query@example.com',
        'password': 'securepassword123'
    }
    
    client.post('/api/auth/register',
               data=json.dumps(register_data),
               content_type='application/json')
    
    login_response = client.post('/api/auth/login',
                              data=json.dumps({
                                  'username': 'queryuser',
                                  'password': 'securepassword123'
                              }),
                              content_type='application/json')
    
    token = login_response.json['access_token']
    
    # Test querying audio
    response = client.get('/api/audio/query?q=test',
                        headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)
