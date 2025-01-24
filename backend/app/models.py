from datetime import datetime
from .extensions import db

class Analysis(db.Model):
    """Analysis model for storing track analysis metadata."""
    __tablename__ = 'analysis'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    duration = db.Column(db.Float)  # Duration in seconds
    error_message = db.Column(db.Text)
    
    # Relationship with Track model
    tracks = db.relationship('Track', back_populates='analysis', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'error_message': self.error_message,
            'tracks': [track.to_dict() for track in self.tracks]
        }

class Track(db.Model):
    """Track model for storing detected tracks within an analysis."""
    __tablename__ = 'tracks'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.Float, nullable=False)
    end_time = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    track_type = db.Column(db.String(50), nullable=False)  # 'full_track', 'onset_based', or 'final_segment'
    file_path = db.Column(db.String(500))  # path to the extracted audio file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Analysis model
    analysis = db.relationship('Analysis', back_populates='tracks')

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'title': self.title,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'confidence': self.confidence,
            'track_type': self.track_type,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
