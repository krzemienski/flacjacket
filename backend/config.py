import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    
    # Audio fingerprinting configuration
    ACOUSTID_API_KEY = os.environ.get('ACOUSTID_API_KEY')
    
    # Dejavu MySQL configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'dejavu')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'dejavu')
    
    # Audfprint configuration
    AUDFPRINT_DB_PATH = os.path.join(basedir, 'audfprint_reference.pklz')
    
    # Ensure required directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
