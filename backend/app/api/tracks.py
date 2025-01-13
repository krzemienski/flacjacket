from flask import send_file, current_app
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields
from app.models import Track
import os

api = Namespace('tracks', description='Track operations')

# API Models
track_model = api.model('Track', {
    'id': fields.Integer(required=True, description='Track ID'),
    'track_name': fields.String(description='Track name'),
    'artist': fields.String(description='Artist name'),
    'start_time': fields.Float(description='Start time in seconds'),
    'end_time': fields.Float(description='End time in seconds'),
    'confidence': fields.Float(description='Confidence score (0-1)'),
    'fingerprint_method': fields.String(description='Method used for fingerprinting'),
    'metadata': fields.Raw(description='Additional metadata')
})

@api.route('/<int:track_id>')
@api.param('track_id', 'The track identifier')
class TrackResource(Resource):
    @api.doc('get_track')
    @api.marshal_with(track_model)
    @jwt_required()
    def get(self, track_id):
        """Get a track by ID"""
        track = Track.query.get_or_404(track_id)
        return track.to_dict()

@api.route('/<int:track_id>/download')
@api.param('track_id', 'The track identifier')
class TrackDownloadResource(Resource):
    @api.doc('download_track')
    @api.produces(['audio/flac'])
    @jwt_required()
    def get(self, track_id):
        """Download a track"""
        track = Track.query.get_or_404(track_id)
        if not track.download_path or not os.path.exists(track.download_path):
            api.abort(404, 'Track file not found')
        
        # Generate filename with fingerprinting method
        filename = f"{track.track_name}"
        if track.artist:
            filename = f"{track.artist} - {filename}"
        filename = f"{filename} [{track.fingerprint_method}].flac"
        
        return send_file(
            track.download_path,
            as_attachment=True,
            download_name=filename
        )
