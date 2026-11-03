"""
Lighting Routes for Smart City - SmartSafi
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.lighting import Lighting
from app.models.history import History

lighting_bp = Blueprint('lighting', __name__)


@lighting_bp.route('/')
@login_required
def index():
    """Page de gestion de l'éclairage"""
    district = request.args.get('district', 'all')
    
    if district == 'all':
        lights = Lighting.get_all()
    else:
        lights = Lighting.get_all(district=district)
    
    stats = Lighting.get_stats(district if district != 'all' else None)
    
    return render_template(
        'pages/lighting/index.html',
        lights=lights,
        stats=stats,
        current_district=district,
        districts=Lighting.DISTRICTS
    )


@lighting_bp.route('/map')
@login_required
def map_view():
    """Vue carte des lampadaires"""
    lights = Lighting.get_all()
    return render_template('pages/lighting/map.html', lights=lights)


@lighting_bp.route('/schedule')
@login_required
def schedule():
    """Planification de l'éclairage"""
    return render_template('pages/lighting/schedule.html')


@lighting_bp.route('/energy')
@login_required
def energy():
    """Consommation énergétique"""
    return render_template('pages/lighting/energy.html')


@lighting_bp.route('/api/lights')
@login_required
def api_get_lights():
    """API - Obtenir tous les lampadaires"""
    district = request.args.get('district')
    limit = request.args.get('limit', type=int)
    lights = Lighting.get_all(district=district, limit=limit)
    return jsonify({
        'success': True,
        'count': len(lights),
        'data': [light.to_dict() for light in lights]
    })


@lighting_bp.route('/api/lights/<light_id>/control', methods=['POST'])
@login_required
def api_control_light(light_id):
    """API - Contrôler un lampadaire"""
    light = Lighting.get_by_id(light_id)
    if not light:
        return jsonify({'success': False, 'message': 'Lampadaire non trouvé'}), 404
    
    data = request.get_json()
    action = data.get('action')
    
    try:
        if action == 'on':
            brightness = data.get('brightness', 100)
            light.turn_on(brightness)
            message = f'Lampadaire allumé à {brightness}%'
        elif action == 'off':
            light.turn_off()
            message = 'Lampadaire éteint'
        elif action == 'brightness':
            brightness = data.get('brightness', 50)
            light.adjust_brightness(brightness)
            message = f'Luminosité ajustée à {brightness}%'
        else:
            return jsonify({'success': False, 'message': 'Action non reconnue'}), 400
        
        # Log the action
        History.log_event(
            category='lighting',
            level='info',
            title='Contrôle éclairage',
            message=message,
            user_id=current_user.get_id(),
            user_name=current_user.username,
            entity_id=light._id,
            entity_type='lighting',
            details={'action': action}
        )
        
        return jsonify({
            'success': True,
            'message': message,
            'data': light.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@lighting_bp.route('/api/stats')
@login_required
def api_get_stats():
    """API - Obtenir les statistiques"""
    district = request.args.get('district')
    stats = Lighting.get_stats(district)
    return jsonify({
        'success': True,
        'data': stats
    })
