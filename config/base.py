"""Shared configuration for all SmartSafi environments."""

import os
from datetime import timedelta
from typing import Dict, List, Optional


class BaseConfig:
    """Settings shared by development, testing, and production."""

    APP_NAME: str = 'SmartSafi'
    APP_VERSION: str = '2.0.0'

    DEBUG: bool = False
    TESTING: bool = False
    FLASK_ENV: str = 'production'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    MONGO_URI: str = os.getenv('MONGO_URI', 'mongodb://localhost:27017/smartsafi')
    MONGO_DB_NAME: str = os.getenv('MONGO_DB_NAME', 'smartsafi')
    MONGO_MIN_POOL_SIZE: int = int(os.getenv('MONGO_MIN_POOL_SIZE', '5'))
    MONGO_MAX_POOL_SIZE: int = int(os.getenv('MONGO_MAX_POOL_SIZE', '50'))

    MQTT_BROKER_HOST: str = os.getenv('MQTT_BROKER_HOST', 'localhost')
    MQTT_BROKER_PORT: int = int(os.getenv('MQTT_BROKER_PORT', '1883'))
    MQTT_USERNAME: str = os.getenv('MQTT_USERNAME', '')
    MQTT_PASSWORD: str = os.getenv('MQTT_PASSWORD', '')
    MQTT_KEEPALIVE: int = int(os.getenv('MQTT_KEEPALIVE', '60'))

    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')
    API_KEYS: List[str] = []

    # =========================================================================
    # Email Server Configuration
    # =========================================================================
    
    MAIL_SERVER: str = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    """SMTP server hostname for sending emails."""
    
    MAIL_PORT: int = int(os.getenv('MAIL_PORT', '587'))
    """SMTP server port (default: 587 for TLS, 465 for SSL)."""
    
    MAIL_USE_TLS: bool = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    """Whether to use TLS encryption for SMTP connections."""
    
    MAIL_USE_SSL: bool = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    """Whether to use SSL encryption for SMTP connections."""
    
    MAIL_USERNAME: str = os.getenv('MAIL_USERNAME', '')
    """Username for SMTP authentication."""
    
    MAIL_PASSWORD: str = os.getenv('MAIL_PASSWORD', '')
    """Password or app-specific password for SMTP authentication."""
    
    MAIL_DEFAULT_SENDER: str = os.getenv(
        'MAIL_DEFAULT_SENDER',
        'SmartSafi <noreply@smartsafi.com>'
    )
    """Default sender address for outgoing emails."""
    
    MAIL_MAX_EMAILS: Optional[int] = None
    """Maximum number of emails to send in a single connection (None for unlimited)."""
    
    MAIL_SUPPRESS_SEND: bool = False
    """If True, emails will be logged but not actually sent (useful for testing)."""
    
    MAIL_ASCII_ATTACHMENTS: bool = False
    """If True, attachment filenames will be converted to ASCII."""
    
    # =========================================================================
    # Security Settings
    # =========================================================================
    
    # Session Security
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(
        seconds=int(os.getenv('SESSION_LIFETIME', '3600'))
    )
    """Duration after which permanent sessions expire (default: 1 hour)."""
    
    SESSION_COOKIE_NAME: str = 'smartsafi_session'
    """Name of the session cookie."""
    
    SESSION_COOKIE_DOMAIN: Optional[str] = None
    """Domain for the session cookie (None for current domain only)."""
    
    SESSION_COOKIE_PATH: str = '/'
    """Path for the session cookie."""
    
    SESSION_COOKIE_HTTPONLY: bool = True
    """Whether the session cookie should be HttpOnly (prevents XSS)."""
    
    SESSION_COOKIE_SECURE: bool = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    """Whether the session cookie should only be sent over HTTPS."""
    
    SESSION_COOKIE_SAMESITE: str = 'Lax'
    """SameSite attribute for session cookie (Strict, Lax, or None)."""
    
    # Remember Me Cookie
    REMEMBER_COOKIE_NAME: str = 'remember_token'
    """Name of the remember me cookie."""
    
    REMEMBER_COOKIE_DURATION: timedelta = timedelta(
        seconds=int(os.getenv('REMEMBER_COOKIE_DURATION', '86400'))
    )
    """Duration for remember me cookie (default: 24 hours)."""
    
    REMEMBER_COOKIE_HTTPONLY: bool = True
    """Whether the remember me cookie should be HttpOnly."""
    
    REMEMBER_COOKIE_SECURE: bool = os.getenv('REMEMBER_COOKIE_SECURE', 'False').lower() == 'true'
    """Whether the remember me cookie should only be sent over HTTPS."""
    
    REMEMBER_COOKIE_SAMESITE: str = 'Lax'
    """SameSite attribute for remember me cookie."""
    
    # Content Security
    MAX_CONTENT_LENGTH: int = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))
    """Maximum allowed content length for uploads (default: 16MB)."""
    
    # Bcrypt settings
    BCRYPT_LOG_ROUNDS: int = int(os.getenv('BCRYPT_LOG_ROUNDS', '12'))
    """Number of bcrypt rounds for password hashing (higher = more secure but slower)."""
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    """Secret key for JWT token signing."""
    
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=1)
    """Expiration time for JWT access tokens."""
    
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=30)
    """Expiration time for JWT refresh tokens."""
    
    # =========================================================================
    # Rate Limiting Configuration
    # =========================================================================
    
    RATELIMIT_ENABLED: bool = True
    """Whether rate limiting is enabled."""
    
    RATELIMIT_STORAGE_URL: str = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    """Storage backend for rate limiting (memory://, redis://localhost:6379/0, etc.)."""
    
    RATELIMIT_STRATEGY: str = 'fixed-window'
    """Rate limiting strategy (fixed-window, moving-window, etc.)."""
    
    RATELIMIT_DEFAULT: str = os.getenv('RATE_LIMIT_DEFAULT', '100 per hour')
    """Default rate limit for all routes."""
    
    RATELIMIT_LOGIN: str = os.getenv('RATE_LIMIT_LOGIN', '5 per minute')
    """Rate limit for login attempts."""
    
    RATELIMIT_API: str = os.getenv('RATE_LIMIT_API', '1000 per hour')
    """Rate limit for API endpoints."""
    
    RATELIMIT_KEY_PREFIX: str = 'smartsafi'
    """Prefix for rate limit keys in storage."""
    
    # =========================================================================
    # Logging Configuration
    # =========================================================================
    
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    """Default logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."""
    
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    """Format string for log messages."""
    
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/smartsafi.log')
    """Path to the main log file."""
    
    LOG_MAX_BYTES: int = int(os.getenv('LOG_MAX_BYTES', '10485760'))
    """Maximum size of log files before rotation (default: 10MB)."""
    
    LOG_BACKUP_COUNT: int = int(os.getenv('LOG_BACKUP_COUNT', '10'))
    """Number of backup log files to keep."""
    
    LOG_TO_STDOUT: bool = True
    """Whether to log to stdout in addition to file."""
    
    # =========================================================================
    # Map Configuration
    # =========================================================================
    
    MAP_DEFAULT_LAT: float = float(os.getenv('MAP_DEFAULT_LAT', '31.6295'))
    """Default latitude for map center (Safi, Morocco)."""
    
    MAP_DEFAULT_LNG: float = float(os.getenv('MAP_DEFAULT_LNG', '-7.9811'))
    """Default longitude for map center (Safi, Morocco)."""
    
    MAP_DEFAULT_ZOOM: int = int(os.getenv('MAP_DEFAULT_ZOOM', '13'))
    """Default zoom level for map."""
    
    MAP_TILE_LAYER: str = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    """URL template for map tiles."""
    
    MAP_ATTRIBUTION: str = '&copy; OpenStreetMap contributors'
    """Attribution text for map tiles."""
    
    # =========================================================================
    # Regional Settings (Smart City Configuration)
    # =========================================================================
    
    # Waste Management Regions
    REGIONS: List[str] = os.getenv('REGIONS', 'nord,sud,est,ouest').split(',')
    """List of waste management regions (nord, sud, est, ouest)."""
    
    # Lighting Districts
    DISTRICTS: List[str] = os.getenv('DISTRICTS', 'quartier_a,quartier_b').split(',')
    """List of lighting districts (quartier_a, quartier_b)."""
    
    # Waste Configuration
    WASTE_BIN_CAPACITY: int = 100  # liters
    """Default capacity of waste bins in liters."""
    
    WASTE_FILL_THRESHOLD_WARNING: float = 0.75  # 75%
    """Fill level threshold for warning alerts."""
    
    WASTE_FILL_THRESHOLD_CRITICAL: float = 0.90  # 90%
    """Fill level threshold for critical alerts."""
    
    WASTE_COLLECTION_SCHEDULE: Dict[str, str] = {
        'nord': '08:00',
        'sud': '09:00',
        'est': '10:00',
        'ouest': '11:00',
    }
    """Collection schedule by region (time in HH:MM format)."""
    
    # Water Quality Configuration
    WATER_PH_MIN: float = 6.5
    """Minimum acceptable pH level for water quality."""
    
    WATER_PH_MAX: float = 8.5
    """Maximum acceptable pH level for water quality."""
    
    WATER_TURBIDITY_MAX: float = 5.0  # NTU
    """Maximum acceptable turbidity level (Nephelometric Turbidity Units)."""
    
    WATER_CONDUCTIVITY_MIN: float = 50.0  # µS/cm
    """Minimum acceptable conductivity."""
    
    WATER_CONDUCTIVITY_MAX: float = 1500.0  # µS/cm
    """Maximum acceptable conductivity."""
    
    WATER_TEMPERATURE_MIN: float = 0.0  # °C
    """Minimum acceptable water temperature."""
    
    WATER_TEMPERATURE_MAX: float = 35.0  # °C
    """Maximum acceptable water temperature."""
    
    # Air Quality Configuration
    AIR_PM25_MAX: float = 35.0  # µg/m³
    """Maximum acceptable PM2.5 level (WHO guideline: 15 µg/m³, national: 35 µg/m³)."""
    
    AIR_PM10_MAX: float = 150.0  # µg/m³
    """Maximum acceptable PM10 level (WHO guideline: 45 µg/m³, national: 150 µg/m³)."""
    
    AIR_O3_MAX: float = 100.0  # ppb
    """Maximum acceptable Ozone (O3) level."""
    
    AIR_NO2_MAX: float = 100.0  # ppb
    """Maximum acceptable Nitrogen Dioxide (NO2) level."""
    
    AIR_SO2_MAX: float = 75.0  # ppb
    """Maximum acceptable Sulfur Dioxide (SO2) level."""
    
    AIR_CO_MAX: float = 9.0  # ppm
    """Maximum acceptable Carbon Monoxide (CO) level."""
    
    AIR_TEMPERATURE_MIN: float = -10.0  # °C
    """Minimum acceptable air temperature."""
    
    AIR_TEMPERATURE_MAX: float = 45.0  # °C
    """Maximum acceptable air temperature."""
    
    AIR_HUMIDITY_MIN: float = 10.0  # %
    """Minimum acceptable relative humidity."""
    
    AIR_HUMIDITY_MAX: float = 95.0  # %
    """Maximum acceptable relative humidity."""
    
    # Agriculture Configuration
    AGRICULTURE_TEMPERATURE_MIN: float = 10.0  # °C
    """Minimum acceptable soil temperature for agriculture."""
    
    AGRICULTURE_TEMPERATURE_MAX: float = 35.0  # °C
    """Maximum acceptable soil temperature for agriculture."""
    
    AGRICULTURE_HUMIDITY_MIN: float = 40.0  # %
    """Minimum acceptable soil humidity for agriculture."""
    
    AGRICULTURE_HUMIDITY_MAX: float = 80.0  # %
    """Maximum acceptable soil humidity for agriculture."""
    
    AGRICULTURE_SOIL_MOISTURE_MIN: float = 20.0  # %
    """Minimum acceptable soil moisture level."""
    
    AGRICULTURE_SOIL_MOISTURE_MAX: float = 70.0  # %
    """Maximum acceptable soil moisture level."""
    
    AGRICULTURE_SOIL_PH_MIN: float = 5.5
    """Minimum acceptable soil pH level."""
    
    AGRICULTURE_SOIL_PH_MAX: float = 7.5
    """Maximum acceptable soil pH level."""
    
    AGRICULTURE_NPK_N_MIN: float = 50.0  # mg/kg
    """Minimum acceptable Nitrogen level in soil."""
    
    AGRICULTURE_NPK_N_MAX: float = 200.0  # mg/kg
    """Maximum acceptable Nitrogen level in soil."""
    
    AGRICULTURE_NPK_P_MIN: float = 10.0  # mg/kg
    """Minimum acceptable Phosphorus level in soil."""
    
    AGRICULTURE_NPK_P_MAX: float = 50.0  # mg/kg
    """Maximum acceptable Phosphorus level in soil."""
    
    AGRICULTURE_NPK_K_MIN: float = 50.0  # mg/kg
    """Minimum acceptable Potassium level in soil."""
    
    AGRICULTURE_NPK_K_MAX: float = 200.0  # mg/kg
    """Maximum acceptable Potassium level in soil."""
    
    # Lighting Configuration
    LIGHTING_INTENSITY_MIN: int = 0  # %
    """Minimum lighting intensity level."""
    
    LIGHTING_INTENSITY_MAX: int = 100  # %
    """Maximum lighting intensity level."""
    
    LIGHTING_DEFAULT_INTENSITY: int = 80  # %
    """Default lighting intensity level."""
    
    LIGHTING_ENERGY_THRESHOLD_WARNING: float = 0.75  # 75%
    """Energy consumption threshold for warning alerts."""
    
    LIGHTING_ENERGY_THRESHOLD_CRITICAL: float = 0.90  # 90%
    """Energy consumption threshold for critical alerts."""
    
    LIGHTING_SCHEDULE: Dict[str, Dict[str, str]] = {
        'quartier_a': {
            'on_time': '18:00',
            'off_time': '06:00',
            'dim_time': '23:00',
            'dim_intensity': '30'
        },
        'quartier_b': {
            'on_time': '18:30',
            'off_time': '05:30',
            'dim_time': '22:30',
            'dim_intensity': '25'
        }
    }
    """Lighting schedule configuration by district."""
