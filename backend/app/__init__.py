from flask import Flask
from flask_cors import CORS
from .extensions import db, migrate, celery
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    celery.conf.update(app.config)

    # Register blueprints
    from .api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
