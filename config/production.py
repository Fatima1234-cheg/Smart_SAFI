"""
SmartSafi - Production Configuration

This module contains the configuration settings for production deployment.
These settings prioritize security, performance, and reliability.

Characteristics:
- Debug mode disabled for security
- Strict security settings (HTTPS, secure cookies, etc.)
- Production-grade logging and monitoring
- Connection pooling and caching for performance
- Error handling without sensitive information exposure

Security Considerations:
- All secret keys and passwords must be set via environment variables
- HTTPS is enforced (cookies are secure-only)
- Debug mode is disabled
- Detailed error messages are hidden from users
"""

import os
from datetime import timedelta
from config.base import BaseConfig


class ProductionConfig(BaseConfig):
    """
    Production environment configuration.
    
    This configuration is optimized for production deployment with
    strict security settings, performance optimizations, and
    comprehensive logging.
    
    WARNING: Ensure all security-related environment variables are set
    before deploying to production!
    """
    
    # =========================================================================
    # Flask Core Settings
    # =========================================================================
    
    DEBUG: bool = False
    """Debug mode is disabled in production for security."""
    
    TESTING: bool = False
    """Testing mode is disabled in production."""
    
    FLASK_ENV: str = 'production'
    """Explicitly set Flask environment to production."""
    
    # =========================================================================
    # Security Settings (Strict)
    # =========================================================================
    
    # Secret key - MUST be set via environment variable in production
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    """
    Production secret key.
    
    CRITICAL: This must be set via the SECRET_KEY environment variable!
    The application will fail to start if not set.
    """
    
    @classmethod
    def validate_secret_key(cls) -> None:
        """Validate that SECRET_KEY is set for production."""
        if not cls.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY environment variable must be set in production! "
                "Generate a secure random key and set it as an environment variable."
            )
    
    # JWT secret key - defaults to SECRET_KEY if not set
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', os.getenv('SECRET_KEY', ''))
    """JWT secret key - defaults to SECRET_KEY."""
    
    # HTTPS-only cookies
    SESSION_COOKIE_SECURE: bool = True
    """
    Enforce HTTPS-only session cookies.
    
    CRITICAL: The application must be served over HTTPS in production,
    otherwise session cookies will not be set!
    """
    
    REMEMBER_COOKIE_SECURE: bool = True
    """Enforce HTTPS-only remember me cookies."""
    
    SESSION_COOKIE_SAMESITE: str = 'Strict'
    """
    Strict SameSite policy for session cookies.
    
    This prevents the cookie from being sent in cross-site requests,
    providing additional CSRF protection.
    """
    
    REMEMBER_COOKIE_SAMESITE: str = 'Strict'
    """Strict SameSite policy for remember me cookies."""
    
    # Bcrypt settings - higher rounds for production security
    BCRYPT_LOG_ROUNDS: int = int(os.getenv('BCRYPT_LOG_ROUNDS', '14'))
    """
    Number of bcrypt rounds for password hashing.
    
    Higher values are more secure but slower. Production: 12-14 rounds.
    Adjust based on your server's performance requirements.
    """
    
    # =========================================================================
    # Database Configuration (Production-Grade)
    # =========================================================================
    
    # MongoDB URI - MUST be set via environment variable
    MONGO_URI: str = os.getenv('MONGO_URI')
    """
    MongoDB connection URI.
    
    CRITICAL: This must be set via the MONGO_URI environment variable!
    For MongoDB Atlas, use the full connection string with credentials.
    
    Example:
        mongodb+srv://username:password@cluster.mongodb.net/smartsafi
    """
    
    @classmethod
    def validate_mongo_uri(cls) -> None:
        """Validate that MONGO_URI is set for production."""
        if not cls.MONGO_URI:
            raise ValueError(
                "MONGO_URI environment variable must be set in production! "
                "Provide the full MongoDB connection string."
            )
    
    MONGO_DB_NAME: str = os.getenv('MONGO_DB_NAME', 'smartsafi')
    """MongoDB database name."""
    
    # Production connection pooling settings
    MONGO_MIN_POOL_SIZE: int = int(os.getenv('MONGO_MIN_POOL_SIZE', '10'))
    """Minimum connections in the pool."""
    
    MONGO_MAX_POOL_SIZE: int = int(os.getenv('MONGO_MAX_POOL_SIZE', '100'))
    """Maximum connections in the pool."""
    
    MONGO_MAX_IDLE_TIME_MS: int = int(os.getenv('MONGO_MAX_IDLE_TIME_MS', '60000'))
    """Maximum idle time before closing a connection."""
    
    MONGO_WAIT_QUEUE_TIMEOUT_MS: int = int(os.getenv('MONGO_WAIT_QUEUE_TIMEOUT_MS', '5000'))
    """Maximum time to wait for a connection from the pool."""
    
    # =========================================================================
    # MQTT Configuration
    # =========================================================================
    
    MQTT_BROKER_HOST: str = os.getenv('MQTT_BROKER_HOST', 'localhost')
    """MQTT broker hostname or IP address."""
    
    MQTT_BROKER_PORT: int = int(os.getenv('MQTT_BROKER_PORT', '1883'))
    """MQTT broker port (1883 for MQTT, 8883 for MQTTS)."""
    
    MQTT_USERNAME: str = os.getenv('MQTT_USERNAME', '')
    """MQTT username (if authentication is required)."""
    
    MQTT_PASSWORD: str = os.getenv('MQTT_PASSWORD', '')
    """MQTT password (if authentication is required)."""
    
    MQTT_KEEPALIVE: int = int(os.getenv('MQTT_KEEPALIVE', '60'))
    """MQTT keepalive interval in seconds."""
    
    MQTT_CLEAN_SESSION: bool = os.getenv('MQTT_CLEAN_SESSION', 'True').lower() == 'true'
    """Start with a clean session."""
    
    MQTT_RECONNECT_ON_FAILURE: bool = os.getenv('MQTT_RECONNECT_ON_FAILURE', 'True').lower() == 'true'
    """Automatically reconnect on connection failure."""
    
    MQTT_RECONNECT_DELAY: int = int(os.getenv('MQTT_RECONNECT_DELAY', '5'))
    """Initial delay between reconnection attempts."""
    
    MQTT_RECONNECT_DELAY_MAX: int = int(os.getenv('MQTT_RECONNECT_DELAY_MAX', '60'))
    """Maximum delay between reconnection attempts."""
    
    # =========================================================================
    # Email Configuration
    # =========================================================================
    
    MAIL_SERVER: str = os.getenv('MAIL_SERVER', '')
    """SMTP server hostname (MUST be set in production!)."""
    
    MAIL_PORT: int = int(os.getenv('MAIL_PORT', '587'))
    """SMTP server port."""
    
    MAIL_USE_TLS: bool = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    """Use TLS encryption for SMTP."""
    
    MAIL_USE_SSL: bool = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    """Use SSL encryption for SMTP."""
    
    MAIL_USERNAME: str = os.getenv('MAIL_USERNAME', '')
    """SMTP username."""
    
    MAIL_PASSWORD: str = os.getenv('MAIL_PASSWORD', '')
    """SMTP password."""
    
    MAIL_DEFAULT_SENDER: str = os.getenv(
        'MAIL_DEFAULT_SENDER',
        'SmartSafi <noreply@smartsafi.com>'
    )
    """Default sender address for emails."""
    
    MAIL_SUPPRESS_SEND: bool = False
    """Actually send emails (don't suppress)."""
    
    # =========================================================================
    # Logging Configuration
    # =========================================================================
    
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    """Production logging level."""
    
    # =========================================================================
    # Rate Limiting
    # =========================================================================
    
    RATELIMIT_ENABLED: bool = True
    """Enable rate limiting for security."""
    
    # =========================================================================
    # Health Check
    # =========================================================================
    
    HEALTH_CHECK_ENDPOINT: str = '/health'
    """Health check endpoint path."""
    
    HEALTH_CHECK_ENABLED: bool = True
    """Enable health check endpoint."""
