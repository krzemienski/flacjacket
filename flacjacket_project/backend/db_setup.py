from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default='Pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'))
    track_name = db.Column(db.String)
    artist = db.Column(db.String)
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)