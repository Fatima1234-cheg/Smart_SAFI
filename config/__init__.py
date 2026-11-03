"""
SmartSafi Configuration Package

This package provides configuration management for different environments:
- Development: Local development with debug enabled
- Production: Production deployment settings
- Testing: Test environment configuration

Usage:
    from config import get_config
    config = get_config('development')
    
    # Or using the config object in Flask
    app.config.from_object(config)
"""

import os
from typing import Optional


def get_config(config_name: Optional[str] = None) -> object:
    """
    Get the configuration class for the specified environment.
    
    Args:
        config_name: The configuration name (development, production, testing).
                    Defaults to the FLASK_ENV environment variable or 'production'.
    
    Returns:
        The configuration class instance.
    
    Raises:
        ValueError: If the configuration name is invalid.
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'production').lower()
    
    # Map old 'default' to 'production'
    if config_name == 'default':
        config_name = 'production'
    
    # Import configurations
    from config.development import DevelopmentConfig
    from config.production import ProductionConfig
    from config.testing import TestingConfig
    
    config_classes = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    if config_name not in config_classes:
        raise ValueError(
            f"Invalid configuration name: '{config_name}'. "
            f"Valid options are: {', '.join(config_classes.keys())}"
        )
    
    config_class = config_classes[config_name]
    return config_class()


def get_config_from_object(obj: object) -> dict:
    """
    Convert a configuration object to a dictionary.
    
    Args:
        obj: The configuration object.
    
    Returns:
        A dictionary containing all uppercase configuration keys.
    """
    return {
        key: getattr(obj, key)
        for key in dir(obj)
        if key.isupper() and not key.startswith('_')
    }


# Export main functions
__all__ = [
    'get_config',
    'get_config_from_object',
]
