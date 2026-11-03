"""
Water Quality Model for Smart City - SmartSafi
"""

from datetime import datetime
from bson.objectid import ObjectId
from app import mongo


class Water:
    """Modèle pour la qualité de l'eau"""
    
    SOURCES = ['source1', 'source2', 'source3']
    
    def __init__(self, data):
        """Initialiser le modèle Water"""
        self._id = str(data.get('_id')) if '_id' in data else None
        self.sensor_id = data.get('sensor_id', '')
        self.source = data.get('source', '')
        self.ph = data.get('ph', 7.0)
        self.turbidity = data.get('turbidity', 0)
        self.conductivity = data.get('conductivity', 0)
        self.temperature = data.get('temperature', 0)
        self.dissolved_oxygen = data.get('dissolved_oxygen', 0)
        self.nitrates = data.get('nitrates', 0)
        self.chlorine = data.get('chlorine', 0)
        self.quality_index = data.get('quality_index', 100)
        self.status = data.get('status', 'good')
        self.location = data.get('location', {})
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self._id,
            'sensor_id': self.sensor_id,
            'source': self.source,
            'ph': self.ph,
            'turbidity': self.turbidity,
            'conductivity': self.conductivity,
            'temperature': self.temperature,
            'dissolved_oxygen': self.dissolved_oxygen,
            'nitrates': self.nitrates,
            'chlorine': self.chlorine,
            'quality_index': self.quality_index,
            'status': self.status,
            'location': self.location,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    def calculate_quality_index(self):
        """Calculer l'indice de qualité de l'eau"""
        # Algorithme simplifié - à ajuster selon les normes
        score = 100
        
        # pH optimal entre 6.5 et 8.5
        if self.ph < 6.5 or self.ph > 8.5:
            score -= 20
        
        # Turbidité (NTU) - idéalement < 1
        if self.turbidity > 1:
            score -= min(20, int(self.turbidity * 5))
        
        # Conductivité (µS/cm) - normalement 50-1500
        if self.conductivity < 50 or self.conductivity > 1500:
            score -= 15
        
        self.quality_index = max(0, min(100, score))
        
        # Déterminer le statut
        if self.quality_index >= 90:
            self.status = 'excellent'
        elif self.quality_index >= 70:
            self.status = 'good'
        elif self.quality_index >= 50:
            self.status = 'fair'
        else:
            self.status = 'poor'
        
        return self.quality_index
    
    @staticmethod
    def get_all(source=None, status=None, limit=None):
        """Récupérer toutes les mesures d'eau"""
        query = {}
        if source:
            query['source'] = source
        if status:
            query['status'] = status
        
        cursor = mongo.db.water.find(query).sort('created_at', -1)
        if limit:
            cursor = cursor.limit(limit)
        return [Water(doc) for doc in cursor]
    
    @staticmethod
    def get_by_id(water_id):
        """Récupérer une mesure par ID"""
        try:
            if isinstance(water_id, str):
                water_id = ObjectId(water_id)
            doc = mongo.db.water.find_one({'_id': water_id})
            if doc:
                return Water(doc)
        except Exception as e:
            print(f"Error getting water by id: {e}")
        return None
    
    @staticmethod
    def get_latest_by_source(source, limit=1):
        """Récupérer les dernières mesures d'une source"""
        cursor = mongo.db.water.find({'source': source}) \
            .sort('created_at', -1) \
            .limit(limit)
        return [Water(doc) for doc in cursor]
    
    @staticmethod
    def create(data):
        """Créer une nouvelle mesure d'eau"""
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        
        # Calculer l'indice de qualité si les données sont disponibles
        if all(k in data for k in ['ph', 'turbidity', 'conductivity']):
            water = Water(data)
            water.calculate_quality_index()
            data['quality_index'] = water.quality_index
            data['status'] = water.status
        
        result = mongo.db.water.insert_one(data)
        return Water.get_by_id(result.inserted_id)
    
    @staticmethod
    def update(water_id, data):
        """Mettre à jour une mesure d'eau"""
        try:
            if isinstance(water_id, str):
                water_id = ObjectId(water_id)
            data['updated_at'] = datetime.utcnow()
            mongo.db.water.update_one({'_id': water_id}, {'$set': data})
            return Water.get_by_id(water_id)
        except Exception as e:
            print(f"Error updating water: {e}")
            return None
    
    @staticmethod
    def delete(water_id):
        """Supprimer une mesure d'eau"""
        try:
            if isinstance(water_id, str):
                water_id = ObjectId(water_id)
            result = mongo.db.water.delete_one({'_id': water_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting water: {e}")
            return False
    
    @staticmethod
    def get_stats(source=None):
        """Obtenir les statistiques de qualité de l'eau"""
        match_stage = {}
        if source:
            match_stage['source'] = source
        
        pipeline = [
            {'$match': match_stage},
            {
                '$group': {
                    '_id': None,
                    'count': {'$sum': 1},
                    'avg_ph': {'$avg': '$ph'},
                    'avg_turbidity': {'$avg': '$turbidity'},
                    'avg_conductivity': {'$avg': '$conductivity'},
                    'avg_temperature': {'$avg': '$temperature'},
                    'avg_quality_index': {'$avg': '$quality_index'},
                    'good_quality': {
                        '$sum': {'$cond': [{'$gte': ['$quality_index', 70]}, 1, 0]}
                    }
                }
            }
        ]
        
        result = list(mongo.db.water.aggregate(pipeline))
        if result:
            stats = result[0]
            del stats['_id']
            return {k: round(v, 2) if isinstance(v, float) else v for k, v in stats.items()}
        return {
            'count': 0,
            'avg_ph': 0,
            'avg_turbidity': 0,
            'avg_conductivity': 0,
            'avg_temperature': 0,
            'avg_quality_index': 0,
            'good_quality': 0
        }
    
    @staticmethod
    def get_source_stats():
        """Obtenir les statistiques par source"""
        pipeline = [
            {
                '$group': {
                    '_id': '$source',
                    'count': {'$sum': 1},
                    'avg_ph': {'$avg': '$ph'},
                    'avg_quality_index': {'$avg': '$quality_index'}
                }
            }
        ]
        
        results = list(mongo.db.water.aggregate(pipeline))
        return {r['_id']: {
            'count': r['count'],
            'avg_ph': round(r['avg_ph'], 2),
            'avg_quality_index': round(r['avg_quality_index'], 2)
        } for r in results}
