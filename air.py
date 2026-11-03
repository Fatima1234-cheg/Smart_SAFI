from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# ========== Configuration MQTT ==========
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

# Topics MQTT
MQTT_TOPICS = {
    'air': "air/qualite",
    'pm25': "air/pm25",
    'pm10': "air/pm10",
    'o3': "air/o3",
    'no2': "air/no2",
    'so2': "air/so2",
    'co': "air/co",
    'led_status': "air/led/status"
}

# ========== Normes internationales OMS ==========
NORMES_OMS = {
    'pm25': {'valeur': 15, 'unite': 'µg/m³', 'nom': 'PM2.5'},
    'pm10': {'valeur': 45, 'unite': 'µg/m³', 'nom': 'PM10'},
    'o3': {'valeur': 100, 'unite': 'µg/m³', 'nom': 'O3'},
    'no2': {'valeur': 25, 'unite': 'µg/m³', 'nom': 'NO2'},
    'so2': {'valeur': 40, 'unite': 'µg/m³', 'nom': 'SO2'},
    'co': {'valeur': 10, 'unite': 'mg/m³', 'nom': 'CO'}
}

NORMES_UE = {
    'pm25': 25, 'pm10': 50, 'o3': 120, 'no2': 40, 'so2': 125, 'co': 10
}

NORMES_USA = {
    'pm25': 35, 'pm10': 150, 'o3': 140, 'no2': 100, 'so2': 196, 'co': 10
}

# ========== Stockage des données ==========
donnees_air = {
    'pm25': 0, 'pm10': 0, 'o3': 0, 'no2': 0, 'so2': 0, 'co': 0,
    'qualite': 0, 'qualite_texte': 'BON',
    'timestamp': None,
    'historique': []
}

# ========== Callback MQTT ==========
def on_connect(client, userdata, flags, rc):
    print(f"✅ MQTT connecté (code: {rc})")
    for topic in MQTT_TOPICS.values():
        client.subscribe(topic)
        print(f"📡 Abonné à: {topic}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    if topic == MQTT_TOPICS['air']:
        try:
            data = json.loads(payload)
            donnees_air.update(data)
            donnees_air['timestamp'] = datetime.now().strftime('%H:%M:%S')
            
            # Ajout à l'historique
            historique = {
                'pm25': data.get('pm25'),
                'pm10': data.get('pm10'),
                'o3': data.get('o3'),
                'no2': data.get('no2'),
                'so2': data.get('so2'),
                'co': data.get('co'),
                'qualite': data.get('qualite'),
                'qualite_texte': data.get('qualite_texte'),
                'time': donnees_air['timestamp']
            }
            donnees_air['historique'].append(historique)
            if len(donnees_air['historique']) > 30:
                donnees_air['historique'].pop(0)
            
            socketio.emit('new_data', donnees_air)
            print(f"📊 PM2.5:{data.get('pm25')} | Qualité:{data.get('qualite_texte')}")
        except Exception as e:
            print(f"❌ Erreur JSON: {e}")
    
    elif topic == MQTT_TOPICS['led_status']:
        socketio.emit('led_status', {'status': payload})

# ========== Configuration client MQTT ==========
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def run_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_forever()

# ========== Routes Flask ==========
@app.route('/')
def index():
    return render_template_string(HTML_PAGE, normes=NORMES_OMS)

@app.route('/api/donnees')
def get_donnees():
    return jsonify(donnees_air)

@app.route('/api/normes')
def get_normes():
    return jsonify({
        'oms': NORMES_OMS,
        'ue': NORMES_UE,
        'usa': NORMES_USA
    })

@app.route('/api/led/<couleur>/<action>')
def control_led(couleur, action):
    commandes = {
        'rouge': 'ROUGE_ON' if action == 'on' else 'ROUGE_OFF',
        'jaune': 'JAUNE_ON' if action == 'on' else 'JAUNE_OFF',
        'verte': 'VERTE_ON' if action == 'on' else 'VERTE_OFF',
        'all': 'ALL' if action == 'on' else 'OFF'
    }
    cmd = commandes.get(couleur)
    if cmd:
        mqtt_client.publish("air/led/commande", cmd)
        return jsonify({'status': 'ok', 'commande': cmd})
    return jsonify({'error': 'Couleur invalide'}), 400

# ========== HTML Interface ==========
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Qualité de l'Air - Smart City</title>
    <meta http-equiv="refresh" content="3">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
            padding: 20px;
        }
        .container { max-width: 1000px; margin: auto; }
        h1 { text-align: center; color: #ffd700; margin-bottom: 10px; }
        .sous-titre { text-align: center; opacity: 0.8; margin-bottom: 30px; }
        
        /* Indice global */
        .indice-global {
            text-align: center;
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 20px;
        }
        .indice-bon { background: linear-gradient(135deg, #006400, #00aa00); }
        .indice-moyen { background: linear-gradient(135deg, #886600, #ccaa00); }
        .indice-mauvais { background: linear-gradient(135deg, #cc6600, #ff8800); }
        .indice-danger { background: linear-gradient(135deg, #660000, #cc0000); }
        .indice-valeur { font-size: 3em; font-weight: bold; }
        .indice-texte { font-size: 1.5em; margin-top: 10px; }
        
        /* Grille des polluants */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
        }
        .card h3 {
            color: #ffd700;
            margin-bottom: 15px;
            border-left: 3px solid #ffd700;
            padding-left: 10px;
        }
        .valeur {
            font-size: 2.5em;
            font-weight: bold;
        }
        .unite { font-size: 0.8em; opacity: 0.7; }
        .norme {
            margin-top: 10px;
            padding: 8px;
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            font-size: 0.8em;
        }
        .norme-ok { color: #00ff00; }
        .norme-alerte { color: #ffaa00; }
        .norme-danger { color: #ff4444; }
        
        /* Barre de progression */
        .barre-container {
            background: #333;
            border-radius: 10px;
            height: 8px;
            margin: 10px 0;
            overflow: hidden;
        }
        .barre {
            height: 100%;
            transition: width 0.5s;
        }
        .barre-bon { background: #00ff00; }
        .barre-moyen { background: #ffaa00; }
        .barre-mauvais { background: #ff6600; }
        .barre-danger { background: #ff0000; }
        
        /* Contrôle LEDs */
        .led-control {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .btn-led {
            background: #333;
            color: white;
            border: none;
            padding: 10px 15px;
            margin: 5px;
            border-radius: 8px;
            cursor: pointer;
            transition: 0.3s;
        }
        .btn-led:hover { transform: scale(1.05); }
        .btn-rouge { background: #cc0000; }
        .btn-jaune { background: #ccaa00; }
        .btn-vert { background: #00aa00; }
        
        /* Historique */
        .historique {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            max-height: 250px;
            overflow-y: auto;
        }
        .event {
            padding: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            font-size: 0.85em;
        }
        .event-bon { border-left: 3px solid #00ff00; }
        .event-moyen { border-left: 3px solid #ffaa00; }
        .event-mauvais { border-left: 3px solid #ff6600; }
        .event-danger { border-left: 3px solid #ff0000; }
        
        .footer { text-align: center; font-size: 11px; margin-top: 20px; opacity: 0.6; }
    </style>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>🌍 SMART CITY - QUALITÉ DE L'AIR 🌬️</h1>
        <div class="sous-titre">Normes OMS (Organisation Mondiale de la Santé)</div>
        
        <div class="indice-global" id="indiceGlobal">
            <div class="indice-valeur" id="indiceValeur">--</div>
            <div class="indice-texte" id="indiceTexte">Chargement...</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🌫️ PM2.5</h3>
                <div><span class="valeur" id="pm25">--</span><span class="unite"> µg/m³</span></div>
                <div class="barre-container"><div class="barre" id="barrePM25" style="width:0%"></div></div>
                <div class="norme">Norme OMS: <span id="normePM25">15</span> µg/m³</div>
                <div id="statutPM25" class="norme-ok">✅ Conforme</div>
            </div>
            <div class="card">
                <h3>🌫️ PM10</h3>
                <div><span class="valeur" id="pm10">--</span><span class="unite"> µg/m³</span></div>
                <div class="barre-container"><div class="barre" id="barrePM10" style="width:0%"></div></div>
                <div class="norme">Norme OMS: <span id="normePM10">45</span> µg/m³</div>
                <div id="statutPM10" class="norme-ok">✅ Conforme</div>
            </div>
            <div class="card">
                <h3>💨 O3</h3>
                <div><span class="valeur" id="o3">--</span><span class="unite"> µg/m³</span></div>
                <div class="barre-container"><div class="barre" id="barreO3" style="width:0%"></div></div>
                <div class="norme">Norme OMS: <span id="normeO3">100</span> µg/m³</div>
                <div id="statutO3" class="norme-ok">✅ Conforme</div>
            </div>
            <div class="card">
                <h3>🏭 NO2</h3>
                <div><span class="valeur" id="no2">--</span><span class="unite"> µg/m³</span></div>
                <div class="barre-container"><div class="barre" id="barreNO2" style="width:0%"></div></div>
                <div class="norme">Norme OMS: <span id="normeNO2">25</span> µg/m³</div>
                <div id="statutNO2" class="norme-ok">✅ Conforme</div>
            </div>
            <div class="card">
                <h3>🏭 SO2</h3>
                <div><span class="valeur" id="so2">--</span><span class="unite"> µg/m³</span></div>
                <div class="barre-container"><div class="barre" id="barreSO2" style="width:0%"></div></div>
                <div class="norme">Norme OMS: <span id="normeSO2">40</span> µg/m³</div>
                <div id="statutSO2" class="norme-ok">✅ Conforme</div>
            </div>
            <div class="card">
                <h3>🔥 CO</h3>
                <div><span class="valeur" id="co">--</span><span class="unite"> mg/m³</span></div>
                <div class="barre-container"><div class="barre" id="barreCO" style="width:0%"></div></div>
                <div class="norme">Norme OMS: <span id="normeCO">10</span> mg/m³</div>
                <div id="statutCO" class="norme-ok">✅ Conforme</div>
            </div>
        </div>
        
        <div class="led-control">
            <h3>🎮 Contrôle des LEDs d'alerte</h3>
            <button class="btn-led btn-rouge" onclick="led('rouge','on')">🔴 ROUGE ON</button>
            <button class="btn-led" onclick="led('rouge','off')">⚫ ROUGE OFF</button>
            <button class="btn-led btn-jaune" onclick="led('jaune','on')">🟡 JAUNE ON</button>
            <button class="btn-led" onclick="led('jaune','off')">⚫ JAUNE OFF</button>
            <button class="btn-led btn-vert" onclick="led('verte','on')">🟢 VERTE ON</button>
            <button class="btn-led" onclick="led('verte','off')">⚫ VERTE OFF</button>
            <button class="btn-led" onclick="led('all','on')">✨ ALL ON</button>
            <button class="btn-led" onclick="led('all','off')">⬛ ALL OFF</button>
        </div>
        
        <div class="historique">
            <h3>📋 Historique des mesures</h3>
            <div id="historiqueList"></div>
        </div>
        
        <div class="footer">Mise à jour automatique toutes les 3 secondes | Référence: OMS 2021</div>
    </div>
    
    <script>
        const socket = io();
        const normes = {{ normes|tojson }};
        
        socket.on('new_data', function(data) {
            // Mise à jour indice global
            let qualite = data.qualite || 0;
            let qualiteTexte = data.qualite_texte || 'BON';
            let classe = 'indice-bon';
            if(qualite == 1) classe = 'indice-moyen';
            else if(qualite == 2) classe = 'indice-mauvais';
            else if(qualite == 3) classe = 'indice-danger';
            document.getElementById('indiceGlobal').className = 'indice-global ' + classe;
            document.getElementById('indiceValeur').innerHTML = qualiteTexte;
            document.getElementById('indiceTexte').innerHTML = getRecommandation(qualite);
            
            // Mise à jour des polluants
            updatePolluant('pm25', data.pm25, normes.pm25.valeur);
            updatePolluant('pm10', data.pm10, normes.pm10.valeur);
            updatePolluant('o3', data.o3, normes.o3.valeur);
            updatePolluant('no2', data.no2, normes.no2.valeur);
            updatePolluant('so2', data.so2, normes.so2.valeur);
            updatePolluant('co', data.co, normes.co.valeur);
            
            // Historique
            let html = '';
            if(data.historique) {
                data.historique.slice().reverse().forEach(h => {
                    let classeHisto = 'event-bon';
                    if(h.qualite == 1) classeHisto = 'event-moyen';
                    else if(h.qualite == 2) classeHisto = 'event-mauvais';
                    else if(h.qualite == 3) classeHisto = 'event-danger';
                    html += `<div class="event ${classeHisto}">🕐 ${h.time} | PM2.5:${h.pm25} | PM10:${h.pm10} | O3:${h.o3} | Qualité: ${h.qualite_texte}</div>`;
                });
                document.getElementById('historiqueList').innerHTML = html;
            }
        });
        
        function updatePolluant(id, valeur, norme) {
            let element = document.getElementById(id);
            let barre = document.getElementById('barre' + id.toUpperCase());
            let statut = document.getElementById('statut' + id.toUpperCase());
            
            if(element) element.innerHTML = valeur !== undefined ? valeur.toFixed(1) : '--';
            
            if(valeur !== undefined && norme) {
                let pourcentage = Math.min((valeur / norme) * 100, 100);
                if(barre) barre.style.width = pourcentage + '%';
                
                if(valeur <= norme) {
                    barre.className = 'barre barre-bon';
                    statut.innerHTML = '✅ Conforme';
                    statut.className = 'norme-ok';
                } else if(valeur <= norme * 1.5) {
                    barre.className = 'barre barre-moyen';
                    statut.innerHTML = '⚠️ Légèrement élevé';
                    statut.className = 'norme-alerte';
                } else {
                    barre.className = 'barre barre-danger';
                    statut.innerHTML = '🔴 DANGER - Dépassement important';
                    statut.className = 'norme-danger';
                }
            }
        }
        
        function getRecommandation(qualite) {
            if(qualite == 0) return '✅ Air sain - Activités normales';
            if(qualite == 1) return '⚠️ Population sensible: réduire les efforts extérieurs';
            if(qualite == 2) return '🚫 Éviter les activités extérieures prolongées';
            return '⛔ URGENCE! Masque obligatoire, restez chez vous';
        }
        
        function led(couleur, action) {
            fetch(`/api/led/${couleur}/${action}`)
                .then(r => r.json())
                .then(data => console.log(data));
        }
        
        // Chargement initial
        fetch('/api/donnees').then(r => r.json()).then(data => {
            if(data.pm25 !== undefined) {
                updatePolluant('pm25', data.pm25, normes.pm25.valeur);
                updatePolluant('pm10', data.pm10, normes.pm10.valeur);
                updatePolluant('o3', data.o3, normes.o3.valeur);
                updatePolluant('no2', data.no2, normes.no2.valeur);
                updatePolluant('so2', data.so2, normes.so2.valeur);
                updatePolluant('co', data.co, normes.co.valeur);
            }
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    # Démarrer le thread MQTT
    mqtt_thread = threading.Thread(target=run_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()
    
    print("=" * 50)
    print("🌍 SMART CITY - QUALITÉ DE L'AIR")
    print("=" * 50)
    print("📡 Serveur: http://localhost:5000")
    print("📡 Broker MQTT: broker.emqx.io")
    print("📡 Topics: air/#")
    print("=" * 50)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)