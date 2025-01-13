import os
import tempfile
import pytest
from app.fingerprinting import AudioFingerprinter

def test_acoustid_analysis():
    """Test AcoustID/Chromaprint fingerprinting."""
    # Create a test audio file
    with tempfile.NamedTemporaryFile(suffix='.flac', delete=False) as temp_file:
        temp_file.write(b'dummy audio data')
        temp_path = temp_file.name
    
    try:
        fingerprinter = AudioFingerprinter(temp_path)
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
    finally:
        os.remove(temp_path)

def test_analyze_all_methods():
    """Test running all analysis methods (only AcoustID)."""
    # Create a test audio file
    with tempfile.NamedTemporaryFile(suffix='.flac', delete=False) as temp_file:
        temp_file.write(b'dummy audio data')
        temp_path = temp_file.name
    
    try:
        fingerprinter = AudioFingerprinter(temp_path)
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
    finally:
        os.remove(temp_path)
