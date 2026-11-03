"""
Agriculture Model for Smart City - SmartSafi
"""

from datetime import datetime
from bson.objectid import ObjectId
from app import mongo


class Agriculture:
    """Modèle pour l'agriculture intelligente"""
    
    ZONES = ['zone_a', 'zone_b', 'zone_c', 'zone_d']
    
    def __init__(self, data):
        """Initialiser le modèle Agriculture"""
        self._id = str(data.get('_id')) if '_id' in data else None
        self.sensor_id = data.get('sensor_id', '')
        self.zone = data.get('zone', '')
        self.plot_id = data.get('plot_id', '')
        self.soil_moisture = data.get('soil_moisture', 0)
        self.soil_temperature = data.get('soil_temperature', 0)
        self.soil_ph = data.get('soil_ph', 7.0)
        self.soil_conductivity = data.get('soil_conductivity', 0)
        self.air_temperature = data.get('air_temperature', 0)
        self.air_humidity = data.get('air_humidity', 0)
        self.light_intensity = data.get('light_intensity', 0)
        self.co2_level = data.get('co2_level', 0)
        self.leaf_wetness = data.get('leaf_wetness', 0)
        self.uv_index = data.get('uv_index', 0)
        self.wind_speed = data.get('wind_speed', 0)
        self.wind_direction = data.get('wind_direction', 0)
        self.rainfall = data.get('rainfall', 0)
        self.irrigation_needed = data.get('irrigation_needed', False)
        self.fertilizer_needed = data.get('fertilizer_needed', False)
        self.health_status = data.get('health_status', 'good')
        self.recommendations = data.get('recommendations', [])
        self.location = data.get('location', {})
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self._id,
            'sensor_id': self.sensor_id,
            'zone': self.zone,
            'plot_id': self.plot_id,
            'soil_moisture': self.soil_moisture,
            'soil_temperature': self.soil_temperature,
            'soil_ph': self.soil_ph,
            'soil_conductivity': self.soil_conductivity,
            'air_temperature': self.air_temperature,
            'air_humidity': self.air_humidity,
            'light_intensity': self.light_intensity,
            'co2_level': self.co2_level,
            'leaf_wetness': self.leaf_wetness,
            'uv_index': self.uv_index,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'rainfall': self.rainfall,
            'irrigation_needed': self.irrigation_needed,
            'fertilizer_needed': self.fertilizer_needed,
            'health_status': self.health_status,
            'recommendations': self.recommendations,
            'location': self.location,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    def analyze_health(self):
        """Analyser la santé des cultures"""
        issues = []
        
        # Analyser l'humidité du sol
        if self.soil_moisture < 30:
            issues.append('Soil too dry - irrigation needed')
            self.irrigation_needed = True
        elif self.soil_moisture > 70:
            issues.append('Soil too wet - risk of root rot')
        
        # Analyser le pH
        if self.soil_ph < 6.0:
            issues.append('Soil pH too low - lime application needed')
        elif self.soil_ph > 7.5:
            issues.append('Soil pH too high - sulfur application needed')
        
        # Analyser la température
        if self.air_temperature > 35:
            issues.append('High temperature - heat stress risk')
        elif self.air_temperature < 5:
            issues.append('Low temperature - frost risk')
        
        # Déterminer le statut de santé
        if len(issues) == 0:
            self.health_status = 'excellent'
        elif len(issues) <= 2:
            self.health_status = 'good'
        elif len(issues) <= 4:
            self.health_status = 'fair'
        else:
            self.health_status = 'poor'
        
        self.recommendations = issues
        return issues
    
    @staticmethod
    def get_all(zone=None, health_status=None, limit=None):
        """Récupérer toutes les mesures agricoles"""
        query = {}
        if zone:
            query['zone'] = zone
        if health_status:
            query['health_status'] = health_status
        
        cursor = mongo.db.agriculture.find(query).sort('created_at', -1)
        if limit:
            cursor = cursor.limit(limit)
        return [Agriculture(doc) for doc in cursor]
    
    @staticmethod
    def get_by_id(agri_id):
        """Récupérer une mesure par ID"""
        try:
            if isinstance(agri_id, str):
                agri_id = ObjectId(agri_id)
            doc = mongo.db.agriculture.find_one({'_id': agri_id})
            if doc:
                return Agriculture(doc)
        except Exception as e:
            print(f"Error getting agriculture by id: {e}")
        return None
    
    @staticmethod
    def create(data):
        """Créer une nouvelle mesure agricole"""
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        
        result = mongo.db.agriculture.insert_one(data)
        return Agriculture.get_by_id(result.inserted_id)
    
    @staticmethod
    def get_stats(zone=None):
        """Obtenir les statistiques agricoles"""
        match_stage = {}
        if zone:
            match_stage['zone'] = zone
        
        pipeline = [
            {'$match': match_stage},
            {
                '$group': {
                    '_id': None,
                    'count': {'$sum': 1},
                    'avg_soil_moisture': {'$avg': '$soil_moisture'},
                    'avg_soil_temperature': {'$avg': '$soil_temperature'},
                    'avg_air_temperature': {'$avg': '$air_temperature'},
                    'avg_air_humidity': {'$avg': '$air_humidity'},
                    'irrigation_needed': {
                        '$sum': {'$cond': ['$irrigation_needed', 1, 0]}
                    }
                }
            }
        ]
        
        result = list(mongo.db.agriculture.aggregate(pipeline))
        if result:
            stats = result[0]
            del stats['_id']
            return {k: round(v, 2) if isinstance(v, float) else v for k, v in stats.items()}
        return {}
