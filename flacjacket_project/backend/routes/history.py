from flask import Blueprint, jsonify
from db_setup import Analysis, Track

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
def history():
    analyses = Analysis.query.all()
    return jsonify([{
        "id": a.id,
        "url": a.url,
        "status": a.status,
        "created_at": a.created_at,
        "tracks": [
            {
                "track_name": t.track_name,
                "artist": t.artist,
                "start_time": t.start_time,
                "end_time": t.end_time
            } for t in Track.query.filter_by(analysis_id=a.id).all()
        ]
    } for a in analyses])