from datetime import datetime
from .extensions import db

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    tracks = db.relationship('Track', backref='analysis', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'tracks': [track.to_dict() for track in self.tracks]
        }

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    title = db.Column(db.String(200))
    artist = db.Column(db.String(200))
    start_time = db.Column(db.Float)  # in seconds
    end_time = db.Column(db.Float)    # in seconds
    confidence = db.Column(db.Float)   # confidence score of the match
    file_path = db.Column(db.String(500))  # path to the extracted audio file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'confidence': self.confidence,
            'duration': self.end_time - self.start_time if self.end_time and self.start_time else None,
            'created_at': self.created_at.isoformat()
        }
