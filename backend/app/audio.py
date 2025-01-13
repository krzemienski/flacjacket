import os
import subprocess
import json
import magic
from datetime import datetime
import structlog
from flask import current_app
from .fingerprinting import AudioFingerprinter

# Get loggers for different components
download_logger = structlog.get_logger("flacjacket.download")
analysis_logger = structlog.get_logger("flacjacket.analysis")

def get_file_info(file_path):
    """Get detailed file information"""
    try:
        file_stat = os.stat(file_path)
        mime = magic.Magic(mime=True)
        return {
            'path': file_path,
            'size_bytes': file_stat.st_size,
            'size_mb': file_stat.st_size / (1024 * 1024),
            'created_at': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            'mime_type': mime.from_file(file_path)
        }
    except Exception as e:
        return {'error': str(e)}

def download_audio(url, source_type):
    """Download audio from URL using appropriate downloader"""
    log = download_logger.bind(
        url=url,
        source_type=source_type,
        operation="download_audio"
    )
    
    log.info("starting_download", status="pending")
    
    output_dir = current_app.config['UPLOAD_FOLDER']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_template = os.path.join(output_dir, f'{timestamp}_%(title)s.%(ext)s')

    try:
        if source_type == 'youtube':
            log.debug("using_youtube_dl")
            cmd = [
                'yt-dlp',
                '-x',  # Extract audio
                '--audio-format', 'flac',  # Convert to FLAC
                '--audio-quality', '0',  # Best quality
                '-o', output_template,
                '--verbose',  # Enable verbose output
                url
            ]
        else:  # soundcloud
            log.debug("using_soundcloud_dl")
            cmd = [
                'scdl',
                '-l', url,  # URL to download
                '--path', output_dir,  # Output directory
                '--flac',  # Download in FLAC format
                '--debug'  # Enable debug output
            ]

        log.debug("executing_command", command=" ".join(cmd))
        
        # Run the command and capture output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Log output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                log.debug("downloader_output", output=output.strip())
        
        # Get the return code and any error output
        return_code = process.poll()
        errors = process.stderr.read()
        
        if return_code != 0:
            log.error("download_failed", 
                     return_code=return_code,
                     error=errors)
            raise Exception(f"Download failed with code {return_code}: {errors}")
        
        # Find the downloaded file
        files = os.listdir(output_dir)
        downloaded_files = [f for f in files if f.startswith(timestamp)]
        if not downloaded_files:
            log.error("file_not_found", timestamp=timestamp)
            raise Exception("Download completed but file not found")
        
        downloaded_file = os.path.join(output_dir, downloaded_files[0])
        file_info = get_file_info(downloaded_file)
        
        log.info("download_complete",
                status="success",
                file_info=file_info)
        
        return downloaded_file

    except Exception as e:
        log.error("download_failed",
                 error=str(e),
                 exc_info=True)
        raise Exception(f"Download failed: {str(e)}")

def analyze_audio(file_path):
    """Analyze audio file using AcoustID fingerprinting"""
    log = analysis_logger.bind(
        file_path=file_path,
        operation="analyze_audio"
    )
    
    try:
        # Log file information
        file_info = get_file_info(file_path)
        log.info("starting_analysis",
                status="pending",
                file_info=file_info)
        
        # Initialize fingerprinter
        fingerprinter = AudioFingerprinter(file_path)
        
        # Run analysis with AcoustID
        log.info("starting_acoustid_analysis")
        try:
            results = fingerprinter.analyze_with_acoustid()
            log.info("acoustid_analysis_complete",
                    track_count=len(results))
            return results
        except Exception as e:
            log.error("acoustid_analysis_failed",
                     error=str(e),
                     exc_info=True)
            raise
        
    except Exception as e:
        log.error("analysis_failed",
                 error=str(e),
                 exc_info=True)
        raise Exception(f"Analysis failed: {str(e)}")

def get_audio_duration(file_path):
    """Get duration of audio file in seconds using ffprobe"""
    log = analysis_logger.bind(
        file_path=file_path,
        operation="get_audio_duration"
    )
    
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-show_entries', 'format=duration',
        '-of', 'json',
        file_path
    ]
    
    try:
        log.debug("executing_command", command=" ".join(cmd))
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        
        log.info("duration_found", duration=duration)
        
        return duration
        
    except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError) as e:
        log.error("duration_not_found",
                 error=str(e),
                 exc_info=True)
        raise Exception(f"Could not determine audio duration: {str(e)}")

def extract_track(source_file, start_time, duration):
    """Extract a portion of the audio file"""
    log = analysis_logger.bind(
        source_file=source_file,
        start_time=start_time,
        duration=duration,
        operation="extract_track"
    )
    
    output_dir = current_app.config['UPLOAD_FOLDER']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'{timestamp}_track.flac')
    
    log.info("starting_extraction",
            status="pending",
            output_file=output_file)
    
    cmd = [
        'ffmpeg',
        '-i', source_file,
        '-ss', str(start_time),
        '-t', str(duration),
        '-c:a', 'flac',
        '-y',  # Overwrite output file
        output_file
    ]
    
    try:
        log.debug("executing_command", command=" ".join(cmd))
        
        # Run ffmpeg
        process = subprocess.run(cmd, 
                               capture_output=True, 
                               text=True, 
                               check=True)
        
        # Get file information
        file_info = get_file_info(output_file)
        
        log.info("extraction_complete",
                status="success",
                file_info=file_info)
        
        return output_file
        
    except subprocess.CalledProcessError as e:
        log.error("extraction_failed",
                 error=e.stderr,
                 return_code=e.returncode,
                 exc_info=True)
        raise Exception(f"Track extraction failed: {e.stderr}")
    except Exception as e:
        log.error("extraction_failed",
                 error=str(e),
                 exc_info=True)
        raise Exception(f"Track extraction failed: {str(e)}")
