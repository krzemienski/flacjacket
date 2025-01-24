from flask import jsonify, send_file
from . import bp
from ..models import Track
import os

@bp.route('/tracks/<int:track_id>', methods=['GET'])
def get_track(track_id):
    track = Track.query.get_or_404(track_id)
    return jsonify(track.to_dict())

@bp.route('/tracks/<int:track_id>/download', methods=['GET'])
def download_track(track_id):
    track = Track.query.get_or_404(track_id)
    
    if not track.file_path or not os.path.exists(track.file_path):
        return jsonify({'error': 'Track file not found'}), 404
    
    return send_file(
        track.file_path,
        as_attachment=True,
        download_name=f"track_{track.id}_{track.track_type}.wav"
    )
