"""
SmartSafi - Flask Application Factory

This module implements the Application Factory pattern for creating Flask
applications. This pattern allows for multiple app instances with different
configurations, making testing and modularity easier.

Usage:
    from app import create_app
    
    # Create app with specific configuration
    app = create_app('development')
    
    # Or use environment variable
    app = create_app()

Architecture:
    - Extensions are initialized in init_extensions()
    - Blueprints are registered in register_blueprints()
    - Error handlers are set up in register_error_handlers()
    - CLI commands are registered in register_cli_commands()
"""

import os
import logging
import sys
from datetime import datetime
from typing import Optional

from flask import Flask, render_template, request, g, jsonify
from flask_login import LoginManager
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from jinja2 import ChoiceLoader, FileSystemLoader

from config import get_config


# Initialize Flask extensions (not bound to any app yet)
# These will be properly initialized in init_extensions()
mongo = PyMongo()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
cors = CORS()


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Application Factory - creates and configures a Flask application instance.
    
    This function implements the Application Factory pattern, allowing for
    multiple app instances with different configurations. This is useful
    for testing, modularity, and different deployment scenarios.
    
    Args:
        config_name: The configuration name (development, production, testing).
                    If None, uses the FLASK_ENV environment variable.
    
    Returns:
        A fully configured Flask application instance.
    
    Example:
        # Create development app
        app = create_app('development')
        
        # Create app from environment variable
        app = create_app()
        
        # Run the app
        app.run()
    """
    # Create Flask app instance
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates',
        instance_relative_config=False
    )
    legacy_templates = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    app.jinja_loader = ChoiceLoader([
        app.jinja_loader,
        FileSystemLoader(legacy_templates),
    ])
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Validate critical configuration settings
    if app.config.get('ENV') == 'production' or app.config.get('FLASK_ENV') == 'production':
        # In production, ensure SECRET_KEY is set and not the default
        secret_key = app.config.get('SECRET_KEY')
        if not secret_key or secret_key == 'dev-secret-key-change-in-production':
            raise ValueError(
                "SECRET_KEY must be set to a secure random value in production! "
                "Set the SECRET_KEY environment variable."
            )
    
    # Ensure logs directory exists
    _ensure_logs_directory()
    
    # Configure logging
    _configure_logging(app)
    
    # Log application startup
    app.logger.info(f"SmartSafi {app.config.get('APP_VERSION', '1.0.0')} starting...")
    app.logger.info(f"Configuration: {app.config.get('FLASK_ENV', 'unknown')}")
    
    # Initialize Flask extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters and context processors
    register_template_functions(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Register before/after request handlers
    register_request_handlers(app)
    
    # Log successful initialization
    app.logger.info("SmartSafi application initialized successfully!")
    
    return app


def _ensure_logs_directory() -> None:
    """Ensure the logs directory exists."""
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)


def _configure_logging(app: Flask) -> None:
    """
    Configure logging for the application.
    
    Args:
        app: The Flask application instance.
    """
    log_level = getattr(
        logging,
        app.config.get('LOG_LEVEL', 'INFO').upper(),
        logging.INFO
    )
    
    log_format = app.config.get(
        'LOG_FORMAT',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure basic logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Add file handler if configured
    log_file = app.config.get('LOG_FILE')
    if log_file:
        from logging.handlers import RotatingFileHandler
        
        # Ensure the log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=app.config.get('LOG_MAX_BYTES', 10485760),  # 10MB
            backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        app.logger.addHandler(file_handler)


def init_extensions(app: Flask) -> None:
    """
    Initialize Flask extensions.
    
    Args:
        app: The Flask application instance.
    """
    # Initialize MongoDB
    mongo.init_app(app)
    
    # Initialize Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    # Initialize Mail
    mail.init_app(app)
    
    # Initialize CSRF Protection
    csrf.init_app(app)
    
    # Initialize Rate Limiter
    if app.config.get('RATELIMIT_ENABLED', True):
        limiter.init_app(app)
    
    # Initialize CORS
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })


def register_blueprints(app: Flask) -> None:
    """
    Register Flask blueprints.
    
    Args:
        app: The Flask application instance.
    """
    # Import blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.api import api_bp
    from app.routes.waste import waste_bp
    from app.routes.water import water_bp
    from app.routes.air import air_bp
    from app.routes.agriculture import agriculture_bp
    from app.routes.lighting import lighting_bp
    from app.routes.history import history_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(waste_bp, url_prefix='/waste')
    app.register_blueprint(water_bp, url_prefix='/water')
    app.register_blueprint(air_bp, url_prefix='/air')
    app.register_blueprint(agriculture_bp, url_prefix='/agriculture')
    app.register_blueprint(lighting_bp, url_prefix='/lighting')
    app.register_blueprint(history_bp, url_prefix='/history')
    app.add_url_rule(
        '/login',
        endpoint='legacy_login',
        view_func=app.view_functions['auth.login'],
        methods=['GET', 'POST']
    )
    
    app.logger.info(f"Registered {len(app.blueprints)} blueprints")


def register_error_handlers(app: Flask) -> None:
    """
    Register error handlers.
    
    Args:
        app: The Flask application instance.
    """
    def render_error(error, status_code: int, json_title: str, page_title: str, message: str):
        if request.is_json:
            json_message = message if status_code == 500 else str(error)
            return jsonify({'error': json_title, 'message': json_message}), status_code
        return render_template(
            'errors/error.html',
            status_code=status_code,
            title=page_title,
            message=message
        ), status_code

    @app.errorhandler(400)
    def bad_request(error):
        return render_error(error, 400, 'Bad Request', 'Requête incorrecte', str(error))

    @app.errorhandler(403)
    def forbidden(error):
        return render_error(error, 403, 'Forbidden', 'Accès interdit', 'Vous ne disposez pas des droits nécessaires.')

    @app.errorhandler(404)
    def not_found(error):
        return render_error(error, 404, 'Not Found', 'Page introuvable', 'La page demandée n’existe pas.')

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}', exc_info=True)
        return render_error(
            error,
            500,
            'Internal Server Error',
            'Erreur interne',
            'Une erreur inattendue s’est produite.'
        )


def register_template_functions(app: Flask) -> None:
    """
    Register template filters and context processors.
    
    Args:
        app: The Flask application instance.
    """
    # Context processors
    @app.context_processor
    def inject_globals():
        return {
            'app_name': app.config.get('APP_NAME', 'SmartSafi'),
            'app_version': app.config.get('APP_VERSION', '1.0.0'),
            'current_year': datetime.now().year
        }
    
    # Template filters
    @app.template_filter('format_datetime')
    def format_datetime_filter(value, format='%d/%m/%Y %H:%M'):
        if value is None:
            return ''
        if isinstance(value, str):
            from dateutil import parser
            value = parser.parse(value)
        return value.strftime(format)
    
    @app.template_filter('format_date')
    def format_date_filter(value, format='%d/%m/%Y'):
        if value is None:
            return ''
        if isinstance(value, str):
            from dateutil import parser
            value = parser.parse(value)
        return value.strftime(format)
    
    @app.template_filter('format_number')
    def format_number_filter(value, decimals=2):
        if value is None:
            return ''
        try:
            return f'{float(value):,.{decimals}f}'
        except (ValueError, TypeError):
            return str(value)
    
    @app.template_filter('percentage')
    def percentage_filter(value, decimals=1):
        if value is None:
            return '0%';
        try:
            return f'{float(value) * 100:.{decimals}f}%'
        except (ValueError, TypeError):
            return '0%';


def register_cli_commands(app: Flask) -> None:
    """
    Register CLI commands.
    
    Args:
        app: The Flask application instance.
    """
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database (create collections and indexes)."""
        from app.models.user import User
        from app.models.waste import Waste
        from app.models.water import Water
        from app.models.air import Air
        from app.models.agriculture import Agriculture
        from app.models.lighting import Lighting
        from app.models.history import History
        
        click.echo('Initializing database...')
        
        # Create indexes (handled by each model's init method)
        # This is where you would add custom index creation if needed
        
        click.echo('Database initialized successfully!')
    
    @app.cli.command('create-admin')
    @click.option('--username', default='admin', help='Admin username')
    @click.option('--email', default='admin@smartsafi.com', help='Admin email')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(username, email, password):
        """Create an admin user."""
        from app.models.user import User
        
        click.echo(f'Creating admin user: {username}')
        
        # Check if user already exists
        existing_user = User.find_by_username(username)
        if existing_user:
            click.echo(f'Error: User "{username}" already exists!')
            return
        
        # Create the admin user
        user = User.create(
            username=username,
            email=email,
            password=password,
            role='admin',
            is_active=True
        )
        
        click.echo(f'Admin user "{username}" created successfully!')
    
    @app.cli.command('seed-data')
    def seed_data():
        """Seed the database with sample data."""
        from app.utils.seed import seed_all
        
        click.echo('Seeding database with sample data...')
        seed_all()
        click.echo('Database seeded successfully!')
    
    @app.cli.command('backup-db')
    @click.option('--output', default='backups', help='Backup output directory')
    def backup_db(output):
        """Backup the database."""
        import subprocess
        from datetime import datetime
        
        # Ensure output directory exists
        if not os.path.exists(output):
            os.makedirs(output)
        
        # Generate backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(output, f'smartsafi_backup_{timestamp}.gz')
        
        # Get MongoDB URI from config
        mongo_uri = app.config.get('MONGO_URI', 'mongodb://localhost:27017/smartsafi')
        db_name = app.config.get('MONGO_DB_NAME', 'smartsafi')
        
        click.echo(f'Creating backup: {backup_file}')
        
        # Run mongodump
        try:
            cmd = [
                'mongodump',
                '--uri', mongo_uri,
                '--db', db_name,
                '--gzip',
                '--archive=' + backup_file
            ]
            subprocess.run(cmd, check=True)
            click.echo(f'Backup created successfully: {backup_file}')
        except subprocess.CalledProcessError as e:
            click.echo(f'Error creating backup: {e}')
        except FileNotFoundError:
            click.echo('Error: mongodump not found. Please install MongoDB tools.')


def register_request_handlers(app: Flask) -> None:
    """
    Register before and after request handlers.
    
    Args:
        app: The Flask application instance.
    """
    @app.before_request
    def before_request():
        """Run before each request."""
        g.start_time = datetime.now()
    
    @app.after_request
    def after_request(response):
        """Run after each request."""
        # Calculate request duration
        if hasattr(g, 'start_time'):
            duration = (datetime.now() - g.start_time).total_seconds()
            response.headers['X-Response-Time'] = f'{duration:.3f}s'
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


# Import User model for login manager
@login_manager.user_loader
def load_user(user_id: str):
    """
    Load user by ID for Flask-Login.
    
    Args:
        user_id: The user's ID as a string.
    
    Returns:
        The User instance or None if not found.
    """
    from app.models.user import User
    return User.find_by_id(user_id)


# Import click for CLI commands
try:
    import click
except ImportError:
    # click is not available, CLI commands won't work
    pass
