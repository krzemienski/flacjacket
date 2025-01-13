from flask import request, current_app
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields
from ..models import db, Analysis, Track
from ..audio import download_audio, analyze_audio, extract_track
import os

api = Namespace('analysis', description='Audio analysis operations')

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

analysis_input = api.model('AnalysisInput', {
    'url': fields.String(required=True, description='URL of audio file to analyze'),
    'source': fields.String(required=False, default='youtube', enum=['youtube', 'soundcloud'], 
                          description='Source type (youtube or soundcloud)')
})

analysis_output = api.model('AnalysisOutput', {
    'id': fields.Integer(required=True, description='Analysis ID'),
    'status': fields.String(required=True, description='Analysis status'),
    'results': fields.Raw(description='Analysis results by fingerprinting method')
})

@api.route('')
class AnalysisResource(Resource):
    @api.doc('create_analysis')
    @api.expect(analysis_input)
    @api.marshal_with(analysis_output)
    @jwt_required()
    def post(self):
        """Start a new analysis job"""
        data = request.get_json()
        url = data['url']
        source_type = data.get('source', 'youtube')
        
        try:
            # Create new analysis record
            analysis = Analysis(url=url, source=source_type, status='in_progress')
            db.session.add(analysis)
            db.session.commit()
            
            # Download the audio file
            file_path = download_audio(url, source_type)
            analysis.file_path = file_path
            db.session.commit()
            
            # Analyze with multiple fingerprinting methods
            results = analyze_audio(file_path)
            
            # Store tracks for each method
            for method, tracks in results.items():
                for track_data in tracks:
                    # Extract the track segment
                    track_file = extract_track(file_path, track_data['start_time'], 
                                            track_data['end_time'] - track_data['start_time'])
                    
                    # Create track record
                    track = Track(
                        analysis_id=analysis.id,
                        track_name=track_data.get('title'),
                        artist=track_data.get('artist'),
                        start_time=track_data['start_time'],
                        end_time=track_data['end_time'],
                        confidence=track_data['confidence'],
                        download_path=track_file,
                        fingerprint_method=method,
                        metadata=track_data.get('metadata', {})
                    )
                    db.session.add(track)
            
            analysis.status = 'completed'
            db.session.commit()
            
            return {
                'id': analysis.id,
                'status': 'completed',
                'results': {
                    method: [track.to_dict() for track in analysis.tracks if track.fingerprint_method == method]
                    for method in results.keys()
                }
            }
            
        except Exception as e:
            if analysis:
                analysis.status = 'failed'
                analysis.error = str(e)
                db.session.commit()
            api.abort(500, str(e))

@api.route('/<int:analysis_id>')
@api.param('analysis_id', 'The analysis identifier')
class AnalysisDetailResource(Resource):
    @api.doc('get_analysis')
    @api.marshal_with(analysis_output)
    @jwt_required()
    def get(self, analysis_id):
        """Get analysis results by ID"""
        analysis = Analysis.query.get_or_404(analysis_id)
        
        # Group tracks by fingerprinting method
        tracks_by_method = {}
        for track in analysis.tracks:
            method = track.fingerprint_method
            if method not in tracks_by_method:
                tracks_by_method[method] = []
            tracks_by_method[method].append(track.to_dict())
        
        return {
            'id': analysis.id,
            'status': analysis.status,
            'results': tracks_by_method
        }

@api.route('/<int:analysis_id>/rerun')
@api.param('analysis_id', 'The analysis identifier')
class AnalysisRerunResource(Resource):
    @api.doc('rerun_analysis')
    @api.marshal_with(analysis_output)
    @jwt_required()
    def post(self, analysis_id):
        """Re-run analysis on an existing file"""
        analysis = Analysis.query.get_or_404(analysis_id)
        
        if not analysis.file_path or not os.path.exists(analysis.file_path):
            api.abort(404, 'Audio file not found')
            
        try:
            # Delete existing tracks
            Track.query.filter_by(analysis_id=analysis.id).delete()
            
            # Re-analyze with multiple fingerprinting methods
            results = analyze_audio(analysis.file_path)
            
            # Store new tracks
            for method, tracks in results.items():
                for track_data in tracks:
                    # Extract the track segment
                    track_file = extract_track(analysis.file_path, track_data['start_time'], 
                                            track_data['end_time'] - track_data['start_time'])
                    
                    # Create track record
                    track = Track(
                        analysis_id=analysis.id,
                        track_name=track_data.get('title'),
                        artist=track_data.get('artist'),
                        start_time=track_data['start_time'],
                        end_time=track_data['end_time'],
                        confidence=track_data['confidence'],
                        download_path=track_file,
                        fingerprint_method=method,
                        metadata=track_data.get('metadata', {})
                    )
                    db.session.add(track)
            
            analysis.status = 'completed'
            analysis.error = None
            db.session.commit()
            
            return {
                'id': analysis.id,
                'status': 'completed',
                'results': {
                    method: [track.to_dict() for track in analysis.tracks if track.fingerprint_method == method]
                    for method in results.keys()
                }
            }
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.error = str(e)
            db.session.commit()
            api.abort(500, str(e))
