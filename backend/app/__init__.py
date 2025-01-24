from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from .models import db
from .api import bp as api_bp
from .config import Config

def create_app(config=None):
    app = Flask(__name__)
    
    # Load default configuration
    app.config.from_object('app.config.Config')
    
    # Override with any custom config
    if config:
        app.config.update(config)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
