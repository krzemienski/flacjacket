from flask import Blueprint
from flask_restx import Api

bp = Blueprint('api', __name__)
api = Api(bp,
          title='FlacJacket API',
          version='1.0',
          description='API for analyzing and extracting tracks from audio files',
          doc='/docs'
)

# Import namespaces after api is created
from .auth import api as auth_ns
from .analysis import api as analysis_ns
from .tracks import api as tracks_ns

# Add namespaces
api.add_namespace(auth_ns)
api.add_namespace(analysis_ns)
api.add_namespace(tracks_ns)
