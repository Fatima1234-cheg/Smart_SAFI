"""
Optimization Service for Smart City - SmartSafi
"""

import math
from typing import List, Dict, Tuple, Any


def calculate_distance(point1: Dict, point2: Dict) -> float:
    """
    Calculer la distance entre deux points (formule de Haversine)
    
    Args:
        point1: Premier point avec 'lat' et 'lon'
        point2: Deuxième point avec 'lat' et 'lon'
    
    Returns:
        Distance en kilomètres
    """
    lat1, lon1 = math.radians(point1['lat']), math.radians(point1['lon'])
    lat2, lon2 = math.radians(point2['lat']), math.radians(point2['lon'])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Rayon de la Terre en km
    r = 6371
    
    return c * r


def optimize_routes(bins: List[Any], depot: Dict = None) -> List[Dict]:
    """
    Optimiser les routes de collecte
    
    Args:
        bins: Liste des poubelles à collecter
        depot: Position du dépôt (optionnel)
    
    Returns:
        Liste des routes optimisées
    """
    if not bins:
        return []
    
    # Position par défaut du dépôt (centre de Safi)
    if depot is None:
        depot = {'lat': 32.2994, 'lon': -9.2372}
    
    # Taille maximale d'une tournée (capacité du camion)
    max_bins_per_route = 8
    
    # Grouper les poubelles par région
    bins_by_region = {}
    for bin_obj in bins:
        region = bin_obj.region if hasattr(bin_obj, 'region') else 'unknown'
        if region not in bins_by_region:
            bins_by_region[region] = []
        bins_by_region[region].append(bin_obj)
    
    routes = []
    route_id = 1
    
    # Pour chaque région, créer des tournées
    for region, region_bins in bins_by_region.items():
        # Diviser en tournées si nécessaire
        for i in range(0, len(region_bins), max_bins_per_route):
            route_bins = region_bins[i:i + max_bins_per_route]
            
            # Calculer la distance totale
            total_distance = 0
            prev_point = depot
            
            for bin_obj in route_bins:
                if hasattr(bin_obj, 'location') and bin_obj.location:
                    point = bin_obj.location
                    total_distance += calculate_distance(prev_point, point)
                    prev_point = point
            
            # Retour au dépôt
            total_distance += calculate_distance(prev_point, depot)
            
            route = {
                'id': route_id,
                'region': region,
                'bins': [bin_obj.to_dict() if hasattr(bin_obj, 'to_dict') else bin_obj for bin_obj in route_bins],
                'bin_count': len(route_bins),
                'estimated_distance_km': round(total_distance, 2),
                'estimated_time_minutes': round(total_distance * 5 + len(route_bins) * 3),
                'status': 'pending'
            }
            
            routes.append(route)
            route_id += 1
    
    return routes


def calculate_collection_priority(bin_obj) -> float:
    """
    Calculer la priorité de collecte d'une poubelle
    
    Args:
        bin_obj: Objet poubelle
    
    Returns:
        Score de priorité (0-100)
    """
    priority = 0
    
    # Priorité basée sur le niveau de remplissage
    if hasattr(bin_obj, 'fill_level'):
        fill_priority = bin_obj.fill_level * 0.6  # 60% du score
        priority += fill_priority
    
    # Priorité basée sur le statut
    if hasattr(bin_obj, 'status'):
        if bin_obj.status == 'critical':
            priority += 30
        elif bin_obj.status == 'full':
            priority += 20
        elif bin_obj.status == 'maintenance':
            priority += 10
    
    # Priorité basée sur la température (risque d'incendie)
    if hasattr(bin_obj, 'temperature'):
        if bin_obj.temperature > 50:
            priority += 10
    
    return min(100, priority)


def optimize_collection_schedule(bins: list, available_trucks: int = 3) -> dict:
    """
    Optimiser le planning de collecte
    
    Args:
        bins: Liste des poubelles
        available_trucks: Nombre de camions disponibles
    
    Returns:
        Planning optimisé
    """
    # Calculer les priorités
    bins_with_priority = []
    for bin_obj in bins:
        priority = calculate_collection_priority(bin_obj)
        bins_with_priority.append((bin_obj, priority))
    
    # Trier par priorité décroissante
    bins_with_priority.sort(key=lambda x: x[1], reverse=True)
    
    # Répartir les poubelles entre les camions
    trucks = {i: {'bins': [], 'total_distance': 0} for i in range(available_trucks)}
    
    for bin_obj, priority in bins_with_priority:
        # Trouver le camion avec le moins de poubelles
        min_truck = min(trucks.keys(), key=lambda k: len(trucks[k]['bins']))
        trucks[min_truck]['bins'].append({
            'bin': bin_obj,
            'priority': priority
        })
    
    return {
        'trucks': trucks,
        'total_bins': len(bins),
        'estimated_completion_time': len(bins) * 15  # 15 min par poubelle
    }


# Fonctions utilitaires pour l'optimisation

def get_bins_needing_collection(bins: list, threshold: int = 80) -> list:
    """
    Obtenir les poubelles nécessitant une collecte
    
    Args:
        bins: Liste de toutes les poubelles
        threshold: Seuil de remplissage (par défaut 80%)
    
    Returns:
        Liste des poubelles à collecter
    """
    return [bin_obj for bin_obj in bins 
            if hasattr(bin_obj, 'fill_level') and bin_obj.fill_level >= threshold]


def estimate_collection_time(num_bins: int, avg_time_per_bin: int = 10) -> int:
    """
    Estimer le temps de collecte
    
    Args:
        num_bins: Nombre de poubelles
        avg_time_per_bin: Temps moyen par poubelle (minutes)
    
    Returns:
        Temps estimé en minutes
    """
    return num_bins * avg_time_per_bin


def calculate_fuel_consumption(distance_km: float, fuel_efficiency: float = 25) -> float:
    """
    Calculer la consommation de carburant
    
    Args:
        distance_km: Distance en kilomètres
        fuel_efficiency: Efficacité en km/L (par défaut 25)
    
    Returns:
        Consommation en litres
    """
    return distance_km / fuel_efficiency
