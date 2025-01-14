import os
import tempfile
from datetime import datetime
import yt_dlp
import librosa
import numpy as np
from urllib.parse import urlparse
import subprocess
import structlog
from celery.utils.log import get_task_logger
from .extensions import celery, db
from .models import Analysis, Track

# Set up structured logging
logger = structlog.wrap_logger(get_task_logger(__name__))

def is_soundcloud_url(url):
    parsed = urlparse(url)
    return 'soundcloud.com' in parsed.netloc

def download_audio(url, output_path):
    log = logger.bind(url=url, output_path=output_path)
    log.info('starting_audio_download')
    
    if is_soundcloud_url(url):
        log.info('using_soundcloud_downloader')
        # Use scdl for SoundCloud URLs
        try:
            subprocess.run([
                'scdl',
                '-l', url,  # URL to download
                '--path', os.path.dirname(output_path),  # Download directory
                '--onlymp3',  # Only download MP3 format
                '--name-format', os.path.basename(output_path),  # Output filename
                '--no-playlist',  # Don't download playlists
            ], check=True)
            log.info('soundcloud_download_complete')
            
            # Convert downloaded MP3 to WAV using ffmpeg
            log.info('converting_to_wav')
            subprocess.run([
                'ffmpeg',
                '-i', output_path + '.mp3',
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                output_path + '.wav'
            ], check=True)
            log.info('wav_conversion_complete')
            
            # Remove the MP3 file
            os.remove(output_path + '.mp3')
            log.info('cleanup_complete')
            
        except subprocess.CalledProcessError as e:
            log.error('soundcloud_download_failed', error=str(e))
            raise Exception(f"Failed to download from SoundCloud: {str(e)}")
    else:
        log.info('using_youtube_downloader')
        # Use yt-dlp for other URLs (YouTube, etc.)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'logger': logger.bind(context='yt-dlp'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
                log.info('youtube_download_complete')
            except Exception as e:
                log.error('youtube_download_failed', error=str(e))
                raise Exception(f"Failed to download from YouTube: {str(e)}")

def analyze_audio(file_path):
    log = logger.bind(file_path=file_path)
    log.info('starting_audio_analysis')
    
    try:
        # Load the audio file
        log.info('loading_audio_file')
        y, sr = librosa.load(file_path)
        
        # Perform onset detection
        log.info('performing_onset_detection')
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        
        # Use onset times to segment the audio
        log.info('segmenting_audio')
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
        
        log.info('analysis_complete', segments_count=len(segments))
        return segments
    except Exception as e:
        log.error('analysis_failed', error=str(e))
        raise

@celery.task(bind=True)
def process_audio_url(self, analysis_id):
    log = logger.bind(
        analysis_id=analysis_id,
        task_id=self.request.id,
    )
    log.info('starting_audio_processing')
    
    analysis = Analysis.query.get(analysis_id)
    if not analysis:
        log.error('analysis_not_found')
        return
    
    analysis.status = 'processing'
    db.session.commit()
    
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            log.info('created_temp_directory', path=temp_dir)
            
            # Download the audio
            output_path = os.path.join(temp_dir, 'audio')
            log.info('downloading_audio')
            download_audio(analysis.url, output_path)
            
            # Update task state
            self.update_state(state='ANALYZING')
            
            # Analyze the audio file
            log.info('analyzing_audio')
            segments = analyze_audio(output_path + '.wav')
            
            # Create track entries
            log.info('creating_track_entries')
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
            log.info('processing_completed')
            
    except Exception as e:
        log.error('processing_failed', error=str(e))
        analysis.status = 'failed'
        analysis.error_message = str(e)
        
    finally:
        db.session.commit()
