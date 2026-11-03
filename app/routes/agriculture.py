"""
Agriculture Routes for Smart City - SmartSafi
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.agriculture import Agriculture
from app.models.history import History

agriculture_bp = Blueprint('agriculture', __name__)


@agriculture_bp.route('/')
@login_required
def index():
    """Page d'agriculture intelligente"""
    zone = request.args.get('zone', 'all')
    
    if zone == 'all':
        measurements = Agriculture.get_all()
    else:
        measurements = Agriculture.get_all(zone=zone)
    
    stats = Agriculture.get_stats(zone if zone != 'all' else None)
    
    return render_template(
        'pages/agriculture/index.html',
        measurements=measurements,
        stats=stats,
        current_zone=zone,
        zones=Agriculture.ZONES
    )


@agriculture_bp.route('/zones')
@login_required
def zones():
    """Gestion des zones agricoles"""
    return render_template('pages/agriculture/zones.html')


@agriculture_bp.route('/irrigation')
@login_required
def irrigation():
    """Gestion de l'irrigation"""
    return render_template('pages/agriculture/irrigation.html')


@agriculture_bp.route('/crops')
@login_required
def crops():
    """Gestion des cultures"""
    return render_template('pages/agriculture/crops.html')


@agriculture_bp.route('/api/measurements')
@login_required
def api_get_measurements():
    """API - Obtenir toutes les mesures"""
    zone = request.args.get('zone')
    limit = request.args.get('limit', type=int)
    measurements = Agriculture.get_all(zone=zone, limit=limit)
    return jsonify({
        'success': True,
        'count': len(measurements),
        'data': [m.to_dict() for m in measurements]
    })


@agriculture_bp.route('/api/stats')
@login_required
def api_get_stats():
    """API - Obtenir les statistiques"""
    zone = request.args.get('zone')
    stats = Agriculture.get_stats(zone)
    return jsonify({
        'success': True,
        'data': stats
    })
