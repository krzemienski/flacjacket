import os
import pytest
import tempfile
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
            assert 'recognition_metadata' in track
            assert 'acoustid_score' in track['recognition_metadata']
    finally:
        os.remove(temp_path)

def test_dejavu_analysis():
    """Test Dejavu fingerprinting."""
    # Create a test audio file
    with tempfile.NamedTemporaryFile(suffix='.flac', delete=False) as temp_file:
        temp_file.write(b'dummy audio data')
        temp_path = temp_file.name
    
    try:
        fingerprinter = AudioFingerprinter(temp_path)
        results = fingerprinter.analyze_with_dejavu()
        
        assert isinstance(results, list)
        for track in results:
            assert 'title' in track
            assert 'start_time' in track
            assert 'end_time' in track
            assert 'confidence' in track
            assert track['method'] == 'dejavu'
            assert 'recognition_metadata' in track
            assert 'dejavu_confidence' in track['recognition_metadata']
    finally:
        os.remove(temp_path)

def test_audfprint_analysis():
    """Test audfprint fingerprinting."""
    # Create a test audio file
    with tempfile.NamedTemporaryFile(suffix='.flac', delete=False) as temp_file:
        temp_file.write(b'dummy audio data')
        temp_path = temp_file.name
    
    try:
        fingerprinter = AudioFingerprinter(temp_path)
        results = fingerprinter.analyze_with_audfprint()
        
        assert isinstance(results, list)
        for track in results:
            assert 'title' in track
            assert 'start_time' in track
            assert 'end_time' in track
            assert 'confidence' in track
            assert track['method'] == 'audfprint'
            assert 'recognition_metadata' in track
            assert 'audfprint_score' in track['recognition_metadata']
    finally:
        os.remove(temp_path)

def test_analyze_all_methods():
    """Test running all fingerprinting methods."""
    # Create a test audio file
    with tempfile.NamedTemporaryFile(suffix='.flac', delete=False) as temp_file:
        temp_file.write(b'dummy audio data')
        temp_path = temp_file.name
    
    try:
        fingerprinter = AudioFingerprinter(temp_path)
        results = fingerprinter.analyze_all_methods()
        
        assert isinstance(results, dict)
        assert 'acoustid' in results
        assert 'dejavu' in results
        assert 'audfprint' in results
        
        # Check each method's results
        for method, tracks in results.items():
            assert isinstance(tracks, list)
            for track in tracks:
                assert 'title' in track
                assert 'start_time' in track
                assert 'end_time' in track
                assert 'confidence' in track
                assert track['method'] == method
                assert 'recognition_metadata' in track
    finally:
        os.remove(temp_path)
