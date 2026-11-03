# SmartSafi - Smart City Management Platform

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask 2.3+](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/mongodb-4.0+-yellow.svg)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

SmartSafi est une plateforme de gestion de ville intelligente (Smart City) conçue pour la ville de Safi, Maroc. Elle intègre la gestion des déchets, la qualité de l'eau, la qualité de l'air, l'agriculture intelligente et l'éclairage public.

---

## Sommaire

- [Caractéristiques](#caractéristiques)
- [Architecture Technique](#architecture-technique)
- [Installation](#installation)
- [Configuration](#configuration)
- [Structure du Projet](#structure-du-projet)
- [API Endpoints](#api-endpoints)
- [MQTT Topics](#mqtt-topics)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [Contribution](#contribution)
- [Licence](#licence)

---

## Caractéristiques

### Modules Smart City

- **Gestion des Déchets** : Suivi des poubelles connectées dans 4 régions (Nord, Sud, Est, Ouest)
- **Qualité de l'Eau** : Surveillance du pH, turbidité, conductivité et température
- **Qualité de l'Air** : Mesure des polluants (PM2.5, PM10, O3, NO2, SO2, CO)
- **Agriculture Intelligente** : Capteurs de sol (humidité, température, pH, NPK)
- **Éclairage Public** : Gestion intelligente des lampadaires LED dans 2 quartiers

### Fonctionnalités Générales

- **Authentification sécurisée** : JWT + sessions Flask-Login
- **Tableaux de bord interactifs** : Visualisation en temps réel avec Chart.js
- **Cartographie** : Cartes interactives avec Leaflet.js
- **Communication IoT** : MQTT pour la communication temps réel
- **Notifications** : Alertes email et notifications push
- **API RESTful** : API complète pour l'intégration tierce
- **Gestion des utilisateurs** : Rôles (admin, driver, operator, viewer)

---

## Architecture Technique

### Stack Technologique

| Couche | Technologie |
|--------|-------------|
| **Backend** | Python 3.8+, Flask 2.3+ |
| **Base de données** | MongoDB 4.0+ |
| **ODM** | Flask-PyMongo |
| **Authentification** | Flask-Login, JWT |
| **Formulaires** | Flask-WTF, WTForms |
| **Email** | Flask-Mail |
| **Limitation de taux** | Flask-Limiter |
| **MQTT** | Paho-MQTT |
| **Frontend** | HTML5, CSS3, JavaScript |
| **CSS Framework** | Bootstrap 5 |
| **Icons** | Font Awesome 6 |
| **Charts** | Chart.js 3+ |
| **Maps** | Leaflet.js |
| **JS Utilities** | jQuery 3.6+ |

### Diagramme d'Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Web UI    │  │ Mobile App  │  │    Third-party API    │  │
│  │  (Browser)  │  │  (Future)   │  │       Clients         │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬───────────┘  │
└─────────┼────────────────┼───────────────────────┼──────────────┘
          │                │                       │
          └────────────────┴───────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │    Nginx/Apache    │
                    │  (Reverse Proxy)   │
                    └─────────┬──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
   ┌──────▼──────┐   ┌────────▼───────┐  ┌──────▼──────┐
   │   Flask     │   │   Flask        │  │   Flask     │
   │   App 1     │   │   App 2        │  │   App N     │
   │  (Gunicorn) │   │   (Gunicorn)   │  │  (Gunicorn) │
   └──────┬──────┘   └────────┬───────┘  └──────┬──────┘
          │                   │                  │
          └───────────────────┴──────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │      MongoDB       │
                    │   (Primary-Replica) │
                    │     Cluster         │
                    └─────────┬──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
   ┌──────▼──────┐   ┌────────▼───────┐  ┌──────▼──────┐
   │   MQTT      │   │   Redis        │  │   External  │
   │   Broker    │   │   (Cache)      │  │   Services  │
   │(Mosquitto)   │   │                │  │  (Email, SMS)│
   └─────────────┘   └────────────────┘  └─────────────┘
```

---

## Installation

### Prérequis

- Python 3.8+
- MongoDB 4.0+
- Node.js 14+ (pour les outils de build frontend)
- Git

### Installation locale

1. **Cloner le repository**

```bash
git clone https://github.com/votre-org/smartsafi.git
cd smartsafi
```

2. **Créer un environnement virtuel**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances**

```bash
# Installation de base
pip install -r requirements.txt

# Pour le développement
pip install -r requirements-dev.txt
```

4. **Configurer les variables d'environnement**

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos paramètres
nano .env
```

5. **Initialiser la base de données**

```bash
# Créer les collections et index
flask init-db

# Créer un administrateur
flask create-admin --username admin --email admin@smartsafi.com
```

6. **Lancer l'application**

```bash
# Mode développement
python run.py

# Ou avec Flask CLI
flask run --debug

# Mode production
python wsgi.py
```

L'application sera accessible à `http://localhost:5000`

---

## Configuration

### Variables d'environnement principales

| Variable | Description | Défaut |
|----------|-------------|---------|
| `FLASK_ENV` | Environnement Flask | `development` |
| `SECRET_KEY` | Clé secrète Flask | **Requis en prod** |
| `MONGO_URI` | URI MongoDB | `mongodb://localhost:27017/smartsafi` |
| `MQTT_BROKER_HOST` | Hôte MQTT | `localhost` |
| `MQTT_BROKER_PORT` | Port MQTT | `1883` |
| `MAIL_SERVER` | Serveur SMTP | - |
| `MAIL_PORT` | Port SMTP | `587` |
| `MAIL_USERNAME` | Email expéditeur | - |
| `MAIL_PASSWORD` | Mot de passe email | - |

### Configuration par environnement

**Développement** (`config/development.py`):
- Debug activé
- Base de données locale
- Emails simulés
- Logging verbeux

**Production** (`config/production.py`):
- Debug désactivé
- HTTPS obligatoire
- Rate limiting activé
- Logging structuré

**Test** (`config/testing.py`):
- Base de données en mémoire
- Services externes mockés
- Couverture de code

---

## Structure du Projet

```
smartsafi/
├── app/                          # Application Flask
│   ├── __init__.py              # Application Factory
│   ├── models/                  # Modèles MongoDB
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── waste.py
│   │   ├── water.py
│   │   ├── air.py
│   │   ├── agriculture.py
│   │   ├── lighting.py
│   │   └── history.py
│   ├── routes/                  # Blueprints
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── api.py
│   │   ├── waste.py
│   │   ├── water.py
│   │   ├── air.py
│   │   ├── agriculture.py
│   │   ├── lighting.py
│   │   └── history.py
│   ├── services/                # Services métier
│   │   ├── __init__.py
│   │   ├── mqtt_service.py
│   │   ├── optimization_service.py
│   │   └── notification_service.py
│   ├── utils/                   # Utilitaires
│   │   ├── __init__.py
│   │   ├── data_store.py
│   │   ├── decorators.py
│   │   └── validators.py
│   ├── templates/               # Templates HTML
│   │   ├── layouts/
│   │   ├── partials/
│   │   └── pages/
│   └── static/                  # Fichiers statiques
│       ├── css/
│       ├── js/
│       └── img/
├── config/                      # Configurations
│   ├── __init__.py
│   ├── base.py
│   ├── development.py
│   ├── production.py
│   └── testing.py
├── tests/                       # Tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_api.py
│   └── test_models.py
├── docs/                        # Documentation
│   ├── architecture.md
│   └── api.md
├── scripts/                     # Scripts utilitaires
│   ├── setup.sh
│   ├── setup.bat
│   └── backup.sh
├── logs/                        # Logs (créé automatiquement)
├── .env.example                 # Exemple de variables d'environnement
├── .gitignore                   # Fichiers ignorés par Git
├── requirements.txt             # Dépendances de base
├── requirements-dev.txt         # Dépendances développement
├── requirements-prod.txt        # Dépendances production
├── run.py                       # Point d'entrée développement
└── wsgi.py                      # Point d'entrée production
```

---

## API Endpoints

### Authentification

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/login` | Connexion utilisateur |
| POST | `/auth/logout` | Déconnexion |
| POST | `/auth/register` | Inscription (admin seulement) |
| POST | `/auth/password` | Changement de mot de passe |

### Dashboard

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/dashboard` | Tableau de bord principal |
| GET | `/dashboard/stats` | Statistiques globales |

### API V1

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/waste` | Liste des poubelles |
| POST | `/api/v1/waste` | Créer une poubelle |
| GET | `/api/v1/waste/:id` | Détails d'une poubelle |
| PUT | `/api/v1/waste/:id` | Mettre à jour une poubelle |
| DELETE | `/api/v1/waste/:id` | Supprimer une poubelle |

... et plus pour water, air, agriculture, lighting

### Documentation API

La documentation complète de l'API est disponible à `/api/docs` quand l'application est en cours d'exécution.

---

## MQTT Topics

### Structure des Topics

```
smartsafi/{domain}/{action}/{id}
```

### Topics par Domaine

#### Waste Management
```
smartsafi/waste/+/fill_level    # Niveau de remplissage
smartsafi/waste/+/status        # Statut de la poubelle
smartsafi/waste/+/location      # Position GPS
smartsafi/waste/command/collect # Commande de collecte
```

#### Water Quality
```
smartsafi/water/+/ph            # Niveau de pH
smartsafi/water/+/turbidity     # Turbidité
smartsafi/water/+/conductivity  # Conductivité
smartsafi/water/+/temperature   # Température
```

#### Air Quality
```
smartsafi/air/+/pm25            # Particules PM2.5
smartsafi/air/+/pm10            # Particules PM10
smartsafi/air/+/o3              # Ozone
smartsafi/air/+/no2             # Dioxyde d'azote
smartsafi/air/+/so2             # Dioxyde de soufre
smartsafi/air/+/co              # Monoxyde de carbone
```

#### Agriculture
```
smartsafi/agriculture/+/soil_moisture   # Humidité du sol
smartsafi/agriculture/+/soil_temperature # Température du sol
smartsafi/agriculture/+/soil_ph         # pH du sol
smartsafi/agriculture/+/npk_n           # Azote
smartsafi/agriculture/+/npk_p           # Phosphore
smartsafi/agriculture/+/npk_k           # Potassium
```

#### Lighting
```
smartsafi/lighting/+/status       # Statut du lampadaire
smartsafi/lighting/+/intensity   # Intensité lumineuse
smartsafi/lighting/+/energy      # Consommation d'énergie
smartsafi/lighting/command/dim   # Commande de gradation
smartsafi/lighting/command/on    # Allumer
smartsafi/lighting/command/off   # Éteindre
```

### Format des Messages

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "device_id": "bin_001",
  "value": 0.75,
  "unit": "percentage",
  "battery": 85,
  "signal_strength": -65
}
```

---

## Tests

### Exécuter les tests

```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/test_auth.py
pytest tests/test_api.py
pytest tests/test_models.py

# Avec couverture
pytest --cov=app tests/

# En mode verbeux
pytest -v

# Tests spécifiques par nom
pytest -k "test_login"
```

### Structure des tests

```
tests/
├── conftest.py          # Fixtures pytest
├── test_auth.py         # Tests d'authentification
├── test_api.py          # Tests API
├── test_models.py       # Tests des modèles
├── test_forms.py        # Tests des formulaires
└── test_services.py     # Tests des services
```

### Fixtures principales

```python
# conftest.py
import pytest
from app import create_app
from app.models import User

@pytest.fixture
def app():
    """Application de test."""
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Client de test."""
    return app.test_client()

@pytest.fixture
def admin_user(app):
    """Utilisateur admin de test."""
    return User.create(
        username='admin_test',
        email='admin@test.com',
        password='password123',
        role='admin'
    )
```

---

## Déploiement

### Déploiement avec Docker

```bash
# Construire l'image
docker build -t smartsafi:latest .

# Exécuter le conteneur
docker run -d \
  -p 5000:5000 \
  -e MONGO_URI=mongodb://mongo:27017/smartsafi \
  -e SECRET_KEY=your-secret-key \
  --name smartsafi \
  smartsafi:latest
```

### Déploiement avec Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f app

# Arrêter
docker-compose down
```

### Déploiement manuel sur serveur

```bash
# 1. Cloner le code
git clone https://github.com/votre-org/smartsafi.git
cd smartsafi

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements-prod.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
nano .env  # Éditer les valeurs

# 5. Initialiser la base de données
flask init-db
flask create-admin

# 6. Démarrer avec Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
```

### Configuration Nginx

```nginx
server {
    listen 80;
    server_name smartsafi.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/smartsafi/app/static;
        expires 30d;
    }
}
```

---

## Contribution

Les contributions sont les bienvenues ! Veuillez suivre ces étapes :

1. Forker le projet
2. Créer une branche (`git checkout -b feature/nom-fonctionnalite`)
3. Commiter vos changements (`git commit -m 'Ajout de fonctionnalité'`)
4. Pusher sur la branche (`git push origin feature/nom-fonctionnalite`)
5. Ouvrir une Pull Request

### Standards de code

- Suivre PEP 8 pour Python
- Utiliser des docstrings Google-style
- Maintenir une couverture de tests > 80%
- Passer tous les tests pylint et flake8

---

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## Contact

- **Projet** : [GitHub - SmartSafi](https://github.com/votre-org/smartsafi)
- **Documentation** : [docs.smartsafi.com](https://docs.smartsafi.com)
- **Support** : support@smartsafi.com

---

## Remerciements

- [Flask](https://flask.palletsprojects.com/) - Framework web
- [MongoDB](https://www.mongodb.com/) - Base de données NoSQL
- [Bootstrap](https://getbootstrap.com/) - Framework CSS
- [Chart.js](https://www.chartjs.org/) - Bibliothèque de graphiques
- [Leaflet](https://leafletjs.com/) - Bibliothèque de cartes

---

<p align="center">
  <strong>SmartSafi - Construire la ville intelligente de demain</strong><br>
  <em>© 2024 SmartSafi. Tous droits réservés.</em>
</p>
