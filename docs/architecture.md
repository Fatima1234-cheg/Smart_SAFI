# Architecture de SmartSafi

## Vue d'ensemble

SmartSafi est une application web Flask suivant l'architecture MVC (Model-View-Controller) avec une séparation claire des responsabilités.

## Architecture en couches

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION                             │
├─────────────────────────────────────────────────────────────────┤
│  Templates HTML    │    Static Files    │    JavaScript       │
│  (Jinja2)          │    (CSS, Images)   │    (Chart.js, etc.) │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION                              │
├─────────────────────────────────────────────────────────────────┤
│  Routes/Blueprints  │    Controllers     │    Middleware       │
│  (URL Mapping)      │    (Request/Resp)  │    (Auth, etc.)     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          SERVICES                               │
├─────────────────────────────────────────────────────────────────┤
│  Business Logic    │    MQTT Service    │    Notification     │
│  (Domain Logic)    │    (IoT Comm.)     │    (Email, etc.)  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          DATA                                   │
├─────────────────────────────────────────────────────────────────┤
│  Models (ORM)      │    Data Access     │    External APIs   │
│  (MongoDB/ODM)     │    (Repository)    │    (Third-party)   │
└─────────────────────────────────────────────────────────────────┘
```

## Composants principaux

### 1. Modèles (Models)

Les modèles définissent la structure des données et interagissent avec MongoDB.

```python
# Exemple: app/models/waste.py
class Waste:
    """Modèle pour la gestion des déchets"""
    
    def __init__(self, data):
        self._id = str(data.get('_id'))
        self.bin_id = data.get('bin_id')
        self.region = data.get('region')
        # ...
```

### 2. Routes (Routes/Blueprints)

Les blueprints définissent les points d'entrée de l'API et les routes web.

```python
# Exemple: app/routes/waste.py
from flask import Blueprint

waste_bp = Blueprint('waste', __name__)

@waste_bp.route('/')
def index():
    """Page de gestion des déchets"""
    # ...
```

### 3. Services (Services)

Les services encapsulent la logique métier complexe.

```python
# Exemple: app/services/optimization_service.py
def optimize_routes(bins, depot=None):
    """Optimiser les routes de collecte"""
    # Algorithme d'optimisation
    # ...
```

### 4. Utilitaires (Utils)

Les utilitaires fournissent des fonctions auxiliaires.

```python
# Exemple: app/utils/decorators.py
def admin_required(f):
    """Vérifier que l'utilisateur est admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # ...
    return decorated_function
```

## Flux de données

### 1. Requête HTTP

```
Client → Route → Controller → Service → Model → Database
```

### 2. Réponse HTTP

```
Database → Model → Service → Controller → Route → Client
```

### 3. Communication MQTT

```
IoT Device → MQTT Broker → MQTT Service → Model → Database
```

## Patterns utilisés

### 1. Factory Pattern

Utilisé pour créer l'application Flask.

```python
# app/__init__.py
def create_app(config_name=None):
    app = Flask(__name__)
    # Configuration...
    return app
```

### 2. Repository Pattern

Utilisé dans les modèles pour abstraire l'accès aux données.

```python
# app/models/waste.py
@staticmethod
def get_by_id(waste_id):
    doc = mongo.db.waste.find_one({'_id': waste_id})
    return Waste(doc) if doc else None
```

### 3. Service Layer Pattern

Utilisé pour encapsuler la logique métier.

```python
# app/services/optimization_service.py
def optimize_routes(bins, depot=None):
    # Logique métier complexe
    pass
```

### 4. Blueprint Pattern

Utilisé pour organiser les routes.

```python
# app/routes/waste.py
waste_bp = Blueprint('waste', __name__)

@waste_bp.route('/')
def index():
    pass
```

## Sécurité

### 1. Authentification
- JWT tokens pour l'API
- Sessions pour le web
- Bcrypt pour le hachage des mots de passe

### 2. Autorisation
- Rôles: admin, operator, driver, viewer
- Permissions granulaires
- Décorateurs pour la vérification des droits

### 3. Protection
- CSRF tokens
- Rate limiting
- Validation des entrées
- Échappement des sorties

## Performance

### 1. Cache
- Cache des requêtes fréquentes
- Cache des statistiques
- Cache des sessions

### 2. Optimisation
- Index MongoDB
- Pagination des résultats
- Requêtes asynchrones

### 3. Monitoring
- Logs structurés
- Métriques de performance
- Alertes automatiques

## Conclusion

Cette architecture est conçue pour être :
- **Modulaire** : Facile à maintenir et étendre
- **Évolutive** : Supporte la croissance du trafic
- **Sécurisée** : Protège les données sensibles
- **Performante** : Répond rapidement aux requêtes

Pour toute question sur l'architecture, consultez la documentation ou contactez l'équipe de développement.
