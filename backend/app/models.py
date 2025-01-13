from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic')

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_url = db.Column(db.String(500), nullable=False)
    source_type = db.Column(db.String(20))  # youtube or soundcloud
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tracks = db.relationship('Track', backref='analysis', lazy='dynamic')

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    artist = db.Column(db.String(200))
    start_time = db.Column(db.Float)  # in seconds
    end_time = db.Column(db.Float)    # in seconds
    confidence = db.Column(db.Float)   # confidence score from AcoustID
    file_path = db.Column(db.String(500))  # path to extracted audio file
    fingerprint_method = db.Column(db.String(20), default='acoustid')  # only using AcoustID
    recognition_metadata = db.Column(db.JSON)      # additional metadata from AcoustID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'))

    def to_dict(self):
        """Convert track to dictionary representation"""
        return {
            'id': self.id,
            'track_name': self.title,
            'artist': self.artist,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'confidence': self.confidence,
            'fingerprint_method': self.fingerprint_method,
            'metadata': self.recognition_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
