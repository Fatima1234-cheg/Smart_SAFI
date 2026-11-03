from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# Stockage des lampadaires
lampadaires = {}
historique = []
alertes = []

# Configuration MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
TOPICS = [
    "ville/lampadaire/+/etat",
    "ville/lampadaire/+/heartbeat",
    "ville/lampadaire/+/evenement"
]

# Callback MQTT
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)
        topic = msg.topic
        print(f"📥 {topic}: {data}")
        
        parts = topic.split('/')
        if len(parts) >= 3:
            lamp_id = parts[2]
            
            if lamp_id not in lampadaires:
                lampadaires[lamp_id] = {"id": lamp_id, "dernier_contact": time.time()}
            
            lampadaires[lamp_id]["dernier_contact"] = time.time()
            lampadaires[lamp_id]["led1"] = data.get("led1", 0)
            lampadaires[lamp_id]["led2"] = data.get("led2", 0)
            lampadaires[lamp_id]["led3"] = data.get("led3", 0)
            lampadaires[lamp_id]["led4"] = data.get("led4", 0)
            
            if "action" in data:
                historique.append({
                    "heure": datetime.now().strftime("%H:%M:%S"),
                    "lampadaire": lamp_id,
                    "action": data["action"]
                })
                if len(historique) > 50:
                    historique.pop(0)
            
            if "status" in data and data["status"] == "OK":
                lampadaires[lamp_id]["statut"] = "OK"
                
    except Exception as e:
        print(f"❌ Erreur MQTT: {e}")

# Vérification des pannes
def verifier_pannes():
    while True:
        now = time.time()
        for lamp_id, data in lampadaires.items():
            dernier = data.get("dernier_contact", 0)
            if now - dernier > 30:
                if data.get("statut") != "PANNE":
                    data["statut"] = "PANNE"
                    alertes.append({
                        "heure": datetime.now().strftime("%H:%M:%S"),
                        "lampadaire": lamp_id,
                        "type": "HORS LIGNE"
                    })
                    print(f"⚠️ PANNE détectée: Lampadaire {lamp_id}")
        time.sleep(5)

# Démarrer MQTT
def start_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    for topic in TOPICS:
        client.subscribe(topic)
    client.loop_forever()

mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

panne_thread = threading.Thread(target=verifier_pannes)
panne_thread.daemon = True
panne_thread.start()

@app.route('/')
def index():
    return render_template_string(HTML_PAGE, lampadaires=lampadaires, historique=historique, alertes=alertes)

@app.route('/api/lampadaires')
def get_lampadaires():
    return jsonify(lampadaires)

@app.route('/api/historique')
def get_historique():
    return jsonify(historique)

@app.route('/api/alertes')
def get_alertes():
    return jsonify(alertes)

# ==================== NOUVEAU HTML SIMPLIFIÉ ====================
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Smart City - Éclairage Public</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
            padding: 20px;
        }
        .container { max-width: 800px; margin: auto; }
        h1 { text-align: center; color: #ffd700; }
        
        /* Carte de la ville */
        .carte {
            background: #0f0f2a;
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        /* Mode actuel */
        .mode {
            font-size: 28px;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            font-weight: bold;
        }
        .mode.nuit {
            background: #0a0a3a;
            border: 2px solid #4466ff;
            color: white;
        }
        .mode.jour {
            background: #ffaa00;
            color: #1a1a2e;
            border: 2px solid white;
        }
        
        /* État global des lampadaires */
        .etat-global {
            background: #1a1a3a;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }
        .etat-ok {
            background: #006600;
            padding: 15px;
            border-radius: 10px;
            font-size: 20px;
        }
        .etat-alerte {
            background: #660000;
            padding: 15px;
            border-radius: 10px;
            font-size: 20px;
            animation: clignote 1s infinite;
        }
        @keyframes clignote {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        /* Statistiques simples */
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        .stat {
            background: #2a2a5a;
            padding: 10px 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-valeur {
            font-size: 24px;
            font-weight: bold;
            color: #ffd700;
        }
        
        /* Historique */
        .historique {
            background: #1a1a3a;
            border-radius: 15px;
            padding: 15px;
            margin-top: 20px;
            max-height: 200px;
            overflow-y: auto;
        }
        .event {
            padding: 8px;
            border-bottom: 1px solid #333;
            font-size: 14px;
        }
        .event.alerte { color: #ff6b6b; }
        .event.info { color: #ffd700; }
        
        /* Alertes */
        .alertes {
            background: #1a1a3a;
            border-radius: 15px;
            padding: 15px;
            margin-top: 20px;
        }
        .alerte-item {
            background: rgba(255,0,0,0.2);
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid red;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏙️ SMART CITY - ÉCLAIRAGE PUBLIC 🌃</h1>
        
        <!-- Carte -->
        <div class="carte">
            🗺️ VILLE - QUARTIER CENTRE
        </div>
        
        <!-- Mode Jour/Nuit (calculé automatiquement) -->
        <div class="mode" id="mode">
            🔄 Chargement...
        </div>
        
        <!-- État global des lampadaires -->
        <div class="etat-global">
            <h3>📊 ÉTAT GLOBAL DES LAMPADAIRES</h3>
            <div id="etatGlobal" class="etat-ok">
                ✅ TOUS LES LAMPADAIRES FONCTIONNENT
            </div>
            <div class="stats">
                <div class="stat">
                    <div>💡 Total</div>
                    <div class="stat-valeur" id="total">0</div>
                </div>
                <div class="stat">
                    <div>🟢 Allumés</div>
                    <div class="stat-valeur" id="allumes">0</div>
                </div>
                <div class="stat">
                    <div>🔴 Éteints</div>
                    <div class="stat-valeur" id="eteints">0</div>
                </div>
            </div>
        </div>
        
        <!-- Alertes -->
        <div class="alertes">
            <h3>⚠️ ALERTES</h3>
            <div id="alertesList">
                {% for alerte in alertes|reverse %}
                <div class="alerte-item">
                    🔴 {{ alerte.heure }} - Lampadaire #{{ alerte.lampadaire }} - {{ alerte.type }}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Historique -->
        <div class="historique">
            <h3>📋 HISTORIQUE</h3>
            <div id="historiqueList">
                {% for evt in historique|reverse %}
                <div class="event info">
                    🕐 {{ evt.heure }} - Lampadaire #{{ evt.lampadaire }} - {{ evt.action }}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <p style="text-align: center; font-size: 12px; margin-top: 20px;">Mise à jour automatique toutes les 3 secondes</p>
    </div>
    
    <script>
        function mettreAJour() {
            fetch('/api/lampadaires')
                .then(response => response.json())
                .then(data => {
                    let total = 0;
                    let allumes = 0;
                    let estNuit = true;
                    let alerteNuit = false;
                    
                    // Parcourir tous les lampadaires
                    for(let id in data) {
                        let lamp = data[id];
                        total++;
                        
                        // Vérifier si un lampadaire est allumé (intensité > 0)
                        let estAllume = (lamp.led1 > 0 || lamp.led2 > 0 || lamp.led3 > 0 || lamp.led4 > 0);
                        if(estAllume) allumes++;
                        
                        // Déterminer si c'est la nuit (au moins un lampadaire allumé)
                        if(estAllume) estNuit = true;
                        
                        // Vérifier si en mode nuit mais lampadaire éteint
                        if(estAllume && (lamp.led1 < 50 && lamp.led2 < 50 && lamp.led3 < 50 && lamp.led4 < 50)) {
                            alerteNuit = true;
                        }
                    }
                    
                    let eteints = total - allumes;
                    
                    // Mettre à jour les stats
                    document.getElementById('total').innerHTML = total;
                    document.getElementById('allumes').innerHTML = allumes;
                    document.getElementById('eteints').innerHTML = eteints;
                    
                    // Déterminer le mode (Jour/Nuit)
                    let modeDiv = document.getElementById('mode');
                    let etatGlobalDiv = document.getElementById('etatGlobal');
                    
                    if(allumes === 0) {
                        // MODE JOUR
                        modeDiv.innerHTML = '☀️ MODE JOUR ☀️<br>Tous les lampadaires sont éteints';
                        modeDiv.className = 'mode jour';
                        etatGlobalDiv.innerHTML = '✅ MODE JOUR - Économie d\'énergie';
                        etatGlobalDiv.className = 'etat-ok';
                    } else {
                        // MODE NUIT
                        if(eteints > 0) {
                            modeDiv.innerHTML = '🌙 MODE NUIT 🌙<br>⚠️ ' + eteints + ' lampadaire(s) éteint(s) !';
                            modeDiv.className = 'mode nuit';
                            etatGlobalDiv.innerHTML = '⚠️ ALERTE - ' + eteints + ' lampadaire(s) non fonctionnel(s) !';
                            etatGlobalDiv.className = 'etat-alerte';
                        } else {
                            modeDiv.innerHTML = '🌙 MODE NUIT 🌙<br>Tous les lampadaires sont allumés';
                            modeDiv.className = 'mode nuit';
                            etatGlobalDiv.innerHTML = '✅ TOUS LES LAMPADAIRES FONCTIONNENT';
                            etatGlobalDiv.className = 'etat-ok';
                        }
                    }
                });
            
            // Mettre à jour les alertes et historique
            fetch('/api/alertes')
                .then(response => response.json())
                .then(data => {
                    let alertesDiv = document.getElementById('alertesList');
                    if(data.length > 0) {
                        alertesDiv.innerHTML = data.slice().reverse().slice(0, 5).map(a => 
                            '<div class="alerte-item">🔴 ' + a.heure + ' - Lampadaire #' + a.lampadaire + ' - ' + a.type + '</div>'
                        ).join('');
                    }
                });
            
            fetch('/api/historique')
                .then(response => response.json())
                .then(data => {
                    let historiqueDiv = document.getElementById('historiqueList');
                    if(data.length > 0) {
                        historiqueDiv.innerHTML = data.slice().reverse().slice(0, 10).map(e => 
                            '<div class="event info">🕐 ' + e.heure + ' - Lampadaire #' + e.lampadaire + ' - ' + e.action + '</div>'
                        ).join('');
                    }
                });
        }
        
        setInterval(mettreAJour, 3000);
        mettreAJour();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Serveur Flask démarré sur http://localhost:5000")
    print("📡 Connecté au broker MQTT: broker.emqx.io")
    app.run(host='0.0.0.0', port=5000, debug=True)