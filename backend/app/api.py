from flask import Blueprint, request, jsonify
from .models import Analysis, Track
from .extensions import db
from .tasks import process_audio_url

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/analysis', methods=['POST'])
def start_analysis():
    """Start a new track analysis."""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Create analysis record
    analysis = Analysis(url=url)
    db.session.add(analysis)
    db.session.commit()
    
    # Start async processing
    process_audio_url.delay(analysis.id)
    
    return jsonify({
        'id': analysis.id,
        'status': 'pending',
        'url': url
    }), 202

@bp.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Get the status and results of an analysis."""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    return jsonify(analysis.to_dict())
