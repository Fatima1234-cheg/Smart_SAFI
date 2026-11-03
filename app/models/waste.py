"""
SmartSafi - Waste Management Model

This module defines the Waste model for MongoDB to track waste bins
across different regions (nord, sud, est, ouest).
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId

from app import mongo


class Waste:
    """
    Waste management model for tracking waste bins.
    
    Attributes:
        id: MongoDB ObjectId as string
        region: Region name (nord, sud, est, ouest)
        bin_id: Unique bin identifier
        fill_level: Fill level as decimal (0.0 to 1.0)
        capacity: Bin capacity in liters
        location: GPS coordinates {lat, lng}
        last_collected: Last collection timestamp
        status: Bin status (active, full, maintenance)
        sensor_data: Additional sensor readings
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    REGIONS = ['nord', 'sud', 'est', 'ouest']
    STATUSES = ['active', 'full', 'maintenance', 'offline']
    
    def __init__(self, waste_data: Dict[str, Any]):
        """Initialize waste bin from MongoDB document."""
        self._id = str(waste_data.get('_id')) if '_id' in waste_data else None
        self.region = waste_data.get('region', '')
        self.bin_id = waste_data.get('bin_id', '')
        self.fill_level = waste_data.get('fill_level', 0.0)
        self.capacity = waste_data.get('capacity', 100)
        self.location = waste_data.get('location', {'lat': 0.0, 'lng': 0.0})
        self.last_collected = waste_data.get('last_collected')
        self.status = waste_data.get('status', 'active')
        self.sensor_data = waste_data.get('sensor_data', {})
        self.created_at = waste_data.get('created_at', datetime.utcnow())
        self.updated_at = waste_data.get('updated_at', datetime.utcnow())
    
    @property
    def id(self) -> str:
        """Return waste record ID as string."""
        return self._id
    
    @property
    def is_full(self) -> bool:
        """Check if bin is full (fill level >= 90%)."""
        return self.fill_level >= 0.90
    
    @property
    def needs_collection(self) -> bool:
        """Check if bin needs collection (fill level >= 75%)."""
        return self.fill_level >= 0.75
    
    @property
    def fill_percentage(self) -> float:
        """Get fill level as percentage."""
        return self.fill_level * 100
    
    def save(self) -> 'Waste':
        """Save waste record to database."""
        collection = mongo.db.waste
        
        waste_data = {
            'region': self.region,
            'bin_id': self.bin_id,
            'fill_level': self.fill_level,
            'capacity': self.capacity,
            'location': self.location,
            'last_collected': self.last_collected,
            'status': self.status,
            'sensor_data': self.sensor_data,
            'updated_at': datetime.utcnow()
        }
        
        if self._id:
            collection.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': waste_data}
            )
        else:
            waste_data['created_at'] = datetime.utcnow()
            result = collection.insert_one(waste_data)
            self._id = str(result.inserted_id)
        
        return self
    
    def delete(self) -> bool:
        """Delete waste record from database."""
        if not self._id:
            return False
        
        collection = mongo.db.waste
        result = collection.delete_one({'_id': ObjectId(self._id)})
        return result.deleted_count > 0
    
    def mark_collected(self) -> 'Waste':
        """Mark bin as collected."""
        self.fill_level = 0.0
        self.last_collected = datetime.utcnow()
        self.status = 'active'
        return self.save()
    
    def update_fill_level(self, level: float) -> 'Waste':
        """Update fill level."""
        self.fill_level = max(0.0, min(1.0, level))
        if self.is_full:
            self.status = 'full'
        return self.save()
    
    @classmethod
    def find_by_id(cls, waste_id: str) -> Optional['Waste']:
        """Find waste record by ID."""
        try:
            collection = mongo.db.waste
            waste_data = collection.find_one({'_id': ObjectId(waste_id)})
            return cls(waste_data) if waste_data else None
        except:
            return None
    
    @classmethod
    def find_by_bin_id(cls, bin_id: str) -> Optional['Waste']:
        """Find waste record by bin ID."""
        collection = mongo.db.waste
        waste_data = collection.find_one({'bin_id': bin_id})
        return cls(waste_data) if waste_data else None
    
    @classmethod
    def find_by_region(cls, region: str, skip: int = 0, limit: int = 100) -> List['Waste']:
        """Find waste records by region."""
        collection = mongo.db.waste
        waste_data = collection.find({'region': region}).skip(skip).limit(limit)
        return [cls(data) for data in waste_data]
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List['Waste']:
        """Get all waste records with pagination."""
        collection = mongo.db.waste
        waste_data = collection.find().skip(skip).limit(limit)
        return [cls(data) for data in waste_data]
    
    @classmethod
    def get_needing_collection(cls, region: str = None) -> List['Waste']:
        """Get bins needing collection (fill level >= 75%)."""
        collection = mongo.db.waste
        query = {'fill_level': {'$gte': 0.75}}
        if region:
            query['region'] = region
        waste_data = collection.find(query)
        return [cls(data) for data in waste_data]
    
    @classmethod
    def get_full_bins(cls, region: str = None) -> List['Waste']:
        """Get full bins (fill level >= 90%)."""
        collection = mongo.db.waste
        query = {'fill_level': {'$gte': 0.90}}
        if region:
            query['region'] = region
        waste_data = collection.find(query)
        return [cls(data) for data in waste_data]
    
    @classmethod
    def get_statistics_by_region(cls) -> Dict[str, Dict[str, Any]]:
        """Get waste statistics grouped by region."""
        collection = mongo.db.waste
        
        pipeline = [
            {
                '$group': {
                    '_id': '$region',
                    'total_bins': {'$sum': 1},
                    'avg_fill_level': {'$avg': '$fill_level'},
                    'full_bins': {
                        '$sum': {
                            '$cond': [{'$gte': ['$fill_level', 0.90]}, 1, 0]
                        }
                    },
                    'bins_need_collection': {
                        '$sum': {
                            '$cond': [{'$gte': ['$fill_level', 0.75]}, 1, 0]
                        }
                    }
                }
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert to dictionary keyed by region
        stats = {}
        for result in results:
            region = result['_id']
            stats[region] = {
                'total_bins': result['total_bins'],
                'avg_fill_level': round(result['avg_fill_level'] * 100, 2),
                'full_bins': result['full_bins'],
                'bins_need_collection': result['bins_need_collection']
            }
        
        return stats
    
    @classmethod
    def count(cls, region: str = None) -> int:
        """Count waste records."""
        collection = mongo.db.waste
        query = {}
        if region:
            query['region'] = region
        return collection.count_documents(query)
    
    @classmethod
    def create(cls, region: str, bin_id: str, fill_level: float = 0.0,
                 capacity: int = 100, location: dict = None,
                 status: str = 'active') -> 'Waste':
        """
        Create a new waste record.
        
        Args:
            region: Region name (nord, sud, est, ouest)
            bin_id: Unique bin identifier
            fill_level: Initial fill level (0.0 to 1.0)
            capacity: Bin capacity in liters
            location: GPS coordinates {'lat': float, 'lng': float}
            status: Bin status
            
        Returns:
            Created Waste instance
        """
        waste = cls({
            'region': region,
            'bin_id': bin_id,
            'fill_level': fill_level,
            'capacity': capacity,
            'location': location or {'lat': 0.0, 'lng': 0.0},
            'status': status
        })
        waste.save()
        return waste
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert waste record to dictionary."""
        return {
            'id': self._id,
            'region': self.region,
            'bin_id': self.bin_id,
            'fill_level': self.fill_level,
            'capacity': self.capacity,
            'location': self.location,
            'last_collected': self.last_collected.isoformat() if self.last_collected else None,
            'status': self.status,
            'sensor_data': self.sensor_data,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    def __repr__(self) -> str:
        """String representation of waste record."""
        return f"<Waste {self.bin_id} - {self.region}>"
