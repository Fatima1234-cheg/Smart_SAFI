"""
SmartSafi - Testing Configuration

This module contains the configuration settings for testing environments.
These settings are optimized for running automated tests with pytest.

Characteristics:
- Testing mode enabled
- In-memory database for fast test execution
- Debug mode disabled to test production-like behavior
- Rate limiting disabled
- Email sending suppressed
- Verbose logging for test debugging

Test Database:
By default, tests use an in-memory SQLite database for speed.
You can override this with the TEST_DATABASE_URI environment variable
to test against a real database (recommended for integration tests).
"""

import os
from datetime import timedelta
from config.base import BaseConfig


class TestingConfig(BaseConfig):
    """
    Testing environment configuration.
    
    This configuration is optimized for running automated tests.
    It uses in-memory databases for speed and disables external
    services to ensure tests are fast and isolated.
    
    Note: While DEBUG is disabled to test production-like behavior,
    detailed error messages are still available in test logs.
    """
    
    # =========================================================================
    # Flask Core Settings
    # =========================================================================
    
    DEBUG: bool = False
    """
    Debug mode is disabled in testing.
    
    This ensures tests run with production-like behavior for accurate results.
    However, detailed error information is still logged for debugging.
    """
    
    TESTING: bool = True
    """
    Testing mode is enabled.
    
    This tells Flask and extensions that we're running tests,
    which may change certain behaviors (e.g., error handling).
    """
    
    FLASK_ENV: str = 'testing'
    """Explicitly set Flask environment to testing."""
    
    # =========================================================================
    # Security Settings (Relaxed for Testing)
    # =========================================================================
    
    # Use a predictable secret key for tests
    SECRET_KEY: str = 'test-secret-key-for-testing-only-not-for-production'
    """
    Testing secret key.
    
    This predictable key makes tests reproducible and easier to debug.
    Never use this key in production!
    """
    
    # Allow HTTP cookies in testing (tests may run without HTTPS)
    SESSION_COOKIE_SECURE: bool = False
    """Allow session cookies over HTTP for testing."""
    
    REMEMBER_COOKIE_SECURE: bool = False
    """Allow remember me cookies over HTTP for testing."""
    
    # Use lax SameSite for testing flexibility
    SESSION_COOKIE_SAMESITE: str = 'Lax'
    """Lax SameSite policy for session cookies in testing."""
    
    REMEMBER_COOKIE_SAMESITE: str = 'Lax'
    """Lax SameSite policy for remember me cookies in testing."""
    
    # =========================================================================
    # Database Configuration (In-Memory for Speed)
    # =========================================================================
    
    # Use in-memory database for fast test execution
    # Can be overridden with TEST_DATABASE_URI for integration tests
    MONGO_URI: str = os.getenv('TEST_DATABASE_URI', 'mongodb://localhost:27017/smartsafi_test')
    """
    MongoDB connection URI for testing.
    
    Defaults to a dedicated test database on localhost.
    Set TEST_DATABASE_URI environment variable to override for integration tests.
    """
    
    MONGO_DB_NAME: str = 'smartsafi_test'
    """Test database name."""
    
    # Small connection pool for tests
    MONGO_MIN_POOL_SIZE: int = 1
    """Minimum connection pool size for tests."""
    
    MONGO_MAX_POOL_SIZE: int = 5
    """Maximum connection pool size for tests."""
    
    # Short timeouts for faster test execution
    MONGO_MAX_IDLE_TIME_MS: int = 10000
    """Short idle time for faster connection recycling."""
    
    MONGO_WAIT_QUEUE_TIMEOUT_MS: int = 1000
    """Short wait timeout for faster test failure."""
    
    # =========================================================================
    # MQTT Configuration (Disabled for Tests)
    # =========================================================================
    
    MQTT_ENABLED: bool = False
    """
    MQTT is disabled in testing.
    
    Tests should use mocking to test MQTT functionality without
    requiring an actual MQTT broker connection.
    """
    
    # These settings are kept for reference but won't be used (MQTT_ENABLED=False)
    MQTT_BROKER_HOST: str = 'localhost'
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = ''
    MQTT_PASSWORD: str = ''
    MQTT_KEEPALIVE: int = 60
    
    # =========================================================================
    # Email Configuration (Suppressed for Tests)
    # =========================================================================
    
    MAIL_SUPPRESS_SEND: bool = True
    """
    Suppress email sending in tests.
    
    Emails will be captured and logged but not actually sent.
    This allows tests to verify email content without sending real emails.
    """
    
    MAIL_SERVER: str = 'localhost'
    MAIL_PORT: int = 1025
    MAIL_USE_TLS: bool = False
    MAIL_USERNAME: str = ''
    MAIL_PASSWORD: str = ''
    MAIL_DEFAULT_SENDER: str = 'test@smartsafi.com'
    
    # =========================================================================
    # Logging Configuration
    # =========================================================================
    
    LOG_LEVEL: str = os.getenv('TEST_LOG_LEVEL', 'WARNING')
    """
    Test logging level.
    
    Defaults to WARNING to keep test output clean.
    Set TEST_LOG_LEVEL environment variable to override for debugging.
    """
    
    LOG_FILE: str = 'logs/test.log'
    """Separate log file for tests."""
    
    # =========================================================================
    # Rate Limiting
    # =========================================================================
    
    RATELIMIT_ENABLED: bool = False
    """
    Rate limiting is disabled in testing.
    
    This allows tests to make rapid requests without hitting limits.
    Rate limiting should be tested separately with integration tests.
    """
    
    # =========================================================================
    # WTF-CSRF Configuration
    # =========================================================================
    
    # CSRF is enabled by default but can be disabled for specific tests
    WTF_CSRF_ENABLED: bool = True
    """CSRF protection is enabled in testing (production-like)."""
    
    # =========================================================================
    # Testing-Specific Settings
    # =========================================================================
    
    # Enable template auto-reload for easier debugging
    TEMPLATES_AUTO_RELOAD: bool = False
    """
    Template auto-reload is disabled for production-like behavior.
    
    Enable by setting TEMPLATES_AUTO_RELOAD=True for debugging specific tests.
    """
    
    # Test-specific settings
    TESTING_DATA_PATH: str = 'tests/data'
    """Path to test data files."""
    
    FIXTURES_PATH: str = 'tests/fixtures'
    """Path to test fixtures."""
