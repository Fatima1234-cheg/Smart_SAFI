"""
API Routes for Smart City - SmartSafi
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required

api_bp = Blueprint('api', __name__)


@api_bp.route('/status')
def status():
    """API - Statut du système"""
    return jsonify({
        'status': 'ok',
        'version': '2.0.0',
        'timestamp': '2024-01-01T00:00:00Z'
    })


@api_bp.route('/sensors/data')
@login_required
def get_sensors_data():
    """API - Données de tous les capteurs"""
    from app.models.waste import Waste
    from app.models.water import Water
    from app.models.air import Air
    from app.models.agriculture import Agriculture
    from app.models.lighting import Lighting
    
    return jsonify({
        'waste': [w.to_dict() for w in Waste.get_all(limit=10)],
        'water': [w.to_dict() for w in Water.get_all(limit=10)],
        'air': [a.to_dict() for a in Air.get_all(limit=10)],
        'agriculture': [a.to_dict() for a in Agriculture.get_all(limit=10)],
        'lighting': [l.to_dict() for l in Lighting.get_all(limit=10)]
    })


@api_bp.route('/stats/global')
@login_required
def get_global_stats():
    """API - Statistiques globales"""
    from app.models.waste import Waste
    from app.models.water import Water
    from app.models.air import Air
    from app.models.agriculture import Agriculture
    from app.models.lighting import Lighting
    
    return jsonify({
        'waste': Waste.get_stats(),
        'water': Water.get_stats(),
        'air': Air.get_stats(),
        'agriculture': Agriculture.get_stats(),
        'lighting': Lighting.get_stats()
    })
