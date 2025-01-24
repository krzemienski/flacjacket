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
        try:
            # Download track with scdl
            log.info('downloading_track')
            result = subprocess.run([
                'scdl',
                '-l', url,
                '--path', os.path.dirname(output_path),
                '--onlymp3'
            ], capture_output=True, text=True)
            
            log.info('scdl_output', 
                    stdout=result.stdout,
                    stderr=result.stderr)
            
            # Check if the file was downloaded - look for any .mp3 file
            mp3_files = [f for f in os.listdir(os.path.dirname(output_path)) if f.endswith('.mp3')]
            if not mp3_files:
                log.error('mp3_file_not_found', 
                         dir_path=os.path.dirname(output_path),
                         dir_contents=os.listdir(os.path.dirname(output_path)))
                raise Exception("No MP3 file found after download")
            
            # Use the first MP3 file found
            mp3_path = os.path.join(os.path.dirname(output_path), mp3_files[0])
            mp3_size = os.path.getsize(mp3_path)
            log.info('soundcloud_download_complete', 
                    file_path=mp3_path,
                    file_size_bytes=mp3_size)
            
            # Convert downloaded MP3 to WAV using ffmpeg
            wav_path = output_path + '.wav'
            log.info('converting_to_wav')
            result = subprocess.run([
                'ffmpeg',
                '-i', mp3_path,
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                wav_path
            ], capture_output=True, text=True)
            
            if not os.path.exists(wav_path):
                log.error('wav_file_not_found', 
                         expected_path=wav_path,
                         dir_contents=os.listdir(os.path.dirname(output_path)))
                raise Exception(f"WAV file not found at {wav_path}")
            
            wav_size = os.path.getsize(wav_path)
            log.info('wav_conversion_complete', 
                    input_size_bytes=mp3_size,
                    output_size_bytes=wav_size,
                    conversion_log=result.stderr)
            
            # Remove the MP3 file
            os.remove(mp3_path)
            log.info('cleanup_complete', removed_file=mp3_path)
            
        except subprocess.CalledProcessError as e:
            log.error('soundcloud_download_failed', 
                     error=str(e),
                     stdout=e.stdout if hasattr(e, 'stdout') else None,
                     stderr=e.stderr if hasattr(e, 'stderr') else None)
            raise Exception(f"Failed to download from SoundCloud: {str(e)}")
        except Exception as e:
            log.error('unexpected_error',
                     error=str(e),
                     error_type=type(e).__name__)
            raise
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
        duration = librosa.get_duration(y=y, sr=sr)
        log.info('audio_file_loaded', 
                duration_seconds=duration,
                sample_rate=sr,
                total_samples=len(y))
        
        # Perform onset detection
        log.info('performing_onset_detection')
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        log.info('onset_detection_complete', 
                total_onsets=len(onset_times),
                first_onset=float(onset_times[0]) if len(onset_times) > 0 else None,
                last_onset=float(onset_times[-1]) if len(onset_times) > 0 else None)
        
        # Use onset times to segment the audio
        log.info('segmenting_audio')
        segments = []
        min_duration = 5  # Minimum segment duration in seconds
        
        # If no onsets detected, treat the whole file as one segment
        if len(onset_times) == 0:
            segments.append({
                'start_time': 0.0,
                'end_time': float(duration),
                'confidence': 0.9,
                'type': 'full_track'
            })
            log.info('created_full_track_segment', 
                    duration=duration,
                    confidence=0.9)
        else:
            # Process segments between onsets
            for i in range(len(onset_times) - 1):
                start_time = onset_times[i]
                end_time = onset_times[i + 1]
                segment_duration = end_time - start_time
                
                if segment_duration >= min_duration:
                    confidence = min(0.9, segment_duration / 60.0)  # Higher confidence for longer segments
                    segments.append({
                        'start_time': float(start_time),
                        'end_time': float(end_time),
                        'confidence': confidence,
                        'type': 'onset_based'
                    })
                    log.info('created_onset_segment', 
                            segment_number=i+1,
                            start_time=float(start_time),
                            end_time=float(end_time),
                            duration=segment_duration,
                            confidence=confidence)
            
            # Handle the last segment to the end of the file
            if len(onset_times) > 0:
                last_onset = onset_times[-1]
                remaining_duration = duration - last_onset
                if remaining_duration >= min_duration:
                    confidence = min(0.9, remaining_duration / 60.0)
                    segments.append({
                        'start_time': float(last_onset),
                        'end_time': float(duration),
                        'confidence': confidence,
                        'type': 'final_segment'
                    })
                    log.info('created_final_segment',
                            start_time=float(last_onset),
                            end_time=float(duration),
                            duration=remaining_duration,
                            confidence=confidence)
        
        log.info('analysis_complete', 
                total_segments=len(segments),
                total_duration=duration,
                segment_types=[s['type'] for s in segments],
                average_confidence=sum(s['confidence'] for s in segments)/len(segments) if segments else 0)
        return segments
    except Exception as e:
        log.error('analysis_failed', error=str(e))
        raise

def process_segments(analysis_id, segments, file_path):
    """Process detected segments and create Track entries."""
    log = logger.bind(analysis_id=analysis_id)
    log.info('creating_track_entries')

    for i, segment in enumerate(segments):
        track = Track(
            analysis_id=analysis_id,
            title=f"Track {i+1}",
            start_time=segment['start_time'],
            end_time=segment['end_time'],
            confidence=segment['confidence'],
            track_type=segment['type'],
            file_path=file_path
        )
        db.session.add(track)
    
    try:
        db.session.commit()
        log.info('tracks_created', count=len(segments))
    except Exception as e:
        log.error('track_creation_failed', error=str(e))
        db.session.rollback()
        raise

@celery.task(bind=True)
def process_audio_url(self, analysis_id):
    """Process a SoundCloud URL and extract tracks."""
    from app import create_app
    app = create_app()
    
    with app.app_context():
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
        analysis.started_at = datetime.utcnow()
        db.session.commit()
        log.info('analysis_status_updated', status='processing', started_at=analysis.started_at)
        
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
                
                # Process segments
                process_segments(analysis_id, segments, output_path + '.wav')
                
                analysis.status = 'completed'
                analysis.completed_at = datetime.utcnow()
                analysis.duration = (analysis.completed_at - analysis.started_at).total_seconds()
                log.info('processing_completed',
                        total_tracks=len(segments),
                        processing_duration=analysis.duration)
                
        except Exception as e:
            log.error('processing_failed', error=str(e))
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.completed_at = datetime.utcnow()
            analysis.duration = (analysis.completed_at - analysis.started_at).total_seconds()
            
        finally:
            db.session.commit()
