from flask import Blueprint, request, jsonify
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
from dejavu_config import DATABASE
from db_setup import db, Analysis, Track
import yt_dlp
import os

analyze_bp = Blueprint('analyze', __name__)
djv = Dejavu(DATABASE)

def download_audio(url, output_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    files = [f for f in os.listdir(output_dir) if f.endswith('.wav')]
    if files:
        return os.path.join(output_dir, files[0])
    raise FileNotFoundError("No audio file found after download")

@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')

    analysis = Analysis(url=url, status='in_progress')
    db.session.add(analysis)
    db.session.commit()

    try:
        output_dir = '/tmp/audio'
        os.makedirs(output_dir, exist_ok=True)
        audio_file = download_audio(url, output_dir)
        djv.fingerprint_file(audio_file)
        results = djv.recognize(FileRecognizer, audio_file)

        for track in results['results']:
            new_track = Track(
                analysis_id=analysis.id,
                track_name=track['song_name'],
                artist=track.get('artist', 'Unknown'),
                start_time=track['start'],
                end_time=track['end']
            )
            db.session.add(new_track)

        analysis.status = 'completed'
    except Exception as e:
        analysis.status = 'failed'
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.commit()

    return jsonify({"analysis_id": analysis.id}), 202