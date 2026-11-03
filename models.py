from pymongo import MongoClient
from datetime import datetime
from config import Config
import bcrypt

class MongoDB:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        
        # Collections
        self.users = self.db['users']
        self.historique = self.db['historique']
        self.alertes = self.db['alertes']
        self.historique_vidanges = self.db['historique_vidanges']
        
        # Initialiser les utilisateurs par défaut
        self.init_default_users()
    
    def init_default_users(self):
        """Créer les utilisateurs par défaut s'ils n'existent pas"""
        
        # Admin par défaut
        if not self.users.find_one({'username': 'admin'}):
            admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            self.users.insert_one({
                'username': 'admin',
                'password': admin_password,
                'role': 'admin',
                'nom': 'Administrateur',
                'email': 'admin@smartsafi.ma',
                'telephone': '+212 5 23 45 67 89',
                'regions': [],  # admin n’a pas de régions spécifiques
                'actif': True,
                'created_at': datetime.now(),
                'last_login': None
            })
            print("✅ Compte admin créé")
        
        # Chauffeur par défaut
        if not self.users.find_one({'username': 'chauffeur'}):
            chauffeur_password = bcrypt.hashpw('chauffeur123'.encode('utf-8'), bcrypt.gensalt())
            self.users.insert_one({
                'username': 'chauffeur',
                'password': chauffeur_password,
                'role': 'chauffeur',
                'nom': 'Chauffeur Principal',
                'email': 'chauffeur@smartsafi.ma',
                'telephone': '+212 6 12 34 56 78',
                'regions': [],  # par défaut, aucune région assignée ( = toutes)
                'actif': True,
                'created_at': datetime.now(),
                'last_login': None
            })
            print("✅ Compte chauffeur créé")
    
    def authenticate_user(self, username, password, role=None):
        """Authentifier un utilisateur par nom ou email"""
        query = {
            '$or': [
                {'username': username},
                {'email': username}
            ],
            'actif': True
        }
        if role:
            query['role'] = role
        user = self.users.find_one(query)
        
        if user:
            stored_password = user['password']
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                self.users.update_one(
                    {'_id': user['_id']},
                    {'$set': {'last_login': datetime.now()}}
                )
                return {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'role': user['role'],
                    'nom': user.get('nom', ''),
                    'email': user.get('email', ''),
                    'regions': user.get('regions', [])
                }
        return None
    
    def get_user_by_username(self, username):
        """Récupérer un utilisateur par son nom"""
        return self.users.find_one({'username': username})
    
    def create_user(self, username, password, role, nom, email, telephone, regions=None):
        """Créer un nouvel utilisateur (avec régions optionnelles)"""
        if self.users.find_one({'username': username}):
            return None, "Nom d'utilisateur déjà existant"
        
        if regions is None:
            regions = []
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user = {
            'username': username,
            'password': hashed_password,
            'role': role,
            'nom': nom,
            'email': email,
            'telephone': telephone,
            'regions': regions,
            'actif': True,
            'created_at': datetime.now(),
            'last_login': None
        }
        
        result = self.users.insert_one(user)
        return str(result.inserted_id), "Utilisateur créé avec succès"
    
    def update_user(self, user_id, updates):
        """Mettre à jour un utilisateur (autorise la modification des régions)"""
        allowed_updates = ['nom', 'email', 'telephone', 'actif', 'regions', 'password']
        update_data = {k: v for k, v in updates.items() if k in allowed_updates}
        
        if update_data:
            self.users.update_one({'_id': user_id}, {'$set': update_data})
            return True
        return False
    
    def delete_user(self, user_id):
        """Désactiver un utilisateur (suppression logique)"""
        self.users.update_one({'_id': user_id}, {'$set': {'actif': False}})
        return True
    
    def get_all_users(self):
        """Récupérer tous les utilisateurs"""
        users = self.users.find({}, {'password': 0})
        return list(users)
    
    def get_users_by_role(self, role):
        """Récupérer les utilisateurs par rôle (inclut le champ regions)"""
        users = self.users.find({'role': role, 'actif': True}, {'password': 0})
        return list(users)
    
    # === MÉTHODES POUR L'HISTORIQUE GÉNÉRAL ===
    def add_historique(self, service, action, details, username=None):
        """Ajouter une entrée dans l'historique général"""
        entry = {
            'service': service,
            'action': action,
            'details': details,
            'username': username,
            'timestamp': datetime.now()

            
        }
        self.historique.insert_one(entry)
    
    def get_historique(self, limit=100, service=None):
        """Récupérer l'historique général"""
        query = {}
        if service:
            query['service'] = service
        
        entries = self.historique.find(query).sort('timestamp', -1).limit(limit)
        return list(entries)
    
    # === MÉTHODES POUR L'HISTORIQUE DES VIDANGES ===
    def ajouter_vidange(self, region, camion_type, nb_poubelles, nb_urgentes):
        """Ajouter une entrée dans l'historique des vidanges"""
        entry = {
            'region': region,
            'camionType': camion_type,
            'nbPoubellesVidees': nb_poubelles,
            'nbUrgentes': nb_urgentes,
            'date': datetime.now()
        }
        self.historique_vidanges.insert_one(entry)
        return str(entry['_id'])
    
    def get_vidanges(self, region=None, limit=50):
        """Récupérer l'historique des vidanges (par région optionnelle)"""
        query = {}
        if region:
            query['region'] = region
        vidanges = self.historique_vidanges.find(query).sort('date', -1).limit(limit)
        return list(vidanges)
    
    # === MÉTHODES POUR LES ALERTES ===
    def add_alerte(self, type_alerte, niveau, message, service):
        """Ajouter une alerte"""
        alerte = {
            'type': type_alerte,
            'niveau': niveau,
            'message': message,
            'service': service,
            'timestamp': datetime.now(),
            'lu': False
        }
        self.alertes.insert_one(alerte)
    
    def get_alertes_non_lues(self):
        """Récupérer les alertes non lues"""
        alertes = self.alertes.find({'lu': False}).sort('timestamp', -1)
        return list(alertes)
    
    def marquer_alerte_lue(self, alerte_id):
        """Marquer une alerte comme lue"""
        self.alertes.update_one({'_id': alerte_id}, {'$set': {'lu': True}})

# Instance globale
db = MongoDB()