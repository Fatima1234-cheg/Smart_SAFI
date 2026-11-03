from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Stockage de la dernière donnée
derniere_donnee = {}
historique = []

# Callback MQTT
def on_message(client, userdata, msg):
    global derniere_donnee, historique
    try:
        data = json.loads(msg.payload)
        data['time'] = datetime.now().strftime("%H:%M:%S")
        derniere_donnee = data
        historique.append(data)
        
        # Garder seulement les 50 dernières mesures
        if len(historique) > 50:
            historique.pop(0)
        
        print(f"📥 [{data['time']}] Temp: {data['temperature']}°C | Sol: {data['soil_pct']}% | LED: {data['led_state']}")
    except Exception as e:
        print(f"❌ Erreur traitement MQTT: {e}")

# Connexion MQTT

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_message = on_message
mqtt_client.connect("broker.emqx.io", 1883)
mqtt_client.subscribe("esp32/agri/data")
mqtt_client.loop_start()

# Template HTML
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Station Météo ESP32</title>
    <meta http-equiv="refresh" content="2">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .card {
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .sensor-card {
            background: rgba(255,255,255,0.15);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s;
        }
        .sensor-card:hover {
            transform: translateY(-5px);
        }
        .sensor-value {
            font-size: 3em;
            font-weight: bold;
            margin: 15px 0;
        }
        .sensor-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        .status {
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            font-size: 1.2em;
            font-weight: bold;
        }
        .status-sec {
            background: rgba(255,0,0,0.3);
        }
        .status-humide {
            background: rgba(0,255,0,0.3);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        th {
            background: rgba(255,255,255,0.1);
            font-weight: bold;
        }
        .time {
            font-family: monospace;
            font-size: 0.9em;
        }
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8em;
        }
        .badge-red {
            background: #ff4444;
        }
        .badge-green {
            background: #44ff44;
            color: #333;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .live {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 Station Météo Intelligente 🌡️</h1>
        
        <div class="card">
            <div class="grid">
                <div class="sensor-card">
                    <div class="sensor-label">🌡️ Température</div>
                    <div class="sensor-value" id="temp">{{ data.temperature if data else '--' }}°C</div>
                </div>
                <div class="sensor-card">
                    <div class="sensor-label">💧 Humidité Air</div>
                    <div class="sensor-value" id="hum">{{ data.humidity if data else '--' }}%</div>
                </div>
                <div class="sensor-card">
                    <div class="sensor-label">🌱 Humidité Sol</div>
                    <div class="sensor-value" id="soil">{{ data.soil_pct if data else '--' }}%</div>
                </div>
            </div>
            
            <div class="status {{ 'status-sec' if data and data.led_state == 'red' else 'status-humide' }}" id="status">
                {{ '🔴 SOL SEC - Arrosage nécessaire' if data and data.led_state == 'red' else '🟢 SOL HUMIDE - Tout va bien' }}
            </div>
            <div class="live" style="text-align: center; margin-top: 10px; font-size: 0.8em;">
                🟢 Données en direct
            </div>
        </div>
        
        <div class="card">
            <h2>📊 Historique ({{ historique|length }} mesures)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Heure</th>
                        <th>🌡️ Température</th>
                        <th>💧 Humidité Air</th>
                        <th>🌱 Humidité Sol</th>
                        <th>État</th>
                    </tr>
                </thead>
                <tbody>
                    {% for d in historique|reverse %}
                    <tr>
                        <td class="time">{{ d.time }}</td>
                        <td>{{ d.temperature }}°C</td>
                        <td>{{ d.humidity }}%</td>
                        <td>{{ d.soil_pct }}%</td>
                        <td><span class="badge {{ 'badge-red' if d.led_state == 'red' else 'badge-green' }}">{{ '🔴 Sec' if d.led_state == 'red' else '🟢 Humide' }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        function updateData() {
            fetch('/api/latest')
                .then(response => response.json())
                .then(data => {
                    if(data && data.temperature) {
                        document.getElementById('temp').innerHTML = data.temperature + '°C';
                        document.getElementById('hum').innerHTML = data.humidity + '%';
                        document.getElementById('soil').innerHTML = data.soil_pct + '%';
                        
                        const statusDiv = document.getElementById('status');
                        if(data.led_state === 'red') {
                            statusDiv.innerHTML = '🔴 SOL SEC - Arrosage nécessaire';
                            statusDiv.className = 'status status-sec';
                        } else {
                            statusDiv.innerHTML = '🟢 SOL HUMIDE - Tout va bien';
                            statusDiv.className = 'status status-humide';
                        }
                    }
                });
        }
        
        // Mise à jour automatique toutes les 2 secondes
        setInterval(updateData, 2000);
        updateData();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, data=derniere_donnee, historique=historique)

@app.route('/api/latest')
def api_latest():
    return jsonify(derniere_donnee)

@app.route('/api/all')
def api_all():
    return jsonify(historique)

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 SERVEUR FLASK DÉMARRÉ")
    print("=" * 50)
    print("📡 Accès local: http://localhost:5000")
    print("📡 API données: http://localhost:5000/api/latest")
    print("📡 API historique: http://localhost:5000/api/all")
    print("=" * 50)
    print("\n📥 En attente des données MQTT de l'ESP32...")
    print("   Topic: esp32/agri/data")
    print("   Broker: broker.emqx.io")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)