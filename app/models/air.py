"""
Air Quality Model for Smart City - SmartSafi
"""

from datetime import datetime
from bson.objectid import ObjectId
from app import mongo


class Air:
    """Modèle pour la qualité de l'air"""
    
    STATIONS = ['centre', 'industriel', 'residentiel']
    
    def __init__(self, data):
        """Initialiser le modèle Air"""
        self._id = str(data.get('_id')) if '_id' in data else None
        self.sensor_id = data.get('sensor_id', '')
        self.station = data.get('station', '')
        self.pm25 = data.get('pm25', 0)
        self.pm10 = data.get('pm10', 0)
        self.o3 = data.get('o3', 0)
        self.no2 = data.get('no2', 0)
        self.so2 = data.get('so2', 0)
        self.co = data.get('co', 0)
        self.temperature = data.get('temperature', 0)
        self.humidity = data.get('humidity', 0)
        self.pressure = data.get('pressure', 0)
        self.aqi = data.get('aqi', 0)
        self.status = data.get('status', 'good')
        self.location = data.get('location', {})
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self._id,
            'sensor_id': self.sensor_id,
            'station': self.station,
            'pm25': self.pm25,
            'pm10': self.pm10,
            'o3': self.o3,
            'no2': self.no2,
            'so2': self.so2,
            'co': self.co,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'aqi': self.aqi,
            'status': self.status,
            'location': self.location,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    def calculate_aqi(self):
        """Calculer l'AQI (Air Quality Index)"""
        # Formule simplifiée basée sur les PM2.5
        # Vraie formule AQI plus complexe
        pm25 = self.pm25
        
        if pm25 <= 12.0:
            aqi = (50 / 12.0) * pm25
        elif pm25 <= 35.4:
            aqi = ((100 - 51) / (35.4 - 12.1)) * (pm25 - 12.1) + 51
        elif pm25 <= 55.4:
            aqi = ((150 - 101) / (55.4 - 35.5)) * (pm25 - 35.5) + 101
        elif pm25 <= 150.4:
            aqi = ((200 - 151) / (150.4 - 55.5)) * (pm25 - 55.5) + 151
        elif pm25 <= 250.4:
            aqi = ((300 - 201) / (250.4 - 150.5)) * (pm25 - 150.5) + 201
        else:
            aqi = ((500 - 301) / (500.4 - 250.5)) * (pm25 - 250.5) + 301
        
        self.aqi = int(aqi)
        
        # Déterminer le statut
        if self.aqi <= 50:
            self.status = 'good'
        elif self.aqi <= 100:
            self.status = 'moderate'
        elif self.aqi <= 150:
            self.status = 'unhealthy_sensitive'
        elif self.aqi <= 200:
            self.status = 'unhealthy'
        elif self.aqi <= 300:
            self.status = 'very_unhealthy'
        else:
            self.status = 'hazardous'
        
        return self.aqi
    
    @staticmethod
    def get_all(station=None, status=None, limit=None):
        """Récupérer toutes les mesures d'air"""
        query = {}
        if station:
            query['station'] = station
        if status:
            query['status'] = status
        
        cursor = mongo.db.air.find(query).sort('created_at', -1)
        if limit:
            cursor = cursor.limit(limit)
        return [Air(doc) for doc in cursor]
    
    @staticmethod
    def get_by_id(air_id):
        """Récupérer une mesure par ID"""
        try:
            if isinstance(air_id, str):
                air_id = ObjectId(air_id)
            doc = mongo.db.air.find_one({'_id': air_id})
            if doc:
                return Air(doc)
        except Exception as e:
            print(f"Error getting air by id: {e}")
        return None
    
    @staticmethod
    def create(data):
        """Créer une nouvelle mesure d'air"""
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        
        # Calculer l'AQI si les données PM2.5 sont disponibles
        if 'pm25' in data:
            air = Air(data)
            air.calculate_aqi()
            data['aqi'] = air.aqi
            data['status'] = air.status
        
        result = mongo.db.air.insert_one(data)
        return Air.get_by_id(result.inserted_id)
    
    @staticmethod
    def get_stats(station=None):
        """Obtenir les statistiques de qualité de l'air"""
        match_stage = {}
        if station:
            match_stage['station'] = station
        
        pipeline = [
            {'$match': match_stage},
            {
                '$group': {
                    '_id': None,
                    'count': {'$sum': 1},
                    'avg_pm25': {'$avg': '$pm25'},
                    'avg_pm10': {'$avg': '$pm10'},
                    'avg_aqi': {'$avg': '$aqi'},
                    'max_aqi': {'$max': '$aqi'},
                    'unhealthy_days': {
                        '$sum': {'$cond': [{'$gt': ['$aqi', 100]}, 1, 0]}
                    }
                }
            }
        ]
        
        result = list(mongo.db.air.aggregate(pipeline))
        if result:
            stats = result[0]
            del stats['_id']
            return {k: round(v, 2) if isinstance(v, float) else v for k, v in stats.items()}
        return {}
