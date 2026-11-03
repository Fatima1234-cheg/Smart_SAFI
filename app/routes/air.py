"""
Air Quality Routes for Smart City - SmartSafi
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.air import Air
from app.models.history import History

air_bp = Blueprint('air', __name__)


@air_bp.route('/')
@login_required
def index():
    """Page de qualité de l'air"""
    station = request.args.get('station', 'all')
    
    if station == 'all':
        measurements = Air.get_all()
    else:
        measurements = Air.get_all(station=station)
    
    stats = Air.get_stats(station if station != 'all' else None)
    
    return render_template(
        'pages/air/index.html',
        measurements=measurements,
        stats=stats,
        current_station=station,
        stations=Air.STATIONS
    )


@air_bp.route('/stations')
@login_required
def stations():
    """Liste des stations"""
    return render_template('pages/air/stations.html')


@air_bp.route('/forecasts')
@login_required
def forecasts():
    """Prévisions de qualité de l'air"""
    return render_template('pages/air/forecasts.html')


@air_bp.route('/api/measurements')
@login_required
def api_get_measurements():
    """API - Obtenir toutes les mesures"""
    station = request.args.get('station')
    limit = request.args.get('limit', type=int)
    measurements = Air.get_all(station=station, limit=limit)
    return jsonify({
        'success': True,
        'count': len(measurements),
        'data': [m.to_dict() for m in measurements]
    })


@air_bp.route('/api/stats')
@login_required
def api_get_stats():
    """API - Obtenir les statistiques"""
    station = request.args.get('station')
    stats = Air.get_stats(station)
    return jsonify({
        'success': True,
        'data': stats
    })
