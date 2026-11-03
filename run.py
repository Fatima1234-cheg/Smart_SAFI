#!/usr/bin/env python3
"""
SmartSafi - Smart City Platform
Development Entry Point

This script starts the Flask development server with the SmartSafi application.
For production deployment, use wsgi.py with a production WSGI server like Gunicorn.

Usage:
    python run.py                          # Start with default settings
    python run.py --host 0.0.0.0 --port 8080  # Custom host and port
    python run.py --debug                  # Enable debug mode explicitly
    flask run                              # Using Flask CLI

Environment Variables:
    FLASK_APP: Path to the Flask application (default: run.py)
    FLASK_ENV: Environment mode (development, production, testing)
    FLASK_DEBUG: Enable debug mode (1 or 0)
    PORT: Port number to bind (default: 5000)
"""

import os
import sys
import argparse
import logging
from typing import Optional

# Add the project directory to the path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app
from app.services.mqtt_service import mqtt_client
from config import get_config


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the development server.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join('logs', 'development.log'), encoding='utf-8')
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the development server.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='SmartSafi - Smart City Platform Development Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                           # Default: localhost:5000
  python run.py --host 0.0.0.0 --port 8080 # Bind to all interfaces on port 8080
  python run.py --debug                    # Enable debug mode
  python run.py --no-mqtt                  # Start without MQTT service
        """
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default=os.getenv('HOST', '127.0.0.1'),
        help='Host to bind to (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.getenv('PORT', 5000)),
        help='Port to bind to (default: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        default=os.getenv('FLASK_DEBUG', '0') == '1',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--no-mqtt',
        action='store_true',
        help='Start without MQTT service'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default=os.getenv('LOG_LEVEL', 'INFO'),
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )
    
    return parser.parse_args()


def create_logs_directory() -> None:
    """Create the logs directory if it doesn't exist."""
    logs_dir = os.path.join(project_root, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"Created logs directory: {logs_dir}")


def main() -> None:
    """
    Main entry point for the development server.
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Create logs directory
    create_logs_directory()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Log startup information
    logger.info("=" * 60)
    logger.info("SmartSafi - Smart City Platform")
    logger.info("=" * 60)
    logger.info(f"Starting development server...")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Debug: {args.debug}")
    logger.info(f"Log Level: {args.log_level}")
    
    # Set environment variables
    os.environ['FLASK_DEBUG'] = '1' if args.debug else '0'
    os.environ['FLASK_ENV'] = 'development' if args.debug else 'production'
    
    # Create Flask application
    try:
        config_name = 'development' if args.debug else 'production'
        app = create_app(config_name)
        logger.info(f"Flask application created with '{config_name}' configuration")
    except Exception as e:
        logger.error(f"Failed to create Flask application: {e}")
        sys.exit(1)
    
    # Start MQTT service if not disabled
    if not args.no_mqtt:
        try:
            logger.info("Starting MQTT service...")
            mqtt_client.init_app(app)
            mqtt_client.start()
            logger.info("MQTT service started successfully")
        except Exception as e:
            logger.warning(f"Failed to start MQTT service: {e}")
            logger.warning("Application will continue without MQTT functionality")
    else:
        logger.info("MQTT service disabled by user")
    
    # Display access URLs
    print("\n" + "=" * 60)
    print(" SmartSafi - Smart City Platform")
    print("=" * 60)
    print(f" Server running at: http://{args.host}:{args.port}")
    print(f" Debug mode: {'Enabled' if args.debug else 'Disabled'}")
    print("")
    print(" URLs:")
    print(f"  - Home:        http://{args.host}:{args.port}/")
    print(f"  - Login:       http://{args.host}:{args.port}/auth/login")
    print(f"  - Dashboard:   http://{args.host}:{args.port}/dashboard")
    print(f"  - API Docs:    http://{args.host}:{args.port}/api/docs")
    print("=" * 60 + "\n")
    
    # Run the Flask development server
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=args.debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("\nReceived keyboard interrupt, shutting down...")
    finally:
        # Cleanup
        if not args.no_mqtt and mqtt_client.connected:
            logger.info("Stopping MQTT service...")
            mqtt_client.stop()
        
        logger.info("Server stopped")
        logger.info("=" * 60)


if __name__ == '__main__':
    main()
