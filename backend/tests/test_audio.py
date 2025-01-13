import os
import pytest
from app.fingerprinting import AudioFingerprinter
from app.models import Audio
from app.extensions import db
from app import create_app

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    return app

def test_audio_fingerprinter_init(tmp_path):
    """Test AudioFingerprinter initialization"""
    # Create a dummy audio file
    test_file = tmp_path / "test.flac"
    test_file.write_bytes(b'dummy audio content')
    
    fingerprinter = AudioFingerprinter(str(test_file))
    assert fingerprinter.file_path == str(test_file)
    assert hasattr(fingerprinter, 'log')

def test_audio_duration(tmp_path):
    """Test getting audio duration"""
    # Create a real audio file using ffmpeg
    test_file = tmp_path / "test.flac"
    os.system(f'ffmpeg -f lavfi -i "sine=frequency=1000:duration=5" {test_file}')
    
    fingerprinter = AudioFingerprinter(str(test_file))
    assert fingerprinter.duration == pytest.approx(5.0, rel=0.1)

def test_audfprint_analysis(tmp_path):
    """Test audfprint analysis"""
    # Create a real audio file using ffmpeg
    test_file = tmp_path / "test.flac"
    os.system(f'ffmpeg -f lavfi -i "sine=frequency=1000:duration=5" {test_file}')
    
    fingerprinter = AudioFingerprinter(str(test_file))
    results = fingerprinter.analyze_with_audfprint()
    
    assert isinstance(results, list)

def test_audio_model(app):
    """Test Audio model"""
    audio = Audio(
        title='Test Song',
        artist='Test Artist',
        filename='test.flac',
        user_id=1
    )
    
    db.session.add(audio)
    db.session.commit()
    
    assert audio.id is not None
    assert audio.title == 'Test Song'
    assert audio.artist == 'Test Artist'
    assert audio.filename == 'test.flac'
    assert audio.user_id == 1
    assert audio.created_at is not None
    
    # Test relationships
    assert hasattr(audio, 'user')
    assert hasattr(audio, 'fingerprints')

def test_audio_fingerprint_methods(tmp_path):
    """Test all fingerprinting methods"""
    # Create a real audio file using ffmpeg
    test_file = tmp_path / "test.flac"
    os.system(f'ffmpeg -f lavfi -i "sine=frequency=1000:duration=5" {test_file}')
    
    fingerprinter = AudioFingerprinter(str(test_file))
    results = fingerprinter.analyze_all_methods()
    
    assert isinstance(results, dict)
    assert 'audfprint' in results
    assert isinstance(results['audfprint'], list)
    
    # Note: We're not testing acoustid here since it requires an API key
    # and dejavu since it requires a MySQL database
