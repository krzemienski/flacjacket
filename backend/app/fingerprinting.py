import os
import subprocess
import json
import tempfile
from datetime import datetime
import acoustid
from flask import current_app
import numpy as np
from pydub import AudioSegment
import audfprint
import structlog

# Get logger
logger = structlog.get_logger("flacjacket.analysis")

class AudioFingerprinter:
    """Class to handle multiple fingerprinting methods"""
    
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
            
    def analyze_with_audfprint(self):
        """Analyze using audfprint"""
        log = self.log.bind(method="audfprint")
        log.info("starting_audfprint_analysis")
        
        try:
            # Initialize audfprint
            log.debug("initializing_audfprint")
            analyzer = audfprint.Analyzer()
            
            # Load the reference database
            db_path = current_app.config['AUDFPRINT_DB_PATH']
            log.debug("loading_database", db_path=db_path)
            analyzer.load_fingerprint_database(db_path)
            
            # Split audio into chunks for analysis
            chunk_size = 30  # seconds
            audio = AudioSegment.from_file(self.file_path)
            
            tracks = []
            for i in range(0, len(audio), chunk_size * 1000):
                chunk = audio[i:i + chunk_size * 1000]
                
                # Save chunk to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    log.debug("analyzing_chunk",
                             chunk_start=i/1000,
                             chunk_end=(i + chunk_size * 1000)/1000,
                             temp_file=temp_file.name)
                    
                    chunk.export(temp_file.name, format='wav')
                    
                    # Analyze the chunk
                    results = analyzer.match_file(temp_file.name)
                    
                    if results is not None and results[0] > 0:  # If matches found
                        track = {
                            'title': results[1],  # Track name from reference database
                            'start_time': i / 1000,  # Convert ms to seconds
                            'end_time': min((i + chunk_size * 1000) / 1000, self.duration),
                            'confidence': results[0] / 100,  # Normalize to 0-1
                            'method': 'audfprint',
                            'metadata': {
                                'audfprint_score': results[0]
                            }
                        }
                        
                        log.info("track_identified",
                                title=results[1],
                                confidence=results[0]/100)
                        
                        tracks.append(track)
                        
                    os.unlink(temp_file.name)
            
            log.info("audfprint_analysis_complete",
                    track_count=len(tracks))
            return tracks
            
        except Exception as e:
            log.error("audfprint_analysis_failed",
                     error=str(e),
                     exc_info=True)
            raise Exception(f"audfprint analysis failed: {str(e)}")
            
    def analyze_all_methods(self):
        """Run analysis with all available methods"""
        log = self.log.bind(operation="analyze_all_methods")
        
        results = {
            'acoustid': [],
            'audfprint': []
        }
        
        try:
            log.info("running_acoustid")
            results['acoustid'] = self.analyze_with_acoustid()
        except Exception as e:
            log.error("acoustid_failed", error=str(e))
            
        try:
            log.info("running_audfprint")
            results['audfprint'] = self.analyze_with_audfprint()
        except Exception as e:
            log.error("audfprint_failed", error=str(e))
            
        # Log summary of results
        summary = {
            method: len(tracks)
            for method, tracks in results.items()
        }
        log.info("analysis_complete",
                total_tracks=sum(summary.values()),
                tracks_by_method=summary)
            
        return results
