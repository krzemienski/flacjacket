import os
import pytest
import tempfile
from app.audio import download_audio, analyze_audio, extract_track, get_file_info
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

def test_download_audio_youtube():
    """Test downloading audio from YouTube."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Use a known stable video
    try:
        file_path = download_audio(url, 'youtube')
        assert os.path.exists(file_path)
        
        # Check file info
        info = get_file_info(file_path)
        assert info['size_bytes'] > 0
        assert info['mime_type'].startswith('audio/')
        
        # Cleanup
        os.remove(file_path)
    except Exception as e:
        pytest.fail(f"Download failed: {str(e)}")

def test_download_audio_soundcloud():
    """Test downloading audio from SoundCloud."""
    url = "https://soundcloud.com/rick-astley-official/never-gonna-give-you-up-4"
    try:
        file_path = download_audio(url, 'soundcloud')
        assert os.path.exists(file_path)
        
        # Check file info
        info = get_file_info(file_path)
        assert info['size_bytes'] > 0
        assert info['mime_type'].startswith('audio/')
        
        # Cleanup
        os.remove(file_path)
    except Exception as e:
        pytest.fail(f"Download failed: {str(e)}")

def test_analyze_audio():
    """Test audio analysis with all fingerprinting methods."""
    # Create a test audio file
    with tempfile.NamedTemporaryFile(suffix='.flac', delete=False) as temp_file:
        temp_file.write(b'dummy audio data')
        temp_path = temp_file.name
    
    try:
        results = analyze_audio(temp_path)
        
        # Check that all methods were attempted
        assert 'acoustid' in results
        assert 'dejavu' in results
        assert 'audfprint' in results
        
        # Check result structure
        for method, tracks in results.items():
            assert isinstance(tracks, list)
            for track in tracks:
                assert 'title' in track
                assert 'start_time' in track
                assert 'end_time' in track
                assert 'confidence' in track
                assert 'method' in track
                assert 'recognition_metadata' in track
    finally:
        os.remove(temp_path)

def test_extract_track():
    """Test track extraction from audio file."""
    # Create a test audio file
    with tempfile.NamedTemporaryFile(suffix='.flac', delete=False) as temp_file:
        temp_file.write(b'dummy audio data')
        temp_path = temp_file.name
    
    try:
        output_file = extract_track(temp_path, 0, 30)  # Extract first 30 seconds
        assert os.path.exists(output_file)
        
        # Check file info
        info = get_file_info(output_file)
        assert info['size_bytes'] > 0
        assert info['mime_type'].startswith('audio/')
        
        # Cleanup
        os.remove(output_file)
    finally:
        os.remove(temp_path)
