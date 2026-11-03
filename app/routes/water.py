"""
Water Management Routes for Smart City - SmartSafi
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.water import Water
from app.models.history import History

water_bp = Blueprint('water', __name__)


@water_bp.route('/')
@login_required
def index():
    """Page de gestion de l'eau"""
    source = request.args.get('source', 'all')
    
    if source == 'all':
        measurements = Water.get_all()
    else:
        measurements = Water.get_all(source=source)
    
    stats = Water.get_stats(source if source != 'all' else None)
    source_stats = Water.get_source_stats()
    
    return render_template(
        'pages/water/index.html',
        measurements=measurements,
        stats=stats,
        source_stats=source_stats,
        current_source=source,
        sources=Water.SOURCES
    )


@water_bp.route('/map')
@login_required
def map_view():
    """Vue carte des sources d'eau"""
    measurements = Water.get_all()
    return render_template('pages/water/map.html', measurements=measurements)


@water_bp.route('/quality')
@login_required
def quality():
    """Qualité de l'eau"""
    return render_template('pages/water/quality.html')


@water_bp.route('/treatment')
@login_required
def treatment():
    """Stations de traitement"""
    return render_template('pages/water/treatment.html')


@water_bp.route('/reports')
@login_required
def reports():
    """Rapports sur l'eau"""
    return render_template('pages/water/reports.html')


# API Routes

@water_bp.route('/api/measurements')
@login_required
def api_get_measurements():
    """API - Obtenir toutes les mesures"""
    source = request.args.get('source')
    limit = request.args.get('limit', type=int)
    measurements = Water.get_all(source=source, limit=limit)
    return jsonify({
        'success': True,
        'count': len(measurements),
        'data': [m.to_dict() for m in measurements]
    })


@water_bp.route('/api/measurements/<measurement_id>')
@login_required
def api_get_measurement(measurement_id):
    """API - Obtenir une mesure par ID"""
    measurement = Water.get_by_id(measurement_id)
    if not measurement:
        return jsonify({'success': False, 'message': 'Mesure non trouvée'}), 404
    return jsonify({
        'success': True,
        'data': measurement.to_dict()
    })


@water_bp.route('/api/measurements', methods=['POST'])
@login_required
def api_create_measurement():
    """API - Créer une nouvelle mesure"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Données requises'}), 400
    
    try:
        new_measurement = Water.create(data)
        
        History.log_event(
            category='water',
            level='info',
            title='Mesure eau créée',
            message=f"Nouvelle mesure créée pour la source {new_measurement.source}",
            user_id=current_user.get_id(),
            user_name=current_user.username,
            entity_id=new_measurement._id,
            entity_type='water'
        )
        
        return jsonify({
            'success': True,
            'message': 'Mesure créée avec succès',
            'data': new_measurement.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@water_bp.route('/api/stats')
@login_required
def api_get_stats():
    """API - Obtenir les statistiques"""
    source = request.args.get('source')
    stats = Water.get_stats(source)
    return jsonify({
        'success': True,
        'data': stats
    })
