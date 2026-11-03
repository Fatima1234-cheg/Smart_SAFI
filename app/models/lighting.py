"""
Lighting Model for Smart City - SmartSafi
"""

from datetime import datetime, time
from bson.objectid import ObjectId
from app import mongo


class Lighting:
    """Modèle pour la gestion de l'éclairage public"""
    
    DISTRICTS = ['quartier_a', 'quartier_b']
    
    def __init__(self, data):
        """Initialiser le modèle Lighting"""
        self._id = str(data.get('_id')) if '_id' in data else None
        self.light_id = data.get('light_id', '')
        self.district = data.get('district', '')
        self.street = data.get('street', '')
        self.status = data.get('status', 'off')
        self.brightness = data.get('brightness', 0)
        self.energy_consumption = data.get('energy_consumption', 0)
        self.voltage = data.get('voltage', 0)
        self.current = data.get('current', 0)
        self.power_factor = data.get('power_factor', 0)
        self.temperature = data.get('temperature', 0)
        self.operating_hours = data.get('operating_hours', 0)
        self.last_maintenance = data.get('last_maintenance')
        self.next_maintenance = data.get('next_maintenance')
        self.maintenance_count = data.get('maintenance_count', 0)
        self.automatic_mode = data.get('automatic_mode', True)
        self.schedule = data.get('schedule', {})
        self.motion_detected = data.get('motion_detected', False)
        self.fault_status = data.get('fault_status', 'ok')
        self.fault_description = data.get('fault_description', '')
        self.location = data.get('location', {})
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self._id,
            'light_id': self.light_id,
            'district': self.district,
            'street': self.street,
            'status': self.status,
            'brightness': self.brightness,
            'energy_consumption': self.energy_consumption,
            'voltage': self.voltage,
            'current': self.current,
            'power_factor': self.power_factor,
            'temperature': self.temperature,
            'operating_hours': self.operating_hours,
            'last_maintenance': self.last_maintenance.isoformat() if isinstance(self.last_maintenance, datetime) else self.last_maintenance,
            'next_maintenance': self.next_maintenance.isoformat() if isinstance(self.next_maintenance, datetime) else self.next_maintenance,
            'maintenance_count': self.maintenance_count,
            'automatic_mode': self.automatic_mode,
            'schedule': self.schedule,
            'motion_detected': self.motion_detected,
            'fault_status': self.fault_status,
            'fault_description': self.fault_description,
            'location': self.location,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    def turn_on(self, brightness=100):
        """Allumer le lampadaire"""
        self.status = 'on'
        self.brightness = min(100, max(0, brightness))
        self.updated_at = datetime.utcnow()
        
        mongo.db.lighting.update_one(
            {'_id': ObjectId(self._id)},
            {'$set': {
                'status': self.status,
                'brightness': self.brightness,
                'updated_at': self.updated_at
            }}
        )
    
    def turn_off(self):
        """Éteindre le lampadaire"""
        self.status = 'off'
        self.brightness = 0
        self.updated_at = datetime.utcnow()
        
        mongo.db.lighting.update_one(
            {'_id': ObjectId(self._id)},
            {'$set': {
                'status': self.status,
                'brightness': self.brightness,
                'updated_at': self.updated_at
            }}
        )
    
    def adjust_brightness(self, brightness):
        """Ajuster la luminosité"""
        brightness = min(100, max(0, brightness))
        self.brightness = brightness
        self.status = 'on' if brightness > 0 else 'off'
        self.updated_at = datetime.utcnow()
        
        mongo.db.lighting.update_one(
            {'_id': ObjectId(self._id)},
            {'$set': {
                'brightness': self.brightness,
                'status': self.status,
                'updated_at': self.updated_at
            }}
        )
    
    def check_faults(self):
        """Vérifier les anomalies"""
        faults = []
        
        if self.voltage < 200 or self.voltage > 260:
            faults.append(f'Abnormal voltage: {self.voltage}V')
        
        if self.current > 10:
            faults.append(f'High current: {self.current}A')
        
        if self.temperature > 80:
            faults.append(f'High temperature: {self.temperature}°C')
        
        if faults:
            self.fault_status = 'fault'
            self.fault_description = '; '.join(faults)
        else:
            self.fault_status = 'ok'
            self.fault_description = ''
        
        return faults
    
    @staticmethod
    def get_all(district=None, status=None, limit=None):
        """Récupérer tous les lampadaires"""
        query = {}
        if district:
            query['district'] = district
        if status:
            query['status'] = status
        
        cursor = mongo.db.lighting.find(query).sort('created_at', -1)
        if limit:
            cursor = cursor.limit(limit)
        return [Lighting(doc) for doc in cursor]
    
    @staticmethod
    def get_by_id(light_id):
        """Récupérer un lampadaire par ID"""
        try:
            if isinstance(light_id, str):
                light_id = ObjectId(light_id)
            doc = mongo.db.lighting.find_one({'_id': light_id})
            if doc:
                return Lighting(doc)
        except Exception as e:
            print(f"Error getting lighting by id: {e}")
        return None
    
    @staticmethod
    def create(data):
        """Créer un nouveau lampadaire"""
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        
        result = mongo.db.lighting.insert_one(data)
        return Lighting.get_by_id(result.inserted_id)
    
    @staticmethod
    def get_stats(district=None):
        """Obtenir les statistiques d'éclairage"""
        match_stage = {}
        if district:
            match_stage['district'] = district
        
        pipeline = [
            {'$match': match_stage},
            {
                '$group': {
                    '_id': None,
                    'total_lights': {'$sum': 1},
                    'active_lights': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'on']}, 1, 0]}
                    },
                    'avg_brightness': {'$avg': '$brightness'},
                    'total_energy': {'$sum': '$energy_consumption'},
                    'fault_count': {
                        '$sum': {'$cond': [{'$ne': ['$fault_status', 'ok']}, 1, 0]}
                    }
                }
            }
        ]
        
        result = list(mongo.db.lighting.aggregate(pipeline))
        if result:
            stats = result[0]
            del stats['_id']
            return {k: round(v, 2) if isinstance(v, float) else v for k, v in stats.items()}
        return {}
