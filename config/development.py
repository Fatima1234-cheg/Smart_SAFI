"""
SmartSafi - Development Configuration

This module contains the configuration settings for the development environment.
These settings are optimized for local development and debugging.

Characteristics:
- Debug mode enabled for detailed error pages
- Verbose logging for troubleshooting
- Development-specific tools enabled (debug toolbar, etc.)
- Local database and services
- Relaxed security settings for convenience

Note: Never use these settings in production!
"""

from config.base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """
    Development environment configuration.
    
    This configuration is optimized for local development with
    debugging tools enabled and verbose logging.
    
    WARNING: These settings are insecure and should NEVER be used
    in a production environment!
    """
    
    # =========================================================================
    # Flask Core Settings
    # =========================================================================
    
    DEBUG: bool = True
    """Enable Flask debug mode for detailed error pages and auto-reload."""
    
    TESTING: bool = False
    """Testing mode is disabled by default in development."""
    
    FLASK_ENV: str = 'development'
    """Explicitly set Flask environment to development."""
    
    # =========================================================================
    # Security Settings (Relaxed for Development)
    # =========================================================================
    
    # Use a predictable secret key for development (NOT SECURE!)
    SECRET_KEY: str = 'dev-secret-key-for-development-only-do-not-use-in-production'
    """
    Development secret key.
    
    WARNING: This is a predictable key for development convenience only!
    Always use a strong random key in production.
    """
    
    # Allow HTTP cookies in development
    SESSION_COOKIE_SECURE: bool = False
    """Allow session cookies over HTTP for local development."""
    
    REMEMBER_COOKIE_SECURE: bool = False
    """Allow remember me cookies over HTTP for local development."""
    
    # =========================================================================
    # Database Configuration
    # =========================================================================
    
    # Use local MongoDB instance
    MONGO_URI: str = 'mongodb://localhost:27017/smartsafi_dev'
    """MongoDB connection URI for development database."""
    
    MONGO_DB_NAME: str = 'smartsafi_dev'
    """Development database name."""
    
    # Smaller connection pool for development
    MONGO_MIN_POOL_SIZE: int = 1
    """Minimum connection pool size (reduced for development)."""
    
    MONGO_MAX_POOL_SIZE: int = 10
    """Maximum connection pool size (reduced for development)."""
    
    # =========================================================================
    # MQTT Configuration
    # =========================================================================
    
    # Use local MQTT broker
    MQTT_BROKER_HOST: str = 'localhost'
    """Local MQTT broker for development."""
    
    MQTT_BROKER_PORT: int = 1883
    """Standard MQTT port."""
    
    # Reconnect aggressively in development
    MQTT_RECONNECT_DELAY: int = 1
    """Quick reconnection delay for development."""
    
    MQTT_RECONNECT_DELAY_MAX: int = 10
    """Maximum reconnection delay for development."""
    
    # =========================================================================
    # Email Configuration
    # =========================================================================
    
    # Use Mailtrap or similar for development
    MAIL_SERVER: str = 'localhost'
    """Local SMTP server for development."""
    
    MAIL_PORT: int = 1025
    """Alternative SMTP port for development."""
    
    MAIL_USE_TLS: bool = False
    """TLS disabled for local development."""
    
    MAIL_SUPPRESS_SEND: bool = True
    """Suppress email sending in development (log only)."""
    
    # =========================================================================
    # Logging Configuration
    # =========================================================================
    
    LOG_LEVEL: str = 'DEBUG'
    """Verbose logging level for development."""
    
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    """Detailed log format including file and line number."""
    
    # =========================================================================
    # Rate Limiting
    # =========================================================================
    
    RATELIMIT_ENABLED: bool = False
    """Disable rate limiting for development convenience."""
    
    # =========================================================================
    # Development Tools
    # =========================================================================
    
    # Enable Flask-DebugToolbar if installed
    DEBUG_TB_ENABLED: bool = True
    """Enable Flask-DebugToolbar for development."""
    
    DEBUG_TB_INTERCEPT_REDIRECTS: bool = False
    """Don't intercept redirects in debug toolbar."""
    
    DEBUG_TB_PROFILER_ENABLED: bool = False
    """Disable profiler by default (can be enabled per-request)."""
    
    # Enable automatic template reloading
    TEMPLATES_AUTO_RELOAD: bool = True
    """Automatically reload templates when they change."""
    
    # Explain template loading for debugging
    EXPLAIN_TEMPLATE_LOADING: bool = False
    """Explain template loading (useful for debugging template issues)."""
