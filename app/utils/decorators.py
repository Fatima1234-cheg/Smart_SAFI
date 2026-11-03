"""
Decorators for Smart City - SmartSafi
"""

from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user


def admin_required(f):
    """Vérifier que l'utilisateur est un administrateur"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def operator_required(f):
    """Vérifier que l'utilisateur est un opérateur ou admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        if current_user.role not in ['admin', 'operator']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def driver_required(f):
    """Vérifier que l'utilisateur est un chauffeur, opérateur ou admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        if current_user.role not in ['admin', 'operator', 'driver']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission):
    """Vérifier que l'utilisateur a une permission spécifique"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if not current_user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def api_key_required(f):
    """Vérifier la clé API pour les requêtes API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return {'error': 'API key required'}, 401
        
        # Vérifier la clé API dans la base de données
        # TODO: Implémenter la vérification réelle
        valid_keys = current_app.config.get('API_KEYS', [])
        if api_key not in valid_keys:
            return {'error': 'Invalid API key'}, 401
        
        return f(*args, **kwargs)
    return decorated_function


def rate_limited(max_requests=100, window=3600):
    """Limiter le taux de requêtes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # TODO: Implémenter la limitation de taux avec Redis
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_action(action_type, description=None):
    """Logger les actions des utilisateurs"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Exécuter la fonction
            result = f(*args, **kwargs)
            
            # Logger l'action
            try:
                from app.models.history import History
                
                user_id = current_user.get_id() if current_user.is_authenticated else None
                user_name = current_user.username if current_user.is_authenticated else 'anonymous'
                
                History.log_event(
                    category='user_action',
                    level='info',
                    title=action_type,
                    message=description or f"Action: {action_type}",
                    user_id=user_id,
                    user_name=user_name,
                    details={'action_type': action_type, 'args': str(kwargs)}
                )
            except Exception as e:
                print(f"Erreur de logging: {e}")
            
            return result
        return decorated_function
    return decorator


def handle_errors(f):
    """Gérer les exceptions de manière uniforme"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Logger l'erreur
            print(f"Erreur dans {f.__name__}: {e}")
            
            # Retourner une réponse d'erreur appropriée
            if request.is_json:
                return {'error': 'Internal server error', 'message': str(e)}, 500
            else:
                flash('Une erreur est survenue. Veuillez réessayer.', 'error')
                return redirect(url_for('main.index'))
    return decorated_function
