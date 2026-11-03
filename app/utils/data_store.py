"""
Data Store for Smart City - SmartSafi
Legacy data storage for backward compatibility
"""

from datetime import datetime
from typing import Dict, List, Any


class DataStore:
    """
    Stockage de données en mémoire pour la rétrocompatibilité.
    Les nouvelles données sont également stockées dans MongoDB via les modèles.
    """
    
    def __init__(self):
        # Déchets - Organisés par région
        self.waste_data = {
            'nord': [],
            'sud': [],
            'est': [],
            'ouest': []
        }
        
        # Eau - Organisée par source
        self.water_data = {
            'source1': [],
            'source2': [],
            'source3': []
        }
        
        # Air - Organisé par station
        self.air_data = {
            'centre': [],
            'industriel': [],
            'residentiel': []
        }
        
        # Agriculture - Organisée par zone
        self.agriculture_data = {
            'zone_a': [],
            'zone_b': [],
            'zone_c': [],
            'zone_d': []
        }
        
        # Éclairage - Organisé par quartier
        self.lighting_data = {
            'quartier_a': [],
            'quartier_b': []
        }
        
        # Historique des actions
        self.history = []
        
        # Alertes
        self.alerts = []
        
        # Statistiques en cache
        self.stats_cache = {}
        
        # Configuration
        self.config = {
            'waste_threshold': 80,  # Seuil de remplissage pour alerte
            'water_ph_min': 6.5,
            'water_ph_max': 8.5,
            'air_aqi_threshold': 100,
            'lighting_auto': True,
            'lighting_on_time': '18:00',
            'lighting_off_time': '06:00'
        }
    
    # Méthodes pour les déchets
    def add_waste_data(self, region: str, data: Dict):
        """Ajouter des données de déchets"""
        if region in self.waste_data:
            data['timestamp'] = datetime.utcnow()
            self.waste_data[region].append(data)
            # Garder seulement les 100 dernières entrées par région
            self.waste_data[region] = self.waste_data[region][-100:]
    
    def get_waste_data(self, region: str = None) -> Dict or List:
        """Obtenir les données de déchets"""
        if region:
            return self.waste_data.get(region, [])
        return self.waste_data
    
    # Méthodes pour l'eau
    def add_water_data(self, source: str, data: Dict):
        """Ajouter des données d'eau"""
        if source in self.water_data:
            data['timestamp'] = datetime.utcnow()
            self.water_data[source].append(data)
            self.water_data[source] = self.water_data[source][-100:]
    
    def get_water_data(self, source: str = None) -> Dict or List:
        """Obtenir les données d'eau"""
        if source:
            return self.water_data.get(source, [])
        return self.water_data
    
    # Méthodes pour l'air
    def add_air_data(self, station: str, data: Dict):
        """Ajouter des données d'air"""
        if station in self.air_data:
            data['timestamp'] = datetime.utcnow()
            self.air_data[station].append(data)
            self.air_data[station] = self.air_data[station][-100:]
    
    def get_air_data(self, station: str = None) -> Dict or List:
        """Obtenir les données d'air"""
        if station:
            return self.air_data.get(station, [])
        return self.air_data
    
    # Méthodes pour l'agriculture
    def add_agriculture_data(self, zone: str, data: Dict):
        """Ajouter des données d'agriculture"""
        if zone in self.agriculture_data:
            data['timestamp'] = datetime.utcnow()
            self.agriculture_data[zone].append(data)
            self.agriculture_data[zone] = self.agriculture_data[zone][-100:]
    
    def get_agriculture_data(self, zone: str = None) -> Dict or List:
        """Obtenir les données d'agriculture"""
        if zone:
            return self.agriculture_data.get(zone, [])
        return self.agriculture_data
    
    # Méthodes pour l'éclairage
    def add_lighting_data(self, district: str, data: Dict):
        """Ajouter des données d'éclairage"""
        if district in self.lighting_data:
            data['timestamp'] = datetime.utcnow()
            self.lighting_data[district].append(data)
            self.lighting_data[district] = self.lighting_data[district][-100:]
    
    def get_lighting_data(self, district: str = None) -> Dict or List:
        """Obtenir les données d'éclairage"""
        if district:
            return self.lighting_data.get(district, [])
        return self.lighting_data
    
    # Méthodes pour l'historique
    def add_history(self, action: str, details: Dict, user: str = 'system'):
        """Ajouter une entrée d'historique"""
        entry = {
            'timestamp': datetime.utcnow(),
            'action': action,
            'details': details,
            'user': user
        }
        self.history.append(entry)
        # Garder seulement les 1000 dernières entrées
        self.history = self.history[-1000:]
    
    def get_history(self, limit: int = 100) -> List:
        """Obtenir l'historique"""
        return self.history[-limit:]
    
    # Méthodes pour les alertes
    def add_alert(self, alert_type: str, message: str, severity: str = 'info', data: Dict = None):
        """Ajouter une alerte"""
        alert = {
            'timestamp': datetime.utcnow(),
            'type': alert_type,
            'message': message,
            'severity': severity,
            'data': data or {},
            'acknowledged': False
        }
        self.alerts.append(alert)
        # Garder seulement les 500 dernières alertes
        self.alerts = self.alerts[-500:]
    
    def get_alerts(self, unacknowledged_only: bool = False, limit: int = 50) -> List:
        """Obtenir les alertes"""
        alerts = self.alerts
        if unacknowledged_only:
            alerts = [a for a in alerts if not a['acknowledged']]
        return alerts[-limit:]
    
    def acknowledge_alert(self, alert_index: int):
        """Acquitter une alerte"""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index]['acknowledged'] = True
    
    # Méthodes de configuration
    def get_config(self, key: str = None):
        """Obtenir la configuration"""
        if key:
            return self.config.get(key)
        return self.config
    
    def set_config(self, key: str, value):
        """Définir une valeur de configuration"""
        self.config[key] = value
    
    # Méthodes de statistiques
    def get_stats(self, category: str = None) -> Dict:
        """Obtenir les statistiques"""
        if category:
            return self.stats_cache.get(category, {})
        return self.stats_cache
    
    def update_stats(self, category: str, stats: Dict):
        """Mettre à jour les statistiques"""
        self.stats_cache[category] = stats


# Instance globale du data store
# Cette instance est utilisée pour la rétrocompatibilité
# Les nouvelles données sont également stockées dans MongoDB
data_store = DataStore()
