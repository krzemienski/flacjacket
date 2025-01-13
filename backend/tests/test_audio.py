import os
import pytest
from app.fingerprinting import AudioFingerprinter
from app.models import Track, Analysis
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

def test_acoustid_analysis(tmp_path):
    """Test AcoustID analysis"""
    # Create a real audio file using ffmpeg
    test_file = tmp_path / "test.flac"
    os.system(f'ffmpeg -f lavfi -i "sine=frequency=1000:duration=5" {test_file}')
    
    fingerprinter = AudioFingerprinter(str(test_file))
    results = fingerprinter.analyze_with_acoustid()
    
    assert isinstance(results, list)
    for track in results:
        assert 'title' in track
        assert 'artist' in track
        assert 'start_time' in track
        assert 'end_time' in track
        assert 'confidence' in track
        assert track['method'] == 'acoustid'
        assert 'metadata' in track
        assert 'acoustid_score' in track['metadata']

def test_track_model(app):
    """Test Track model"""
    track = Track(
        title='Test Song',
        artist='Test Artist',
        start_time=0.0,
        end_time=5.0,
        confidence=0.8,
        fingerprint_method='acoustid',
        recognition_metadata={'acoustid_score': 0.8}
    )
    
    assert track.title == 'Test Song'
    assert track.artist == 'Test Artist'
    assert track.start_time == 0.0
    assert track.end_time == 5.0
    assert track.confidence == 0.8
    assert track.fingerprint_method == 'acoustid'
    assert track.recognition_metadata['acoustid_score'] == 0.8

def test_audio_fingerprint_methods(tmp_path):
    """Test all fingerprinting methods (only AcoustID)"""
    # Create a real audio file using ffmpeg
    test_file = tmp_path / "test.flac"
    os.system(f'ffmpeg -f lavfi -i "sine=frequency=1000:duration=5" {test_file}')
    
    fingerprinter = AudioFingerprinter(str(test_file))
    results = fingerprinter.analyze_all_methods()
    
    assert isinstance(results, list)
    for track in results:
        assert 'title' in track
        assert 'artist' in track
        assert 'start_time' in track
        assert 'end_time' in track
        assert 'confidence' in track
        assert track['method'] == 'acoustid'
        assert 'metadata' in track
        assert 'acoustid_score' in track['metadata']
