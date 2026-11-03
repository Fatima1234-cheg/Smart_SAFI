#!/usr/bin/env python3
"""
SmartSafi - Smart City Platform
WSGI Entry Point for Production Deployment

This module provides the WSGI application entry point for production servers
like Gunicorn, uWSGI, or Apache with mod_wsgi.

Usage with Gunicorn:
    gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application

Usage with uWSGI:
    uwsgi --http 0.0.0.0:8000 --wsgi-file wsgi.py --callable application --processes 4

Usage with Apache mod_wsgi:
    Add to Apache config: WSGIScriptAlias / /path/to/wsgi.py

Environment Variables:
    FLASK_ENV: Set to 'production' for production deployment
    CONFIG_NAME: Configuration name (development, production, testing)
    GUNICORN_WORKERS: Number of Gunicorn worker processes
    GUNICORN_BIND: Bind address and port
"""

import os
import sys
import logging
from typing import Optional

# Add the project directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Ensure logs directory exists
logs_dir = os.path.join(project_root, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir, exist_ok=True)

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(logs_dir, 'wsgi.log'),
            encoding='utf-8'
        ),
        logging.FileHandler(
            os.path.join(logs_dir, 'application.log'),
            encoding='utf-8'
        )
    ]
)

logger = logging.getLogger(__name__)

# Log startup information
logger.info("=" * 60)
logger.info("SmartSafi WSGI Application Starting")
logger.info("=" * 60)
logger.info(f"Project Root: {project_root}")
logger.info(f"Python Version: {sys.version}")
logger.info(f"Platform: {sys.platform}")

# Determine configuration from environment
def get_config_name() -> str:
    """
    Determine the configuration name from environment variables.
    
    Returns:
        Configuration name (development, production, testing)
    """
    config_name = os.getenv('CONFIG_NAME', os.getenv('FLASK_ENV', 'production'))
    
    # Validate configuration name
    valid_configs = ['development', 'production', 'testing']
    if config_name not in valid_configs:
        logger.warning(f"Invalid config '{config_name}', using 'production'")
        return 'production'
    
    return config_name

# Import and create Flask application
try:
    from app import create_app
    
    config_name = get_config_name()
    logger.info(f"Creating application with '{config_name}' configuration")
    
    # Create the Flask application
    application = create_app(config_name)
    
    # Get configuration for logging
    config = application.config
    logger.info(f"Application Name: {config.get('APP_NAME', 'SmartSafi')}")
    logger.info(f"Application Version: {config.get('APP_VERSION', '1.0.0')}")
    logger.info(f"Debug Mode: {config.get('DEBUG', False)}")
    logger.info(f"Testing Mode: {config.get('TESTING', False)}")
    
    # Application factory function for Gunicorn
    def app():
        """WSGI application factory for Gunicorn."""
        return application
    
    # Also make the application available as 'app' for some WSGI servers
    app = application
    
    logger.info("WSGI Application created successfully")
    logger.info("=" * 60)
    
except ImportError as e:
    logger.error(f"Failed to import application: {e}")
    logger.error("Ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    logger.error(f"Failed to create application: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)


# Gunicorn configuration variables (used when running with Gunicorn)
# These can be overridden using environment variables or command-line arguments
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
workers = int(os.getenv('GUNICORN_WORKERS', 4))
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'sync')
worker_connections = int(os.getenv('GUNICORN_WORKER_CONNECTIONS', 1000))
timeout = int(os.getenv('GUNICORN_TIMEOUT', 30))
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', 2))
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
proc_name = os.getenv('GUNICORN_PROC_NAME', 'smartsafi')
