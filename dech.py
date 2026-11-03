from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
from datetime import datetime
import threading
import math

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
TOPIC_ETAT = "dechets/region/etat"
TOPIC_COMMANDE = "dechets/region/commande"

# Stockage des données
poubelles_data = []
dernier_rafraichissement = None

# Coordonnées fixes des poubelles à Safi
POUBELLES_FIXES = [
    {"id": 1, "type": "VERRE", "lat": 32.2850, "lng": -9.2350, "adresse": "Boulevard Mohammed V, Centre Ville"},
    {"id": 2, "type": "CARTON", "lat": 32.2900, "lng": -9.2280, "adresse": "Route de Marrakech, Zone Industrielle"},
    {"id": 3, "type": "MENAGER", "lat": 32.2780, "lng": -9.2400, "adresse": "Bab Chaaba, Médina"},
    {"id": 4, "type": "PAPIER", "lat": 32.2800, "lng": -9.2250, "adresse": "Derb Sultan, Quartier Résidentiel"}
]

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"✅ MQTT connecté (code: {rc})")
    client.subscribe(TOPIC_ETAT)

def on_message(client, userdata, msg):
    global poubelles_data, dernier_rafraichissement
    try:
        payload = msg.payload.decode()
        print(f"📨 Reçu: {payload}")
        
        # Format: [niv1,ode1,niv2,ode2,niv3,ode3,niv4,ode4]
        if payload.startswith('[') and payload.endswith(']'):
            contenu = payload[1:-1]
            valeurs = contenu.split(',') if contenu else []
            
            nouvelle_liste = []
            for i in range(4):
                niveau = int(valeurs[i*2]) if len(valeurs) > i*2 else 0
                odeur = int(valeurs[i*2+1]) if len(valeurs) > i*2+1 else 0
                
                nouvelle_liste.append({
                    "id": POUBELLES_FIXES[i]["id"],
                    "type": POUBELLES_FIXES[i]["type"],
                    "niveau": niveau,
                    "odeur": odeur,
                    "urgence": niveau > 80,
                    "lat": POUBELLES_FIXES[i]["lat"],
                    "lng": POUBELLES_FIXES[i]["lng"],
                    "adresse": POUBELLES_FIXES[i]["adresse"]
                })
            
            poubelles_data = nouvelle_liste
            dernier_rafraichissement = datetime.now().strftime('%H:%M:%S')
            
            socketio.emit('maj_donnees', {
                'poubelles': poubelles_data,
                'time': dernier_rafraichissement
            })
            
            print(f"📊 {len(poubelles_data)} poubelles mises à jour")
            for p in poubelles_data:
                print(f"   {p['type']}: {p['niveau']}% | Odeur: {p['odeur']}%")
        else:
            print(f"⚠️ Format non reconnu: {payload}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def run_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_forever()

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/donnees')
def get_donnees():
    return jsonify({
        'poubelles': poubelles_data,
        'time': dernier_rafraichissement
    })

@app.route('/api/commande/vider')
def vider_poubelles():
    mqtt_client.publish(TOPIC_COMMANDE, "VIDER")
    print("🚛 Commande de vidage envoyée")
    return jsonify({'status': 'ok', 'message': 'Camion envoyé'})

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Safi - Gestion Intelligente des Déchets</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial; background: #1a1a2e; color: white; height: 100vh; display: flex; flex-direction: column; }
        .header { background: linear-gradient(135deg, #0f0f23, #1a1a2e); padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; }
        h1 { color: #ffd700; font-size: 1.5em; }
        .subtitle { color: #aaa; font-size: 0.8em; }
        .stats { display: flex; gap: 20px; }
        .stat { text-align: center; padding: 5px 15px; background: rgba(255,255,255,0.1); border-radius: 20px; }
        .stat-value { font-size: 1.2em; font-weight: bold; }
        .stat-label { font-size: 0.7em; color: #aaa; }
        .btn-vider { background: linear-gradient(135deg, #ff4444, #880000); color: white; border: none; padding: 10px 25px; border-radius: 25px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        .btn-vider:hover { transform: scale(1.05); box-shadow: 0 0 15px red; }
        .container { display: flex; flex: 1; overflow: hidden; }
        #map { flex: 3; height: 100%; }
        .sidebar { flex: 1; background: rgba(0,0,0,0.5); padding: 15px; overflow-y: auto; border-left: 1px solid #333; }
        .sidebar-title { margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #333; }
        .poubelle-list { display: flex; flex-direction: column; gap: 10px; }
        .poubelle-item { background: rgba(255,255,255,0.1); border-radius: 10px; padding: 12px; cursor: pointer; transition: 0.2s; border-left: 4px solid; }
        .poubelle-item.urgence { border-left-color: #ff0000; animation: pulse 1s infinite; }
        .poubelle-item.attention { border-left-color: #ffaa00; }
        .poubelle-item.normal { border-left-color: #00ff00; }
        @keyframes pulse { 0% { background: rgba(255,0,0,0.1); } 50% { background: rgba(255,0,0,0.3); } 100% { background: rgba(255,0,0,0.1); } }
        .barre { height: 8px; background: #333; border-radius: 4px; overflow: hidden; margin: 8px 0; }
        .barre-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
        .barre-fill.vert { background: #00ff00; }
        .barre-fill.jaune { background: #ffaa00; }
        .barre-fill.rouge { background: #ff0000; }
        .poubelle-adresse { font-size: 0.7em; color: #888; margin-top: 5px; }
        .timestamp { text-align: center; padding: 10px; font-size: 0.7em; color: #666; background: rgba(0,0,0,0.3); }
        .legende { display: flex; justify-content: space-around; margin-top: 15px; padding-top: 15px; border-top: 1px solid #333; }
        .legende-item { display: flex; align-items: center; gap: 8px; font-size: 0.7em; }
        .legende-couleur { width: 15px; height: 15px; border-radius: 50%; }
        .legende-couleur.vert { background: #00ff00; }
        .legende-couleur.jaune { background: #ffaa00; }
        .legende-couleur.rouge { background: #ff0000; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🗑️ SAFI - GESTION INTELLIGENTE DES DÉCHETS</h1>
            <div class="subtitle">📍 Ville de Safi, Maroc | Localisation en temps réel</div>
        </div>
        <div class="stats">
            <div class="stat"><div class="stat-value" id="statTotal">0</div><div class="stat-label">Poubelles</div></div>
            <div class="stat"><div class="stat-value" id="statUrgence">0</div><div class="stat-label">Urgences</div></div>
            <div class="stat"><div class="stat-value" id="statOdeur">0</div><div class="stat-label">Odeur >70%</div></div>
        </div>
        <button class="btn-vider" onclick="envoyerVidage()">🚛 ENVOYER CAMION</button>
    </div>
    
    <div class="container">
        <div id="map"></div>
        <div class="sidebar">
            <div class="sidebar-title">📋 Liste des poubelles</div>
            <div class="poubelle-list" id="poubelleList"></div>
            <div class="legende">
                <div class="legende-item"><div class="legende-couleur vert"></div><span>Normal (<60%)</span></div>
                <div class="legende-item"><div class="legende-couleur jaune"></div><span>Attention (60-80%)</span></div>
                <div class="legende-item"><div class="legende-couleur rouge"></div><span>Urgence (>80%)</span></div>
            </div>
        </div>
    </div>
    <div class="timestamp" id="timestamp">🕐 En attente des données...</div>

    <script>
        let map;
        let markers = {};
        const socket = io();
        
        function initMap() {
            map = L.map('map').setView([32.2833, -9.2333], 13);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> | Safi, Maroc',
                subdomains: 'abcd',
                maxZoom: 19
            }).addTo(map);
        }
        
        function getIcone(poubelle) {
            let niveau = poubelle.niveau;
            let couleur = '#00ff00';
            let taille = 32;
            let emoji = '🗑️';
            
            if (niveau >= 80) { couleur = '#ff0000'; taille = 44; }
            else if (niveau >= 60) { couleur = '#ffaa00'; taille = 38; }
            
            if (poubelle.type === 'VERRE') emoji = '🥤';
            else if (poubelle.type === 'CARTON') emoji = '📦';
            else if (poubelle.type === 'MENAGER') emoji = '🍌';
            else if (poubelle.type === 'PAPIER') emoji = '📄';
            
            return L.divIcon({
                html: `<div style="background: ${couleur}; width: ${taille}px; height: ${taille}px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; border: 2px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.5);">${emoji}</div>`,
                iconSize: [taille, taille],
                className: 'custom-div-icon'
            });
        }
        
        function updateStats(poubelles) {
            let total = poubelles.length;
            let urgence = poubelles.filter(p => p.niveau >= 80).length;
            let odeur = poubelles.filter(p => p.odeur > 70 && p.niveau < 80).length;
            document.getElementById('statTotal').innerHTML = total;
            document.getElementById('statUrgence').innerHTML = urgence;
            document.getElementById('statOdeur').innerHTML = odeur;
        }
        
        function updateListe(poubelles) {
            const container = document.getElementById('poubelleList');
            container.innerHTML = '';
            
            poubelles.forEach(p => {
                let niveauClass = p.niveau >= 80 ? 'urgence' : (p.niveau >= 60 ? 'attention' : 'normal');
                let couleurBarre = p.niveau >= 80 ? 'rouge' : (p.niveau >= 60 ? 'jaune' : 'vert');
                const item = document.createElement('div');
                item.className = `poubelle-item ${niveauClass}`;
                item.onclick = () => { map.setView([p.lat, p.lng], 15); if (markers[p.id]) markers[p.id].openPopup(); };
                item.innerHTML = `<div class="poubelle-nom"><span>${p.type}</span><span>${p.niveau}%</span></div>
                    <div class="barre"><div class="barre-fill ${couleurBarre}" style="width: ${p.niveau}%"></div></div>
                    <div>👃 Odeur: ${p.odeur}%</div>
                    <div class="poubelle-adresse">📍 ${p.adresse}</div>
                    ${p.niveau >= 80 ? '<div style="color:#ff0000; font-size:0.8em;">🔴 VIDAGE URGENT !</div>' : ''}`;
                container.appendChild(item);
            });
        }
        
        function updateCarte(poubelles) {
            poubelles.forEach(p => {
                if (markers[p.id]) map.removeLayer(markers[p.id]);
                const popupContent = `<div style="min-width: 180px;"><h3>🗑️ ${p.type}</h3><div><strong>${p.adresse}</strong></div>
                    <div style="margin: 10px 0;"><div>📊 Niveau: ${p.niveau}%</div>
                    <div style="background:#333; height:8px; border-radius:4px;"><div style="background:${p.niveau>=80?'#ff0000':(p.niveau>=60?'#ffaa00':'#00ff00')}; width:${p.niveau}%; height:8px; border-radius:4px;"></div></div></div>
                    <div>👃 Odeur: ${p.odeur}%</div>${p.niveau >= 80 ? '<div style="color:#ff0000;">🔴 VIDAGE URGENT !</div>' : ''}</div>`;
                markers[p.id] = L.marker([p.lat, p.lng], { icon: getIcone(p) }).bindPopup(popupContent).addTo(map);
            });
        }
        
        function updateAll(data) {
            if (!data.poubelles) return;
            updateStats(data.poubelles);
            updateListe(data.poubelles);
            updateCarte(data.poubelles);
            document.getElementById('timestamp').innerHTML = `🕐 Dernière mise à jour: ${data.time}`;
        }
        
        function envoyerVidage() { fetch('/api/commande/vider').then(r => r.json()).then(data => alert('🚛 Camion envoyé !')); }
        
        socket.on('maj_donnees', function(data) { updateAll(data); });
        initMap();
        fetch('/api/donnees').then(r => r.json()).then(data => { if (data.poubelles && data.poubelles.length > 0) updateAll(data); });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    mqtt_thread = threading.Thread(target=run_mqtt, daemon=True)
    mqtt_thread.start()
    
    print("🚀 Serveur Flask: http://localhost:5000")
    print("🗺️ Carte de Safi, Maroc - 4 poubelles")
    print("📡 Topic MQTT: " + TOPIC_ETAT)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)