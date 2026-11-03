"""
History Model for Smart City - SmartSafi
"""

from datetime import datetime, timedelta
from bson.objectid import ObjectId
from app import mongo


class History:
    """Modèle pour l'historique des activités et événements"""
    
    CATEGORIES = [
        'waste', 'water', 'air', 'agriculture', 'lighting',
        'user_action', 'system', 'alert', 'maintenance', 'collection'
    ]
    
    LEVELS = ['info', 'warning', 'error', 'critical']
    
    def __init__(self, data):
        """Initialiser le modèle History"""
        self._id = str(data.get('_id')) if '_id' in data else None
        self.category = data.get('category', '')
        self.level = data.get('level', 'info')
        self.title = data.get('title', '')
        self.message = data.get('message', '')
        self.details = data.get('details', {})
        self.user_id = data.get('user_id')
        self.user_name = data.get('user_name', '')
        self.entity_id = data.get('entity_id')
        self.entity_type = data.get('entity_type', '')
        self.location = data.get('location', {})
        self.ip_address = data.get('ip_address', '')
        self.user_agent = data.get('user_agent', '')
        self.is_read = data.get('is_read', False)
        self.read_at = data.get('read_at')
        self.read_by = data.get('read_by', '')
        self.created_at = data.get('created_at', datetime.utcnow())
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self._id,
            'category': self.category,
            'level': self.level,
            'title': self.title,
            'message': self.message,
            'details': self.details,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'location': self.location,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if isinstance(self.read_at, datetime) else self.read_at,
            'read_by': self.read_by,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    def mark_as_read(self, user_id=None, user_name=''):
        """Marquer comme lu"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        self.read_by = user_name
        
        mongo.db.history.update_one(
            {'_id': ObjectId(self._id)},
            {'$set': {
                'is_read': True,
                'read_at': self.read_at,
                'read_by': user_name
            }}
        )
    
    @staticmethod
    def get_all(category=None, level=None, is_read=None, limit=None, skip=0):
        """Récupérer tous les historiques"""
        query = {}
        if category:
            query['category'] = category
        if level:
            query['level'] = level
        if is_read is not None:
            query['is_read'] = is_read
        
        cursor = mongo.db.history.find(query).sort('created_at', -1).skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return [History(doc) for doc in cursor]
    
    @staticmethod
    def get_by_id(history_id):
        """Récupérer un historique par ID"""
        try:
            if isinstance(history_id, str):
                history_id = ObjectId(history_id)
            doc = mongo.db.history.find_one({'_id': history_id})
            if doc:
                return History(doc)
        except Exception as e:
            print(f"Error getting history by id: {e}")
        return None
    
    @staticmethod
    def create(data):
        """Créer un nouvel historique"""
        data['created_at'] = datetime.utcnow()
        result = mongo.db.history.insert_one(data)
        return History.get_by_id(result.inserted_id)
    
    @staticmethod
    def log_event(category, level, title, message, **kwargs):
        """Créer rapidement un log d'événement"""
        data = {
            'category': category,
            'level': level,
            'title': title,
            'message': message
        }
        data.update(kwargs)
        return History.create(data)
    
    @staticmethod
    def get_unread_count(category=None):
        """Compter les notifications non lues"""
        query = {'is_read': False}
        if category:
            query['category'] = category
        return mongo.db.history.count_documents(query)
    
    @staticmethod
    def cleanup_old(days=90):
        """Nettoyer les anciens historiques"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = mongo.db.history.delete_many({
            'created_at': {'$lt': cutoff_date},
            'is_read': True
        })
        return result.deleted_count
    
    @staticmethod
    def get_stats(days=7):
        """Obtenir les statistiques d'historique"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {'$match': {'created_at': {'$gte': cutoff_date}}},
            {
                '$group': {
                    '_id': '$category',
                    'count': {'$sum': 1}
                }
            }
        ]
        
        results = list(mongo.db.history.aggregate(pipeline))
        return {r['_id']: r['count'] for r in results}
