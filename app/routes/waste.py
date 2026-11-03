"""
Waste Management Routes for Smart City - SmartSafi
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.waste import Waste
from app.models.history import History
from app.services.optimization_service import optimize_routes

waste_bp = Blueprint('waste', __name__)


@waste_bp.route('/')
@login_required
def index():
    """Page de gestion des déchets"""
    region = request.args.get('region', 'all')
    
    if region == 'all':
        bins = Waste.get_all()
    else:
        bins = Waste.get_all(region=region)
    
    stats = Waste.get_stats(region if region != 'all' else None)
    region_stats = Waste.get_region_stats()
    
    return render_template(
        'pages/waste/index.html',
        bins=bins,
        stats=stats,
        region_stats=region_stats,
        current_region=region,
        regions=Waste.REGIONS
    )


@waste_bp.route('/map')
@login_required
def map_view():
    """Vue carte des poubelles"""
    bins = Waste.get_all()
    return render_template('pages/waste/map.html', bins=bins)


@waste_bp.route('/route-optimization')
@login_required
def route_optimization():
    """Optimisation des routes de collecte"""
    # Obtenir les poubelles pleines
    full_bins = Waste.get_all(status='full')
    
    # Optimiser les routes
    optimized_routes = optimize_routes(full_bins)
    
    return render_template(
        'pages/waste/route_optimization.html',
        routes=optimized_routes,
        full_bins=full_bins
    )


@waste_bp.route('/collection-schedule')
@login_required
def collection_schedule():
    """Planning des collectes"""
    return render_template('pages/waste/collection_schedule.html')


@waste_bp.route('/reports')
@login_required
def reports():
    """Rapports de gestion des déchets"""
    return render_template('pages/waste/reports.html')


# API Routes

@waste_bp.route('/api/bins')
@login_required
def api_get_bins():
    """API - Obtenir toutes les poubelles"""
    region = request.args.get('region')
    bins = Waste.get_all(region=region)
    return jsonify({
        'success': True,
        'count': len(bins),
        'data': [bin.to_dict() for bin in bins]
    })


@waste_bp.route('/api/bins/<bin_id>')
@login_required
def api_get_bin(bin_id):
    """API - Obtenir une poubelle par ID"""
    bin_obj = Waste.get_by_id(bin_id)
    if not bin_obj:
        return jsonify({'success': False, 'message': 'Poubelle non trouvée'}), 404
    return jsonify({
        'success': True,
        'data': bin_obj.to_dict()
    })


@waste_bp.route('/api/bins', methods=['POST'])
@login_required
def api_create_bin():
    """API - Créer une nouvelle poubelle"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Données requises'}), 400
    
    try:
        new_bin = Waste.create(data)
        
        # Log the action
        History.log_event(
            category='waste',
            level='info',
            title='Poubelle créée',
            message=f"Nouvelle poubelle créée: {new_bin.bin_id}",
            user_id=current_user.get_id(),
            user_name=current_user.username,
            entity_id=new_bin._id,
            entity_type='waste'
        )
        
        return jsonify({
            'success': True,
            'message': 'Poubelle créée avec succès',
            'data': new_bin.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@waste_bp.route('/api/bins/<bin_id>', methods=['PUT'])
@login_required
def api_update_bin(bin_id):
    """API - Mettre à jour une poubelle"""
    bin_obj = Waste.get_by_id(bin_id)
    if not bin_obj:
        return jsonify({'success': False, 'message': 'Poubelle non trouvée'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Données requises'}), 400
    
    try:
        updated_bin = Waste.update(bin_id, data)
        
        # Log the action
        History.log_event(
            category='waste',
            level='info',
            title='Poubelle mise à jour',
            message=f"Poubelle {updated_bin.bin_id} mise à jour",
            user_id=current_user.get_id(),
            user_name=current_user.username,
            entity_id=updated_bin._id,
            entity_type='waste'
        )
        
        return jsonify({
            'success': True,
            'message': 'Poubelle mise à jour avec succès',
            'data': updated_bin.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@waste_bp.route('/api/bins/<bin_id>/collect', methods=['POST'])
@login_required
def api_collect_bin(bin_id):
    """API - Marquer une poubelle comme collectée"""
    bin_obj = Waste.get_by_id(bin_id)
    if not bin_obj:
        return jsonify({'success': False, 'message': 'Poubelle non trouvée'}), 404
    
    try:
        from datetime import datetime
        data = {
            'fill_level': 0,
            'status': 'normal',
            'last_collection': datetime.utcnow()
        }
        updated_bin = Waste.update(bin_id, data)
        
        # Log the action
        History.log_event(
            category='waste',
            level='info',
            title='Poubelle collectée',
            message=f"Poubelle {updated_bin.bin_id} collectée",
            user_id=current_user.get_id(),
            user_name=current_user.username,
            entity_id=updated_bin._id,
            entity_type='waste'
        )
        
        return jsonify({
            'success': True,
            'message': 'Poubelle collectée avec succès',
            'data': updated_bin.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@waste_bp.route('/api/stats')
@login_required
def api_get_stats():
    """API - Obtenir les statistiques des déchets"""
    region = request.args.get('region')
    stats = Waste.get_stats(region)
    return jsonify({
        'success': True,
        'data': stats
    })


@waste_bp.route('/api/region-stats')
@login_required
def api_get_region_stats():
    """API - Obtenir les statistiques par région"""
    stats = Waste.get_region_stats()
    return jsonify({
        'success': True,
        'data': stats
    })
