

# 🌊 SmartSafi — Plateforme Smart City pour Safi

**Vers une gestion urbaine plus intelligente, connectée et durable.**

SmartSafi est un projet de plateforme Smart City open source visant à centraliser et structurer les données de différents domaines urbains afin de faciliter leur consultation, leur suivi et leur exploitation.

Développé avec Python et Flask, le projet repose sur une architecture modulaire organisée autour de cinq domaines : la gestion des déchets, l'eau, la qualité de l'air, l'agriculture et l'éclairage public.
[![Python](https://img.shields.io/badge/python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.3+-000000?logo=flask)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/mongodb-4.0+-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![MQTT](https://img.shields.io/badge/mqtt-IoT--ready-660066?logo=eclipsemosquitto)](https://mqtt.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-contribuer)

[Démarrage en 2 minutes](#-démarrage-en-2-minutes) ·
[Innovation](#-ce-qui-rend-smartsafi-différent) ·
[Architecture](#-architecture) ·
[API](#-api) ·
[Roadmap](#-roadmap)
---

## 🎯 Objectifs du projet

Les données urbaines sont souvent réparties entre plusieurs services et systèmes. SmartSafi propose une approche centralisée permettant de regrouper ces différents domaines dans une même plateforme.

Les principaux objectifs sont :

- Centraliser les informations liées aux différents services urbains.
- Structurer les données pour faciliter leur exploitation.
- Proposer une architecture modulaire et évolutive.
- Faciliter le suivi des indicateurs à travers une interface de visualisation.
- Préparer l'intégration de technologies IoT et de mécanismes d'analyse avancée.

---

## 🧩 Les cinq domaines de SmartSafi

| Domaine | Données concernées |
|---|---|
| ♻️ Gestion des déchets | Remplissage, statut et localisation des bennes |
| 💧 Gestion de l'eau | pH, turbidité, conductivité et température |
| 🌫️ Qualité de l'air | PM2.5, PM10, O₃, NO₂, SO₂ et CO |
| 🌱 Agriculture intelligente | Humidité, température, pH et nutriments du sol |
| 💡 Éclairage public | État, intensité et consommation énergétique |

Ces domaines constituent les axes fonctionnels de la plateforme. La disponibilité de données réelles dépend de l'intégration des sources et équipements correspondants.

---

## ⚙️ Fonctionnalités et socle technique

Le projet s'appuie sur une architecture backend modulaire développée avec Flask.

Les principaux éléments du socle sont :

- **Architecture modulaire Flask** : organisation du backend en modules et blueprints.
- **Gestion des données** : utilisation de MongoDB pour structurer et stocker les informations.
- **API REST** : organisation des échanges de données entre les différentes parties de l'application.
- **Interface web** : visualisation des informations à l'aide de technologies web.
- **Organisation par domaine** : séparation des fonctionnalités liées aux cinq axes de SmartSafi.

---

## 🏗️ Architecture technique

```text
SmartSafi
│
├── Backend
│   ├── Python
│   ├── Flask
│   ├── Blueprints
│   └── API REST
│
├── Data Layer
│   └── MongoDB
│
├── Frontend
│   ├── Bootstrap 5
│   ├── JavaScript / jQuery
│   ├── Chart.js
│   └── Leaflet
│
└── Domaines fonctionnels
    ├── Déchets
    ├── Eau
    ├── Air
    ├── Agriculture
    └── Éclairage
```

### Stack technique

| Catégorie | Technologies |
|---|---|
| Langage | Python |
| Backend | Flask |
| Base de données | MongoDB |
| API | REST |
| IoT | MQTT / Paho-MQTT |
| Interface | HTML, CSS, JavaScript |
| Framework CSS | Bootstrap 5 |
| Visualisation | Chart.js |
| Cartographie | Leaflet |
| Versionnement | Git, GitHub |

---

## 🗺️ Perspectives d'évolution

Plusieurs fonctionnalités avancées sont envisagées pour enrichir progressivement la plateforme.

| Fonctionnalité | État |
|---|---|
| Architecture modulaire et cinq domaines | Socle du projet |
| Amélioration de la validation des données | À développer |
| Notifications avancées | En évolution |
| Moteur de corrélation inter-domaines | En conception |
| Prévision du remplissage des bennes | En conception |
| Indice de Résilience Urbaine (IRU) | En conception |
| Simulation et jumeau numérique | Perspective à long terme |
| Application mobile | Perspective à long terme |
| Portail Open Data | Perspective à long terme |

**Important :** les fonctionnalités indiquées comme étant en conception ou en perspective ne sont pas présentées comme des fonctionnalités déjà opérationnelles.

---

## 🚀 Installation

### Prérequis

- Python 3.8+
- MongoDB
- Git

### Étapes

```bash
# Cloner le dépôt
git clone https://github.com/fatima1234-cheg/SmartSafi.git

# Accéder au projet
cd SmartSafi

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement sous Windows
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python run.py
```

*Vérifier les noms du dépôt, du fichier de dépendances et du point d'entrée avec la structure réelle du projet avant publication.*

---

## 📁 Structure du projet

```text
smartsafi/
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   ├── templates/
│   └── static/
│
├── config/
├── tests/
├── docs/
├── scripts/
├── run.py
└── wsgi.py
```

---

## 🌍 Vision du projet

SmartSafi ambitionne de proposer une approche centralisée de la gestion urbaine, en mettant les données au service d'une meilleure compréhension des enjeux environnementaux et opérationnels de la ville de Safi.

Le projet constitue une base technique évolutive sur laquelle pourront être intégrées progressivement des fonctionnalités IoT, des mécanismes d'analyse avancée et des outils d'aide à la décision.

---

## 👩‍💻 Développé par

**Fatima Chegdani**

Étudiante ingénieure en Génie Informatique et Intelligence Artificielle — ENSA Safi.

<p>
  <a href="https://fatima1234-cheg.github.io/portfolio-fatima/">
    <img src="https://img.shields.io/badge/Portfolio-6366F1?style=flat-square&logo=googlechrome&logoColor=white" alt="Portfolio" />
  </a>
  <a href="https://www.linkedin.com/in/fatima-chegdani-44b840274/">
    <img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn" />
  </a>
  <a href="https://github.com/fatima1234-cheg">
    <img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub" />
  </a>
</p>

---

⭐ Si le projet vous intéresse, n'hésitez pas à consulter le dépôt et à contribuer à son évolution.

