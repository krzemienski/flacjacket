import os
import tempfile
from datetime import datetime
import yt_dlp
import librosa
import numpy as np
from .extensions import celery, db
from .models import Analysis, Track

def download_audio(url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def analyze_audio(file_path):
    # Load the audio file
    y, sr = librosa.load(file_path)
    
    # Perform onset detection
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    
    # Use onset times to segment the audio
    segments = []
    for i in range(len(onset_times) - 1):
        start_time = onset_times[i]
        end_time = onset_times[i + 1]
        if end_time - start_time > 30:  # Only consider segments longer than 30 seconds
            segments.append({
                'start_time': float(start_time),
                'end_time': float(end_time),
                'confidence': 0.8  # Placeholder confidence
            })
    
    return segments

@celery.task
def process_audio_url(analysis_id):
    analysis = Analysis.query.get(analysis_id)
    if not analysis:
        return
    
    analysis.status = 'processing'
    db.session.commit()
    
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the audio
            output_path = os.path.join(temp_dir, 'audio')
            download_audio(analysis.url, output_path)
            
            # Analyze the audio file
            segments = analyze_audio(output_path + '.wav')
            
            # Create track entries
            for i, segment in enumerate(segments):
                track = Track(
                    analysis_id=analysis_id,
                    title=f'Track {i+1}',  # Placeholder title
                    start_time=segment['start_time'],
                    end_time=segment['end_time'],
                    confidence=segment['confidence']
                )
                db.session.add(track)
            
            analysis.status = 'completed'
            analysis.completed_at = datetime.utcnow()
            
    except Exception as e:
        analysis.status = 'failed'
        analysis.error_message = str(e)
        
    finally:
        db.session.commit()
