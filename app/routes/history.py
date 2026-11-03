"""
History Routes for Smart City - SmartSafi
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.history import History

history_bp = Blueprint('history', __name__)


@history_bp.route('/')
@login_required
def index():
    """Page d'historique"""
    category = request.args.get('category', 'all')
    level = request.args.get('level', 'all')
    
    query = {}
    if category != 'all':
        query['category'] = category
    if level != 'all':
        query['level'] = level
    
    history = History.get_all(
        category=query.get('category'),
        level=query.get('level'),
        limit=100
    )
    
    return render_template(
        'pages/history/index.html',
        history=history,
        current_category=category,
        current_level=level,
        categories=History.CATEGORIES,
        levels=History.LEVELS
    )


@history_bp.route('/alerts')
@login_required
def alerts():
    """Page d'alertes"""
    return render_template('pages/history/alerts.html')


@history_bp.route('/logs')
@login_required
def logs():
    """Page de logs système"""
    return render_template('pages/history/logs.html')


# API Routes

@history_bp.route('/api/events')
@login_required
def api_get_events():
    """API - Obtenir les événements"""
    category = request.args.get('category')
    level = request.args.get('level')
    limit = request.args.get('limit', 50, type=int)
    
    events = History.get_all(
        category=category,
        level=level,
        limit=limit
    )
    
    return jsonify({
        'success': True,
        'count': len(events),
        'data': [e.to_dict() for e in events]
    })


@history_bp.route('/api/events/<event_id>')
@login_required
def api_get_event(event_id):
    """API - Obtenir un événement par ID"""
    event = History.get_by_id(event_id)
    if not event:
        return jsonify({'success': False, 'message': 'Événement non trouvé'}), 404
    
    return jsonify({
        'success': True,
        'data': event.to_dict()
    })


@history_bp.route('/api/events/<event_id>/read', methods=['POST'])
@login_required
def api_mark_as_read(event_id):
    """API - Marquer un événement comme lu"""
    event = History.get_by_id(event_id)
    if not event:
        return jsonify({'success': False, 'message': 'Événement non trouvé'}), 404
    
    event.mark_as_read(
        user_id=current_user.get_id(),
        user_name=current_user.username
    )
    
    return jsonify({
        'success': True,
        'message': 'Marqué comme lu'
    })


@history_bp.route('/api/unread-count')
@login_required
def api_get_unread_count():
    """API - Obtenir le nombre d'événements non lus"""
    category = request.args.get('category')
    count = History.get_unread_count(category)
    
    return jsonify({
        'success': True,
        'count': count
    })
