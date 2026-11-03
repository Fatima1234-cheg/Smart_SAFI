"""
SmartSafi - MongoDB Models

This package contains all MongoDB document models for the SmartSafi application.
Each model provides methods for CRUD operations and business logic.

Models:
    - User: User authentication and management
    - Waste: Waste management and bin monitoring
    - Water: Water quality monitoring
    - Air: Air quality monitoring
    - Agriculture: Smart agriculture sensors
    - Lighting: Smart street lighting
    - History: Activity and audit logs

Usage:
    from app.models import User, Waste
    
    # Find a user
    user = User.find_by_username('admin')
    
    # Create a waste record
    waste = Waste.create(
        region='nord',
        bin_id='bin_001',
        fill_level=0.75
    )
"""

from app.models.user import User
from app.models.waste import Waste
from app.models.water import Water
from app.models.air import Air
from app.models.agriculture import Agriculture
from app.models.lighting import Lighting
from app.models.history import History

__all__ = [
    'User',
    'Waste',
    'Water',
    'Air',
    'Agriculture',
    'Lighting',
    'History',
]
