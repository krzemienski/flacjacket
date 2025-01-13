from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from config import Config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
api = Api(title='FlacJacket API',
          version='1.0',
          description='API for analyzing and extracting tracks from audio files',
          doc='/docs')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)

    # Import and register API namespaces
    from app.api.auth import api as auth_ns
    from app.api.analysis import api as analysis_ns
    from app.api.tracks import api as tracks_ns

    api.add_namespace(auth_ns, path='/api/auth')
    api.add_namespace(analysis_ns, path='/api/analysis')
    api.add_namespace(tracks_ns, path='/api/tracks')

    return app

from app import models
