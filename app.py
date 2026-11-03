from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
import threading
import urllib.request
from urllib.parse import quote
from datetime import datetime
import os
from models import db  
from bson import ObjectId
import math
import itertools
import bcrypt
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart_city_safi_2024'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ========== CONFIGURATION MQTT ==========
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

REGIONS = {
    'nord': {'nom': 'Nord', 'topic_etat': 'dechets/nord/etat', 'topic_commande': 'dechets/nord/commande', 'center': [32.3200, -9.2350], 'couleur': '#3498db'},
    'sud': {'nom': 'Sud', 'topic_etat': 'dechets/sud/etat', 'topic_commande': 'dechets/sud/commande', 'center': [32.2600, -9.2300], 'couleur': '#2ecc71'},
    'est': {'nom': 'Est', 'topic_etat': 'dechets/est/etat', 'topic_commande': 'dechets/est/commande', 'center': [32.2900, -9.1900], 'couleur': '#e67e22'},
    'ouest': {'nom': 'Ouest', 'topic_etat': 'dechets/ouest/etat', 'topic_commande': 'dechets/ouest/commande', 'center': [32.2850, -9.2600], 'couleur': '#9b59b6'}
}

POUBELLES_PAR_REGION = {
    'nord': [
        {"id": 1, "type": "MENAGER", "lat": 32.3188, "lng": -9.2315, "adresse": "Avenue Moulay Youssef, Safi Nord"},
        {"id": 2, "type": "VERRE",   "lat": 32.3160, "lng": -9.2380, "adresse": "Rue Ibn Sina, Safi Nord"},
        {"id": 3, "type": "CARTON",  "lat": 32.3125, "lng": -9.2350, "adresse": "Quartier Industriel, Safi Nord"},
        {"id": 4, "type": "PAPIER",  "lat": 32.3090, "lng": -9.2395, "adresse": "Lotissement Al Amal, Safi Nord"}
    ],
    'sud': [
        {"id": 5, "type": "MENAGER", "lat": 32.2685, "lng": -9.2305, "adresse": "Bab Marrakech, Safi Sud"},
        {"id": 6, "type": "VERRE",   "lat": 32.2650, "lng": -9.2345, "adresse": "Avenue Hassan II, Safi Sud"},
        {"id": 7, "type": "CARTON",  "lat": 32.2615, "lng": -9.2280, "adresse": "Quartier Salam, Safi Sud"},
        {"id": 8, "type": "PAPIER",  "lat": 32.2590, "lng": -9.2325, "adresse": "Cité Ouvrière, Safi Sud"}
    ],
    'est': [
        {"id": 9,  "type": "MENAGER", "lat": 32.2925, "lng": -9.1895, "adresse": "Zone Jorf Lasfar, Safi Est"},
        {"id": 10, "type": "VERRE",   "lat": 32.2890, "lng": -9.1940, "adresse": "Route d'Essaouira, Safi Est"},
        {"id": 11, "type": "CARTON",  "lat": 32.2855, "lng": -9.1885, "adresse": "Hay El Massira, Safi Est"},
        {"id": 12, "type": "PAPIER",  "lat": 32.2910, "lng": -9.1860, "adresse": "Bd des FAR, Safi Est"}
    ],
    'ouest': [
        {"id": 13, "type": "MENAGER", "lat": 32.2838, "lng": -9.2455, "adresse": "Boulevard Al Maghrib Al Arabi, Safi Ouest"},
        {"id": 14, "type": "VERRE",   "lat": 32.2813, "lng": -9.2440, "adresse": "Rue Mohammed V, Safi Ouest"},
        {"id": 15, "type": "CARTON",  "lat": 32.2792, "lng": -9.2480, "adresse": "Avenue des Nations Unies, Safi Ouest"},
        {"id": 16, "type": "PAPIER",  "lat": 32.2767, "lng": -9.2445, "adresse": "Rue Yougoslavie, Safi Ouest"}
    ]
}

toutes_les_poubelles = []
for region_key, poubelles in POUBELLES_PAR_REGION.items():
    for p in poubelles:
        toutes_les_poubelles.append({
            **p,
            'region': region_key,
            'niveau': 0,
            'odeur': 0,
            'urgence': False,
            'attention': False,
            'last_update': None
        })

data_store = {
    'dechets': {
        'poubelles': toutes_les_poubelles,
        'par_region': {region: [] for region in REGIONS.keys()},
        'derniere_maj': None,
        'statistiques': {'total': 0, 'urgences': 0, 'attention': 0}
    },
    'eau': {
        'pH': 7.0,
        'turbidite': 0,
        'conductivite': 0,
        'qualite': 0,
        'qualite_texte': 'POTABLE',
        'icone': '🟢',
        'problemes': [],
        'timestamp': None
    },
    'air': {
        'pm25': 0, 'pm10': 0, 'o3': 0, 'no2': 0, 'so2': 0, 'co': 0,
        'qualite': 0, 'qualite_texte': 'BON',
        'timestamp': None,
        'historique': []
    },
    'agriculture': {
        'temperature': 0,
        'humidite_air': 0,
        'humidite_sol': 0,
        'led_state': 'green',
        'timestamp': None
    },
    'eclairage': {
        'A': {
            'nuit': False,
            'led1': 0,
            'led2': 0,
            'led3': 0,
            'led4': 0,
            'allumees': 0,
            'panne': {'active': False, 'niveau': 0, 'led_grillee': -1},
            'intensite_manuelle': 0,
            'timestamp': None,
            'historique': []
        },
        'B': {
            'nuit': False,
            'led1': 0,
            'led2': 0,
            'led3': 0,
            'led4': 0,
            'allumees': 0,
            'timestamp': None,
            'historique': []
        }
    }
}

# ========== FONCTIONS ==========
def evaluer_qualite_eau():
    pH = data_store['eau']['pH']
    turb = data_store['eau']['turbidite']
    cond = data_store['eau']['conductivite']
    danger = False
    attention = False
    problemes = []
    if pH < 5.5 or pH > 9.5:
        danger = True
        problemes.append(f"⚠️ pH {pH} - HORS NORME! (normal: 6.5-8.5)")
    elif pH < 6.5 or pH > 8.5:
        attention = True
        problemes.append(f"⚠️ pH {pH} - Légèrement hors norme (normal: 6.5-8.5)")
    if turb > 5:
        danger = True
        problemes.append(f"⚠️ Turbidité {turb} NTU - TRÈS ÉLEVÉE (normale: <1)")
    elif turb > 1:
        attention = True
        problemes.append(f"⚠️ Turbidité {turb} NTU - ÉLEVÉE (normale: <1)")
    if cond > 1000:
        danger = True
        problemes.append(f"⚠️ Conductivité {cond} µS/cm - TRÈS ÉLEVÉE (normale: <400)")
    elif cond > 600:
        attention = True
        problemes.append(f"⚠️ Conductivité {cond} µS/cm - ÉLEVÉE (normale: <400)")
    if danger:
        data_store['eau']['qualite'] = 2
        data_store['eau']['qualite_texte'] = "DANGER"
        data_store['eau']['icone'] = "🔴"
    elif attention:
        data_store['eau']['qualite'] = 1
        data_store['eau']['qualite_texte'] = "ATTENTION"
        data_store['eau']['icone'] = "🟡"
    else:
        data_store['eau']['qualite'] = 0
        data_store['eau']['qualite_texte'] = "POTABLE"
        data_store['eau']['icone'] = "🟢"
    data_store['eau']['problemes'] = problemes
    data_store['eau']['timestamp'] = datetime.now().strftime('%H:%M:%S')

def osrm_distance_matrix(points):
    coords = ';'.join(f"{p['lng']},{p['lat']}" for p in points)
    url = f"https://router.project-osrm.org/table/v1/driving/{coords}?annotations=distance"
    with urllib.request.urlopen(url, timeout=20) as response:
        data = json.loads(response.read().decode())
    if data.get("code") != "Ok":
        raise ValueError("Erreur matrice OSRM")
    return data["distances"]

def osrm_route_geometry(points):
    coords = ';'.join(f"{p['lng']},{p['lat']}" for p in points)
    url = f"https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson&steps=true"
    with urllib.request.urlopen(url, timeout=20) as response:
        data = json.loads(response.read().decode())
    if data.get("code") != "Ok":
        raise ValueError("Erreur route OSRM")
    route = data["routes"][0]
    return {
        "geometry": route["geometry"],
        "distance_km": round(route["distance"] / 1000, 2),
        "duration_min": round(route["duration"] / 60, 2)
    }

def tsp_nearest_neighbor(dist):
    n = len(dist)
    visited = [False] * n
    route = [0]
    visited[0] = True
    current = 0
    for _ in range(n - 1):
        nearest = None
        min_dist = float('inf')
        for j in range(1, n):
            if not visited[j] and dist[current][j] < min_dist:
                min_dist = dist[current][j]
                nearest = j
        if nearest is not None:
            route.append(nearest)
            visited[nearest] = True
            current = nearest
    return route

def trouver_plus_court_chemin(dist, points):
    n = len(dist)
    indices = list(range(1, n))
    meilleurs = None
    distance_min = float('inf')
    for perm in itertools.permutations(indices):
        route = [0] + list(perm)
        total = 0
        for i in range(len(route) - 1):
            total += dist[route[i]][route[i+1]]
        distance_km = round(total / 1000, 2)
        noms = ["D"] + [points[i]["type"] for i in perm]
        chemin_str = " → ".join(noms)
        print(f"{chemin_str} = {distance_km} km")
        if total < distance_min:
            distance_min = total
            meilleurs = route
    print("✅ Meilleur chemin trouvé !")
    return meilleurs, round(distance_min / 1000, 2)

# ========== MQTT ==========
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"✅ MQTT connecté (code: {rc})")
    topics = [
        "dechets/nord/etat", "dechets/sud/etat", "dechets/est/etat", "dechets/ouest/etat",
        "air/qualite", "air/pm25", "air/pm10", "air/o3", "air/no2", "air/so2", "air/co",
        "eau/ph", "eau/turbidite", "eau/conductivite",
        "esp32/agri/data",
        "ville/quartierA/lampadaire/1/etat", "ville/quartierA/lampadaire/1/evenement",
        "ville/quartierB/lampadaire/1/etat", "ville/quartierB/lampadaire/1/evenement"
    ]
    for topic in topics:
        client.subscribe(topic)
        print(f"📡 Abonné à: {topic}")

def afficher_commande_eclairage(quartier, action):
    if action == "GAUCHE":
        print(f"💡 [{quartier}] Allumage progressif GAUCHE → DROITE (← →)")
    elif action == "DROITE":
        print(f"💡 [{quartier}] Allumage progressif DROITE → GAUCHE (→ ←)")
    elif action == "ALLUMER_TOUT":
        print(f"🔆 [{quartier}] Allumage de TOUTES les LEDs")
    elif action == "ETEINDRE_TOUT":
        print(f"⬛ [{quartier}] Extinction de TOUTES les LEDs")
    else:
        print(f"🎛️ [{quartier}] Commande reçue : {action}")

def afficher_panne(quartier, panne):
    if not panne.get('active', False):
        print(f"✅ [{quartier}] Panne résolue")
    else:
        niveau = panne.get('niveau', 0)
        led = panne.get('led_grillee', -1)
        if niveau == 1:
            print(f"⚠️ [{quartier}] Panne LÉGÈRE (intensité réduite)")
        elif niveau == 2:
            print(f"🔴 [{quartier}] Panne MOYENNE - LED{led+1} grillée !")
        elif niveau == 3:
            print(f"💀 [{quartier}] Panne GRAVE")

def afficher_etat_eclairage(quartier, data):
    mode = "🌙 NUIT" if data.get('nuit') else "☀️ JOUR"
    leds = f"LED1={data.get('led1',0)} LED2={data.get('led2',0)} LED3={data.get('led3',0)} LED4={data.get('led4',0)}"
    print(f"🏙️ [{quartier}] {mode} | {leds}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    if topic in ["dechets/nord/etat", "dechets/sud/etat", "dechets/est/etat", "dechets/ouest/etat"]:
        try:
            region = topic.split('/')[1]
            if payload.startswith('[') and payload.endswith(']'):
                contenu = payload[1:-1]
                valeurs = contenu.split(',') if contenu else []
                poubelles_region = [p for p in data_store['dechets']['poubelles'] if p['region'] == region]
                for i, poubelle in enumerate(poubelles_region):
                    niveau = int(valeurs[i*2]) if len(valeurs) > i*2 else 0
                    odeur = int(valeurs[i*2+1]) if len(valeurs) > i*2+1 else 0
                    poubelle['niveau'] = niveau
                    poubelle['odeur'] = odeur
                    poubelle['urgence'] = niveau > 80
                    poubelle['attention'] = 60 <= niveau <= 80
                    poubelle['last_update'] = datetime.now().strftime('%H:%M:%S')
                toutes = data_store['dechets']['poubelles']
                data_store['dechets']['statistiques'] = {
                    'total': len(toutes),
                    'urgences': sum(1 for p in toutes if p['niveau'] > 80),
                    'attention': sum(1 for p in toutes if 60 <= p['niveau'] <= 80)
                }
                data_store['dechets']['derniere_maj'] = datetime.now().strftime('%H:%M:%S')
                for r in REGIONS.keys():
                    data_store['dechets']['par_region'][r] = [p for p in toutes if p['region'] == r]
                socketio.emit('dechets_update', data_store['dechets'])
                print(f"🗑️ {REGIONS[region]['nom']} mis à jour - Urgences: {data_store['dechets']['statistiques']['urgences']}")
        except Exception as e:
            print(f"❌ Erreur déchets région {region}: {e}")
    
    elif topic in ["air/qualite", "air/pm25", "air/pm10", "air/o3", "air/no2", "air/so2", "air/co"]:
        try:
            if topic == "air/qualite":
                data = json.loads(payload)
                data_store['air'].update(data)
                data_store['air']['timestamp'] = datetime.now().strftime('%H:%M:%S')
                socketio.emit('air_update', data_store['air'])
                print(f"🌬️ Air: PM2.5={data.get('pm25')} | {data.get('qualite_texte')}")
            else:
                val = float(payload) if '.' in payload else int(payload)
                key = topic.split('/')[-1]
                data_store['air'][key] = val
        except Exception as e:
            print(f"❌ Erreur air: {e}")
    
    elif topic in ["eau/ph", "eau/turbidite", "eau/conductivite"]:
        try:
            key_raw = topic.split('/')[-1]
            key = 'pH' if key_raw == 'ph' else key_raw
            value = float(payload)
            data_store['eau'][key] = value
            evaluer_qualite_eau()
            socketio.emit('eau_update', data_store['eau'])
            print(f"💧 Eau: {key}={value} | {data_store['eau']['qualite_texte']}")
        except Exception as e:
            print(f"❌ Erreur eau: {e}")
    
    elif topic == "esp32/agri/data":
        try:
            data = json.loads(payload)
            data_store['agriculture'] = {
                'temperature': data.get('temperature', 0),
                'humidite_air': data.get('humidity', 0),
                'humidite_sol': data.get('soil_pct', 0),
                'led_state': data.get('led_state', 'green'),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            socketio.emit('agriculture_update', data_store['agriculture'])
            print(f"🌱 Agriculture: {data_store['agriculture']['temperature']}°C | Sol: {data_store['agriculture']['humidite_sol']}%")
        except Exception as e:
            print(f"❌ Erreur agriculture: {e}")
    
    elif topic == "ville/quartierA/lampadaire/1/etat":
        try:
            data = json.loads(payload)
            data_store['eclairage']['A'].update({
                'nuit': data.get('nuit', False),
                'led1': data.get('led1', 0),
                'led2': data.get('led2', 0),
                'led3': data.get('led3', 0),
                'led4': data.get('led4', 0),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            allumees = sum(1 for k in ['led1','led2','led3','led4'] if data.get(k,0) >= 200)
            data_store['eclairage']['A']['allumees'] = allumees
            afficher_etat_eclairage('A', data_store['eclairage']['A'])
            socketio.emit('maj_etat_A', data_store['eclairage']['A'])
        except Exception as e:
            print(f"❌ Erreur état quartier A: {e}")
    
    elif topic == "ville/quartierA/lampadaire/1/evenement":
        try:
            data = json.loads(payload)
            action = data.get('action', '')
            if "PANNE" in action:
                panne = data_store['eclairage']['A']['panne']
                if "LÉGÈRE" in action:
                    panne.update({'active': True, 'niveau': 1, 'led_grillee': -1})
                elif "MOYENNE" in action:
                    match = re.search(r'LED(\d+)', action)
                    led = int(match.group(1)) if match else -1
                    panne.update({'active': True, 'niveau': 2, 'led_grillee': led})
                elif "GRAVE" in action:
                    panne.update({'active': True, 'niveau': 3, 'led_grillee': -1})
                elif "Aucune" in action:
                    panne.update({'active': False, 'niveau': 0, 'led_grillee': -1})
                afficher_panne('A', panne)
            else:
                if action in ["GAUCHE", "DROITE", "ALLUMER_TOUT", "ETEINDRE_TOUT"]:
                    afficher_commande_eclairage('A', action)
                else:
                    print(f"🎬 [A] Événement: {action}")
            historique = data_store['eclairage']['A']['historique']
            historique.insert(0, {
                'time': datetime.now().strftime('%H:%M:%S'),
                'action': action,
                'nuit': data_store['eclairage']['A']['nuit']
            })
            if len(historique) > 20:
                historique.pop()
            socketio.emit('maj_evenement_A', {'action': action, 'time': datetime.now().strftime('%H:%M:%S')})
        except Exception as e:
            print(f"❌ Erreur événement quartier A: {e}")
    
    elif topic == "ville/quartierB/lampadaire/1/etat":
        try:
            data = json.loads(payload)
            data_store['eclairage']['B'].update({
                'nuit': data.get('nuit', False),
                'led1': data.get('led1', 0),
                'led2': data.get('led2', 0),
                'led3': data.get('led3', 0),
                'led4': data.get('led4', 0),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            allumees = sum(1 for k in ['led1','led2','led3','led4'] if data.get(k,0) >= 200)
            data_store['eclairage']['B']['allumees'] = allumees
            afficher_etat_eclairage('B', data_store['eclairage']['B'])
            socketio.emit('maj_etat_B', data_store['eclairage']['B'])
        except Exception as e:
            print(f"❌ Erreur état quartier B: {e}")
    
    elif topic == "ville/quartierB/lampadaire/1/evenement":
        try:
            data = json.loads(payload)
            action = data.get('action', '')
            if action in ["GAUCHE", "DROITE", "ALLUMER_TOUT", "ETEINDRE_TOUT"]:
                afficher_commande_eclairage('B', action)
            else:
                print(f"🎬 [B] Événement: {action}")
            historique = data_store['eclairage']['B']['historique']
            historique.insert(0, {
                'time': datetime.now().strftime('%H:%M:%S'),
                'action': action,
                'nuit': data_store['eclairage']['B']['nuit']
            })
            if len(historique) > 20:
                historique.pop()
            socketio.emit('maj_evenement_B', {'action': action, 'time': datetime.now().strftime('%H:%M:%S')})
        except Exception as e:
            print(f"❌ Erreur événement quartier B: {e}")

# Client MQTT
try:
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    print("📡 Utilisation de paho-mqtt version 2.0+")
except AttributeError:
    mqtt_client = mqtt.Client()
    print("📡 Utilisation de paho-mqtt version < 2.0")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def run_mqtt():
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"❌ Erreur connexion MQTT: {e}")

# ========== ROUTES FLASK ==========
@app.route('/api/me')
def api_me():
    if not session.get('user'):
        return jsonify({'error': 'Non authentifié'}), 401
    return jsonify({
        'username': session.get('user'),
        'role': session.get('role'),
        'nom': session.get('nom', ''),
        'email': session.get('email', ''),
        'regions': session.get('regions', [])
    })

@app.route('/api/driver/regions')
def driver_regions():
    if not session.get('user') or session.get('role') != 'chauffeur':
        return jsonify({'error': 'Accès réservé aux chauffeurs'}), 403
    return jsonify({'regions': session.get('regions', [])})

@app.route('/api/panne/<quartier>')
def get_panne(quartier):
    if quartier not in ['A', 'B']:
        return jsonify({'error': 'Quartier invalide'}), 400
    if quartier == 'A':
        panne = data_store['eclairage']['A'].get('panne', {})
    else:
        panne = {'active': False}
    return jsonify(panne)

@app.route('/api/optimiser_trajet', methods=['POST'])
def optimiser_trajet():
    try:
        data = request.get_json() or {}
        seuil = data.get("seuil", 80)
        regions_filtre = data.get("regions", [])
        if isinstance(regions_filtre, str):
            regions_filtre = [regions_filtre] if regions_filtre != "all" else []
        
        poubelles = []
        for p in data_store["dechets"]["poubelles"]:
            if p["niveau"] > seuil:
                if not regions_filtre or p.get("region") in regions_filtre:
                    poubelles.append(p)
        
        if not poubelles:
            return jsonify({"status": "empty", "message": "Aucune poubelle urgente dans vos zones"})
        
        depot = {"id": 0, "type": "Dépôt", "lat": 32.2833, "lng": -9.2333}
        all_points = [depot] + poubelles
        distances = osrm_distance_matrix(all_points)
        route_indices = tsp_nearest_neighbor(distances)
        ordered_points = [all_points[i] for i in route_indices]
        route_info = osrm_route_geometry(ordered_points)
        
        return jsonify({
            "status": "ok",
            "poubelles": ordered_points[1:],
            "distance_km": route_info["distance_km"],
            "duration_min": route_info["duration_min"],
            "geometry": route_info["geometry"]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/eclairage/commande/<quartier>/<action>', methods=['POST'])
def commander_eclairage(quartier, action):
    if quartier not in ['A', 'B']:
        return jsonify({'status': 'error', 'message': 'Quartier invalide'}), 400
    topic_cmd = f"ville/quartier{quartier}/lampadaire/1/commande"
    mqtt_client.publish(topic_cmd, action)
    afficher_commande_eclairage(quartier, action)
    return jsonify({'status': 'ok', 'message': f'Commande {action} envoyée au quartier {quartier}'})

@app.route('/api/eclairage')
def api_eclairage():
    return jsonify(data_store['eclairage'])

@app.route('/optimisation')
def optimisation_page():
    return render_template('optimisation.html')

@app.route('/')
def acceuil():
    return render_template('acceuil.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return render_template('login.html', error="Tous les champs sont requis")

        user = db.authenticate_user(username, password, role=None)
        if not user:
            print(f"Échec login: username={username!r}")
            return render_template('login.html', error="Nom d'utilisateur ou mot de passe invalide")

        session['user'] = user['username']
        session['role'] = user['role']
        session['user_id'] = user['id']
        session['nom'] = user.get('nom', '')
        session['email'] = user.get('email', '')
        session['regions'] = user.get('regions', [])

        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user['role'] == 'chauffeur':
            return redirect(url_for('chauffeur_dashboard'))
        else:
            return redirect(url_for('acceuil'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('user') or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html', data=data_store)

# UNE SEULE FOIS : la route /chauffeur avec injection des régions
@app.route('/chauffeur')
def chauffeur_dashboard():
    if not session.get('user') or session.get('role') != 'chauffeur':
        return redirect(url_for('login'))
    return render_template('chauffeur_dashboard.html',
                           poubelles=data_store['dechets']['poubelles'],
                           regions=session.get('regions', []),
                           username=session.get('user'),
                           nom=session.get('nom', ''))

@app.route('/api/dechets')
def api_dechets():
    if session.get('role') == 'chauffeur':
        regions = session.get('regions', []) or []
        if regions:
            filtered_poubelles = [p for p in data_store['dechets']['poubelles'] if p.get('region') in regions]
            filtered = {**data_store['dechets']}
            filtered['poubelles'] = filtered_poubelles
            return jsonify(filtered)
    return jsonify(data_store['dechets'])

@app.route('/api/eau')
def api_eau():
    return jsonify(data_store['eau'])

@app.route('/api/air')
def api_air():
    return jsonify(data_store['air'])

@app.route('/api/agriculture')
def api_agriculture():
    return jsonify(data_store['agriculture'])

@app.route('/api/all')
def api_all():
    return jsonify(data_store)


@app.route('/api/commande/vider', methods=['POST'])
def vider_poubelles_selector():
    if session.get('role') != 'chauffeur':
        return jsonify({'status': 'error', 'message': 'Accès refusé. Seul un chauffeur peut lancer une collecte.'}), 403

    data = request.get_json() or {}
    requested_regions = data.get('regions')
    chauffeur_regions = session.get('regions', []) or []

    if requested_regions:
        regions_a_vider = [r for r in requested_regions if r in chauffeur_regions or not chauffeur_regions]
    else:
        regions_a_vider = list(chauffeur_regions) if chauffeur_regions else list(REGIONS.keys())

    if not regions_a_vider:
        return jsonify({'status': 'error', 'message': 'Aucune région assignée pour ce chauffeur.'}), 400

    for r in regions_a_vider:
        if r not in REGIONS:
            return jsonify({'status': 'error', 'message': f'Région inconnue : {r}'}), 400

    # 1. Envoyer la commande MQTT (pour les vrais capteurs)
    for region in regions_a_vider:
        mqtt_client.publish(REGIONS[region]['topic_commande'], "VIDER")

    # 2. Ne vider que les poubelles URGENTES (niveau >= 80) dans les régions concernées
    toutes = data_store['dechets']['poubelles']
    nb_urgentes_avant = sum(1 for p in toutes if p['region'] in regions_a_vider and p['niveau'] >= 80)
    nb_videes = 0
    for poubelle in toutes:
        if poubelle['region'] in regions_a_vider and poubelle['niveau'] >= 80:
            poubelle['niveau'] = 0
            poubelle['odeur'] = max(0, poubelle['odeur'] - 30)
            poubelle['urgence'] = False
            poubelle['attention'] = False
            nb_videes += 1

    # 3. Recalculer les statistiques globales
    data_store['dechets']['statistiques'] = {
        'total': len(toutes),
        'urgences': sum(1 for p in toutes if p['niveau'] >= 80),
        'attention': sum(1 for p in toutes if 60 <= p['niveau'] < 80)
    }
    data_store['dechets']['derniere_maj'] = datetime.now().strftime('%H:%M:%S')

    # 4. Émettre l’événement pour rafraîchir tous les clients
    socketio.emit('dechets_update', data_store['dechets'])

    # 5. Enregistrement dans l’historique (optionnel)
    try:
        db.ajouter_vidange(
            ",".join(regions_a_vider),
            data.get('camionType', 'moyen'),
            nb_videes,
            nb_urgentes_avant
        )
    except Exception as e:
        print(f"Erreur enregistrement historique: {e}")

    return jsonify({
        'status': 'ok',
        'message': f'🚛 Collecte des urgences lancée pour les régions : {", ".join(regions_a_vider)}'
    })
@app.route('/api/led/<service>/<couleur>/<action>')
def control_led(service, couleur, action):
    cmd = ""
    if service == 'air':
        cmd = f"{couleur.upper()}_{'ON' if action == 'on' else 'OFF'}"
        mqtt_client.publish("air/led/commande", cmd)
    elif service == 'eau':
        cmd = f"{couleur.upper()}_{'ON' if action == 'on' else 'OFF'}"
        mqtt_client.publish("eau/led/commande", cmd)
    return jsonify({'status': 'ok', 'commande': cmd})

@app.route('/dechets')
def dechets():
    return render_template('dechets.html')

@app.route('/dechets_multiregions')
def dechets_multiregions():
    return render_template('dechets_multiregions.html')

# ========== GESTION CHAUFFEURS ==========
@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.json or {}
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Nom d\'utilisateur et mot de passe requis'}), 400

        user = db.authenticate_user(username, password)
        if not user:
            return jsonify({'status': 'error', 'message': 'Identifiants incorrects'}), 401

        session['user'] = user['username']
        session['role'] = user['role']
        session['user_id'] = user['id']
        session['nom'] = user.get('nom', '')
        session['email'] = user.get('email', '')
        session['regions'] = user.get('regions', [])

        return jsonify({'status': 'ok', 'user': user})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/users')
def get_users():
    if not session.get('user') or session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Accès refusé'}), 403
    users = db.get_all_users()
    for user in users:
        user['_id'] = str(user['_id'])
        if 'regions' not in user:
            user['regions'] = []
    return jsonify(users)

@app.route('/api/chauffeurs')
def get_chauffeurs():
    try:
        chauffeurs = db.get_users_by_role('chauffeur')
        for chauffeur in chauffeurs:
            chauffeur['_id'] = str(chauffeur['_id'])
            if 'regions' not in chauffeur:
                chauffeur['regions'] = []
        return jsonify(chauffeurs)
    except Exception as e:
        print(f"Erreur GET chauffeurs: {e}")
        return jsonify([])

@app.route('/api/chauffeurs', methods=['POST'])
def add_chauffeur():
    if not session.get('user') or session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Accès refusé'}), 403

    try:
        data = request.json or {}
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'chauffeur')
        nom = data.get('nom', username)
        email = data.get('email', '')
        telephone = data.get('telephone', '')
        regions = data.get('regions', [])

        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Nom d\'utilisateur et mot de passe requis'}), 400

        if role not in ['admin', 'chauffeur']:
            return jsonify({'status': 'error', 'message': 'Rôle invalide'}), 400

        user_id, message = db.create_user(
            username=username,
            password=password,
            role=role,
            nom=nom,
            email=email,
            telephone=telephone,
            regions=regions
        )
        if user_id:
            db.add_historique('users', 'create', f"Ajout de l'utilisateur {username} (role: {role}, régions: {regions})", session.get('user'))
            return jsonify({'status': 'ok', 'message': 'Utilisateur ajouté avec succès', 'user_id': user_id})
        else:
            return jsonify({'status': 'error', 'message': message}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/chauffeurs/<username>', methods=['PUT'])
def update_chauffeur(username):
    try:
        data = request.json
        user = db.get_user_by_username(username)
        if not user:
            return jsonify({'status': 'error', 'message': 'Chauffeur non trouvé'}), 404
        
        update_data = {}
        if data.get('email'):
            update_data['email'] = data['email']
        if data.get('telephone'):
            update_data['telephone'] = data['telephone']
        if data.get('regions') is not None:
            update_data['regions'] = data['regions']
        if data.get('password') and len(data['password']) > 0:
            update_data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        if update_data:
            db.update_user(user['_id'], update_data)
        
        db.add_historique('users', 'update', f"Modification du chauffeur {username}", session.get('user'))
        return jsonify({'status': 'ok', 'message': 'Chauffeur modifié'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/profile', methods=['PUT'])
def update_admin_profile():
    try:
        data = request.json
        email = data.get('email')
        telephone = data.get('telephone')
        new_password = data.get('password')
        admin = db.get_user_by_username('admin')
        if not admin:
            return jsonify({'status': 'error', 'message': 'Admin non trouvé'}), 404
        update_data = {}
        if email:
            update_data['email'] = email
        if telephone:
            update_data['telephone'] = telephone
        if new_password and len(new_password) > 0:
            update_data['password'] = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        if update_data:
            db.update_user(admin['_id'], update_data)
        if session.get('user'):
            db.add_historique('profile', 'update', "Mise à jour du profil admin", session.get('user'))
        return jsonify({'status': 'ok', 'message': 'Profil mis à jour avec succès'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stats/global')
def get_global_stats():
    try:
        total_chauffeurs = len(db.get_users_by_role('chauffeur'))
        total_alertes = db.alertes.count_documents({'lu': False})
        return jsonify({
            'total_chauffeurs': total_chauffeurs,
            'total_alertes': total_alertes,
            'alertes_urgentes': db.alertes.count_documents({'type': 'urgent', 'lu': False})
        })
    except:
        return jsonify({'total_chauffeurs': 0, 'total_alertes': 0, 'alertes_urgentes': 0})

@app.route('/api/historique/vidange', methods=['POST'])
def ajouter_historique_vidange():
    try:
        data = request.json
        region = data.get('region')
        camionType = data.get('camionType')
        nbPoubellesVidees = data.get('nbPoubellesVidees')
        nbUrgentes = data.get('nbUrgentes')
        db.ajouter_vidange(region, camionType, nbPoubellesVidees, nbUrgentes)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/historique/vidange', methods=['GET'])
def get_historique_vidange():
    region = request.args.get('region')
    vidanges = db.get_vidanges(region=region, limit=50)
    for v in vidanges:
        v['_id'] = str(v['_id'])
        v['date'] = v['date'].strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(vidanges)

@app.route('/api/dernier_camion')
def dernier_camion():
    try:
        dernier = db.get_vidanges(limit=1)
        if dernier and len(dernier) > 0:
            camion_type = dernier[0].get('camionType', 'moyen')
        else:
            camion_type = 'moyen'
        return jsonify({'camionType': camion_type})
    except Exception as e:
        return jsonify({'camionType': 'moyen', 'error': str(e)}), 500

# ========== DÉMARRAGE ==========
if __name__ == '__main__':
    mqtt_thread = threading.Thread(target=run_mqtt, daemon=True)
    mqtt_thread.start()
    print("=" * 60)
    print("🏙️ SMART CITY SAFI - PLATEFORME UNIFIÉE (4 RÉGIONS + ÉCLAIRAGE + PANNES)")
    print("=" * 60)
    print("📡 Serveur: http://localhost:5000")
    print("🔐 Accès: admin/admin123 | chauffeur/chauffeur123")
    print("💡 Commandes éclairage : GAUCHE (← →) | DROITE (→ ←) | ALLUMER_TOUT | ETEINDRE_TOUT")
    print("=" * 60)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)