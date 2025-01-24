import os
import pytest
import time
from app import create_app
from app.extensions import db
from app.models import Analysis, Track
from app.tasks import process_audio_url

# Test URL from SoundCloud - using just one for now to debug
SOUNDCLOUD_URL = "https://soundcloud.com/sparrowandbarbossa/maggies1"

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flacjacket:flacjacket@localhost/flacjacket_test'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_soundcloud_track_analysis(app, client, caplog):
    """
    Functional test to verify the complete analysis pipeline for a SoundCloud track.
    This test:
    1. Creates an analysis record
    2. Processes the audio using real SoundCloud URL
    3. Verifies track detection and properties
    4. Validates logging output for each stage
    """
    with app.app_context():
        # Create analysis record
        analysis = Analysis(url=SOUNDCLOUD_URL)
        db.session.add(analysis)
        db.session.commit()
        
        # Process the audio (this will take some time)
        process_audio_url.apply(args=[analysis.id]).get(timeout=300)  # 5 minute timeout
        
        # Refresh the analysis from DB
        db.session.refresh(analysis)
        
        # Verify analysis completed successfully
        assert analysis.status == 'completed', f"Analysis failed with error: {analysis.error_message}"
        assert analysis.duration > 0, "Processing duration not recorded"
        
        # Get detected tracks
        tracks = Track.query.filter_by(analysis_id=analysis.id).all()
        
        # Basic validation of track detection
        assert len(tracks) > 0, "No tracks were detected"
        
        # Print analysis summary
        print(f"\nAnalysis Summary for {SOUNDCLOUD_URL}:")
        print(f"Total processing time: {analysis.duration:.2f} seconds")
        print(f"Number of tracks detected: {len(tracks)}")
        
        # Verify track properties
        total_duration = 0
        for track in tracks:
            assert track.start_time >= 0, "Invalid start time"
            assert track.end_time > track.start_time, "Invalid end time"
            assert track.confidence > 0, "Invalid confidence score"
            assert track.track_type in ['full_track', 'onset_based', 'final_segment'], "Invalid track type"
            
            duration = track.end_time - track.start_time
            total_duration += duration
            
            # Log track information
            print(f"\nTrack {track.id}:")
            print(f"  Type: {track.track_type}")
            print(f"  Start time: {track.start_time:.2f}s")
            print(f"  End time: {track.end_time:.2f}s")
            print(f"  Duration: {duration:.2f}s")
            print(f"  Confidence: {track.confidence:.2f}")
        
        print(f"\nTotal audio duration: {total_duration:.2f}s")
        
        # Verify essential logging stages
        expected_logs = [
            'starting_audio_processing',
            'created_temp_directory',
            'downloading_audio',
            'downloading_track',
            'scdl_output',
            'soundcloud_download_complete',
            'converting_to_wav',
            'wav_conversion_complete',
            'cleanup_complete',
            'starting_audio_analysis',
            'audio_file_loaded',
            'performing_onset_detection',
            'onset_detection_complete',
            'segmenting_audio',
            'analysis_complete',
            'creating_track_entries',
            'processing_completed'
        ]
        
        for log_event in expected_logs:
            assert log_event in caplog.text, f"Missing log event: {log_event}"

def test_soundcloud_track_analysis_api(client):
    """
    Test the complete API flow for SoundCloud track analysis.
    """
    # Start analysis
    response = client.post('/api/analysis', json={
        'url': SOUNDCLOUD_URL
    })
    assert response.status_code == 202  # Expect 202 Accepted for async operation
    data = response.get_json()
    analysis_id = data['id']
    
    # Poll for completion (with timeout)
    start_time = time.time()
    timeout = 300  # 5 minutes
    while time.time() - start_time < timeout:
        response = client.get(f'/api/analysis/{analysis_id}')
        assert response.status_code == 200
        data = response.get_json()
        
        if data['status'] == 'completed':
            # Verify tracks were detected
            assert len(data['tracks']) > 0, "No tracks were detected"
            print(f"\nDetected {len(data['tracks'])} tracks:")
            for track in data['tracks']:
                print(f"Track {track['id']}:")
                print(f"  Type: {track['track_type']}")
                print(f"  Start time: {track['start_time']:.2f}s")
                print(f"  End time: {track['end_time']:.2f}s")
                print(f"  Duration: {(track['end_time'] - track['start_time']):.2f}s")
                print(f"  Confidence: {track['confidence']:.2f}")
            return
        
        time.sleep(5)  # Wait before polling again
    
    pytest.fail("Analysis did not complete within timeout")
