"""
Dashboard Routes for Smart City - SmartSafi
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.waste import Waste
from app.models.water import Water
from app.models.air import Air
from app.models.agriculture import Agriculture
from app.models.lighting import Lighting
from app.models.history import History

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Page principale du dashboard"""
    # Statistiques globales
    stats = {
        'waste': Waste.get_stats(),
        'water': Water.get_stats(),
        'air': Air.get_stats(),
        'lighting': Lighting.get_stats()
    }
    
    # Alertes récentes
    alerts = History.get_all(level='warning', limit=5)
    
    # Activités récentes
    activities = History.get_all(limit=10)
    
    return render_template(
        'pages/dashboard/index.html',
        stats=stats,
        alerts=alerts,
        activities=activities,
        user=current_user
    )


@dashboard_bp.route('/overview')
@login_required
def overview():
    """Vue d'ensemble"""
    return render_template('pages/dashboard/overview.html')


@dashboard_bp.route('/stats')
@login_required
def stats():
    """Statistiques globales"""
    return render_template('pages/dashboard/stats.html')


@dashboard_bp.route('/api/summary')
@login_required
def api_summary():
    """API pour les données de résumé du dashboard"""
    summary = {
        'waste': {
            'total_bins': 20,
            'full_bins': 3,
            'collection_needed': True
        },
        'water': {
            'sources_monitored': 3,
            'quality_good': 3,
            'alerts': 0
        },
        'air': {
            'aqi': 85,
            'status': 'moderate',
            'trend': 'stable'
        },
        'agriculture': {
            'zones_monitored': 4,
            'irrigation_needed': 2,
            'health_good': 4
        },
        'lighting': {
            'lights_total': 50,
            'lights_on': 25,
            'faults': 0
        }
    }
    return jsonify(summary)
