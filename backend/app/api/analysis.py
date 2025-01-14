from flask import jsonify, request
from . import bp
from ..models import Analysis, db
from ..tasks import process_audio_url

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'FlacJacket API is running'}), 200

@bp.route('/analysis', methods=['POST'])
def start_analysis():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url']
    analysis = Analysis(url=url)
    db.session.add(analysis)
    db.session.commit()
    
    # Start async task
    process_audio_url.delay(analysis.id)
    
    return jsonify(analysis.to_dict()), 202

@bp.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    return jsonify(analysis.to_dict())

@bp.route('/analyses', methods=['GET'])
def list_analyses():
    analyses = Analysis.query.order_by(Analysis.created_at.desc()).all()
    return jsonify({'analyses': [analysis.to_dict() for analysis in analyses]})

@bp.route('/analysis/<int:analysis_id>', methods=['DELETE'])
def delete_analysis(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    db.session.delete(analysis)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Analysis deleted successfully'})
