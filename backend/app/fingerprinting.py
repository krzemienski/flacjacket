import os
import subprocess
import json
import tempfile
from datetime import datetime
import acoustid
from flask import current_app
from pydub import AudioSegment
import structlog

# Get logger
logger = structlog.get_logger("flacjacket.analysis")

class AudioFingerprinter:
    """Class to handle audio fingerprinting using AcoustID"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.log = logger.bind(file_path=file_path)
        self.duration = self._get_audio_duration()
        
    def _get_audio_duration(self):
        """Get duration of audio file in seconds using ffprobe"""
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'json',
            self.file_path
        ]
        
        try:
            self.log.debug("getting_duration", command=" ".join(cmd))
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            self.log.info("duration_found", duration=duration)
            return duration
        except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError) as e:
            self.log.error("duration_not_found", error=str(e), exc_info=True)
            raise Exception(f"Could not determine audio duration: {str(e)}")
            
    def analyze_with_acoustid(self):
        """Analyze using AcoustID/Chromaprint"""
        log = self.log.bind(method="acoustid")
        log.info("starting_acoustid_analysis")
        
        try:
            matches = acoustid.match(current_app.config['ACOUSTID_API_KEY'], self.file_path)
            
            tracks = []
            current_position = 0
            
            for score, recording_id, title, artist in matches:
                if score < 0.5:  # Skip low confidence matches
                    log.debug("skipping_low_confidence_match",
                            score=score,
                            recording_id=recording_id)
                    continue
                    
                # Estimate track duration (this is simplified)
                track_duration = 180  # Default 3 minutes if can't determine
                
                track = {
                    'title': title,
                    'artist': artist,
                    'start_time': current_position,
                    'end_time': min(current_position + track_duration, self.duration),
                    'confidence': score,
                    'method': 'acoustid',
                    'metadata': {
                        'recording_id': recording_id,
                        'acoustid_score': score
                    }
                }
                
                log.info("track_identified",
                        title=title,
                        artist=artist,
                        confidence=score,
                        recording_id=recording_id)
                
                tracks.append(track)
                current_position += track_duration
                
                if current_position >= self.duration:
                    break
            
            log.info("acoustid_analysis_complete",
                    track_count=len(tracks))
            return tracks
            
        except Exception as e:
            log.error("acoustid_analysis_failed",
                     error=str(e),
                     exc_info=True)
            raise Exception(f"AcoustID analysis failed: {str(e)}")
            
    def analyze_all_methods(self):
        """Run analysis with AcoustID"""
        log = self.log.bind(action="analyze_all")
        log.info("starting_analysis")
        
        try:
            # Only use AcoustID for analysis
            tracks = self.analyze_with_acoustid()
            
            log.info("analysis_complete",
                    track_count=len(tracks))
            
            return tracks
            
        except Exception as e:
            log.error("analysis_failed",
                     error=str(e),
                     exc_info=True)
            raise
