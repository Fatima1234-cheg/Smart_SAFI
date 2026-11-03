from flask import Flask, render_template_string, jsonify
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import threading

app = Flask(__name__)

# Configuration MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

# Stockage des données
donnees_eau = {
    'pH': 7.0,
    'turbidite': 0,
    'conductivite': 0,
    'qualite': 0,
    'qualite_texte': 'POTABLE',
    'icone': '🟢',
    'problemes': [],
    'timestamp': None
}

# Seuils selon ESP32
def evaluer_qualite_complete():
    pH = donnees_eau['pH']
    turb = donnees_eau['turbidite']
    cond = donnees_eau['conductivite']
    
    # Logique de qualité
    danger = False
    attention = False
    
    # pH
    if pH < 5.5 or pH > 9.5:
        danger = True
    elif pH < 6.5 or pH > 8.5:
        attention = True
    
    # Turbidité
    if turb > 5:
        danger = True
    elif turb > 1:
        attention = True
    
    # Conductivité
    if cond > 600:
        danger = True
    elif cond > 400:
        attention = True
    
    # Déterminer qualité
    if danger:
        qualite = 2
        qualite_texte = "DANGER"
        icone = "🔴"
    elif attention:
        qualite = 1
        qualite_texte = "ATTENTION"
        icone = "🟡"
    else:
        qualite = 0
        qualite_texte = "POTABLE"
        icone = "🟢"
    
    # Trouver problèmes spécifiques
    problemes = []
    if pH < 5.5:
        problemes.append(f"⚠️ pH TROP BAS: {pH} (minimum 5.5)")
    elif pH > 9.5:
        problemes.append(f"⚠️ pH TROP HAUT: {pH} (maximum 9.5)")
    elif pH < 6.5:
        problemes.append(f"⚠️ pH BAS: {pH} (normal 6.5-8.5)")
    elif pH > 8.5:
        problemes.append(f"⚠️ pH HAUT: {pH} (normal 6.5-8.5)")
    
    if turb > 5:
        problemes.append(f"⚠️ Turbidité TRÈS ÉLEVÉE: {turb} NTU (maximum 5)")
    elif turb > 1:
        problemes.append(f"⚠️ Turbidité ÉLEVÉE: {turb} NTU (normal <1)")
    
    if cond > 600:
        problemes.append(f"⚠️ Conductivité TRÈS ÉLEVÉE: {cond} µS/cm (maximum 600)")
    elif cond > 400:
        problemes.append(f"⚠️ Conductivité ÉLEVÉE: {cond} µS/cm (normal <400)")
    
    donnees_eau['qualite'] = qualite
    donnees_eau['qualite_texte'] = qualite_texte
    donnees_eau['icone'] = icone
    donnees_eau['problemes'] = problemes
    donnees_eau['timestamp'] = datetime.now().strftime('%H:%M:%S')

# Callbacks MQTT
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"✅ MQTT connecté (code: {rc})")
    client.subscribe("eau/ph")
    client.subscribe("eau/turbidite")
    client.subscribe("eau/conductivite")
    client.subscribe("eau/qualite")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        payload = msg.payload.decode()
        
        if topic == "eau/ph":
            donnees_eau['pH'] = float(payload)
            print(f"📥 pH: {donnees_eau['pH']}")
        elif topic == "eau/turbidite":
            donnees_eau['turbidite'] = float(payload)
            print(f"📥 Turbidité: {donnees_eau['turbidite']}")
        elif topic == "eau/conductivite":
            donnees_eau['conductivite'] = float(payload)
            print(f"📥 Conductivité: {donnees_eau['conductivite']}")
        elif topic == "eau/qualite":
            try:
                data = json.loads(payload)
                donnees_eau['pH'] = float(data.get('pH', donnees_eau['pH']))
                donnees_eau['turbidite'] = float(data.get('turbidite', donnees_eau['turbidite']))
                donnees_eau['conductivite'] = float(data.get('conductivite', donnees_eau['conductivite']))
            except:
                pass
        
        # Recalculer la qualité
        evaluer_qualite_complete()
        
        # Afficher dans console
        print(f"\n🏆 {donnees_eau['icone']} {donnees_eau['qualite_texte']}")
        if donnees_eau['problemes']:
            for p in donnees_eau['problemes']:
                print(f"   {p}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

# Client MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def run_mqtt():
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"❌ Erreur MQTT: {e}")

# Routes Flask
@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/donnees')
def get_donnees():
    return jsonify(donnees_eau)

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
        mqtt_client.publish("eau/led/commande", cmd)
        return jsonify({'status': 'ok', 'commande': cmd})
    return jsonify({'error': 'Couleur invalide'}), 400

# Page HTML avec rafraîchissement automatique
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Qualité de l'Eau - Smart City</title>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="2">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Segoe UI',Arial;background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;padding:20px;min-height:100vh}
        .container{max-width:1200px;margin:auto}
        h1{text-align:center;color:#ffd700;margin-bottom:30px;font-size:2.5em}
        .dashboard{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-bottom:20px}
        .card{background:rgba(255,255,255,0.1);border-radius:20px;padding:25px;backdrop-filter:blur(10px);text-align:center}
        .card h2{font-size:1.2em;color:#aaa;margin-bottom:15px}
        .valeur{font-size:3em;font-weight:bold;margin:10px 0}
        .unite{font-size:0.8em;color:#aaa}
        .status{font-size:0.9em;margin-top:10px;padding:8px;border-radius:8px}
        .status.normal{background:rgba(0,255,0,0.2);color:#00ff00}
        .status.attention{background:rgba(255,170,0,0.2);color:#ffaa00}
        .status.danger{background:rgba(255,68,68,0.2);color:#ff4444}
        .conclusion-card{background:rgba(255,255,255,0.15);border-radius:20px;padding:25px;margin-bottom:20px;text-align:center}
        .qualite{font-size:2.5em;font-weight:bold;margin:10px 0}
        .qualite.normal{color:#00ff00}
        .qualite.attention{color:#ffaa00}
        .qualite.danger{color:#ff4444}
        .problemes{background:rgba(0,0,0,0.3);border-radius:15px;padding:15px;margin-top:15px;text-align:left}
        .probleme-item{background:rgba(255,68,68,0.2);border-left:4px solid #ff4444;padding:12px;margin:8px 0;border-radius:5px}
        .ok-item{background:rgba(0,255,0,0.1);border-left:4px solid #00ff00;padding:12px;margin:8px 0;border-radius:5px;color:#00ff00}
        button{background:#ffd700;color:#1a1a2e;border:none;padding:10px 20px;margin:5px;border-radius:8px;cursor:pointer;font-weight:bold;transition:0.3s}
        button:hover{transform:scale(1.05);background:#ffed4a}
        .led-panel{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:20px}
        .timestamp{text-align:center;color:#aaa;margin-top:10px;font-size:0.8em}
    </style>
</head>
<body>
    <div class="container">
        <h1>💧 QUALITÉ DE L'EAU - SMART CITY 🌊</h1>
        
        <div class="dashboard">
            <div class="card">
                <h2>🌡️ pH</h2>
                <div class="valeur" id="phValue">--</div>
                <div class="unite">(6.5 - 8.5 normal)</div>
                <div class="status" id="phStatus">--</div>
            </div>
            
            <div class="card">
                <h2>💨 Turbidité</h2>
                <div class="valeur" id="turbValue">--</div>
                <div class="unite">NTU (&lt;1 bonne, &lt;5 attention)</div>
                <div class="status" id="turbStatus">--</div>
            </div>
            
            <div class="card">
                <h2>⚡ Conductivité</h2>
                <div class="valeur" id="condValue">--</div>
                <div class="unite">µS/cm (&lt;400 bonne, &lt;600 attention)</div>
                <div class="status" id="condStatus">--</div>
            </div>
        </div>
        
        <div class="conclusion-card">
            <h2>🏆 CONCLUSION</h2>
            <div class="qualite" id="qualiteGlobale">--</div>
            <div id="problemesContainer"></div>
        </div>
        
        <div class="card">
            <h2>🎮 Contrôle des LEDs</h2>
            <div class="led-panel">
                <button onclick="led('rouge','on')">🔴 Rouge ON</button>
                <button onclick="led('rouge','off')">⚫ Rouge OFF</button>
                <button onclick="led('jaune','on')">🟡 Jaune ON</button>
                <button onclick="led('jaune','off')">⚫ Jaune OFF</button>
                <button onclick="led('verte','on')">🟢 Verte ON</button>
                <button onclick="led('verte','off')">⚫ Verte OFF</button>
                <button onclick="led('all','on')">✨ ALL ON</button>
                <button onclick="led('all','off')">⬛ ALL OFF</button>
            </div>
        </div>
        
        <div class="timestamp" id="timestamp">--</div>
    </div>
    
    <script>
        function mettreAJourAffichage() {
            fetch('/api/donnees')
                .then(response => response.json())
                .then(data => {
                    console.log("Données reçues:", data);
                    
                    // Mettre à jour les valeurs
                    document.getElementById('phValue').innerHTML = data.pH;
                    document.getElementById('turbValue').innerHTML = data.turbidite;
                    document.getElementById('condValue').innerHTML = data.conductivite;
                    document.getElementById('timestamp').innerHTML = "🕐 Dernière mise à jour: " + (data.timestamp || "--");
                    
                    // Statut pH
                    let phStatus = document.getElementById('phStatus');
                    if (data.pH < 5.5 || data.pH > 9.5) {
                        phStatus.innerHTML = `🔴 DANGER: pH ${data.pH}`;
                        phStatus.className = "status danger";
                    } else if (data.pH < 6.5 || data.pH > 8.5) {
                        phStatus.innerHTML = `🟡 ATTENTION: pH ${data.pH}`;
                        phStatus.className = "status attention";
                    } else {
                        phStatus.innerHTML = `✅ NORMAL: pH ${data.pH}`;
                        phStatus.className = "status normal";
                    }
                    
                    // Statut Turbidité
                    let turbStatus = document.getElementById('turbStatus');
                    if (data.turbidite > 5) {
                        turbStatus.innerHTML = `🔴 DANGER: ${data.turbidite} NTU`;
                        turbStatus.className = "status danger";
                    } else if (data.turbidite > 1) {
                        turbStatus.innerHTML = `🟡 ATTENTION: ${data.turbidite} NTU`;
                        turbStatus.className = "status attention";
                    } else {
                        turbStatus.innerHTML = `✅ NORMAL: ${data.turbidite} NTU`;
                        turbStatus.className = "status normal";
                    }
                    
                    // Statut Conductivité
                    let condStatus = document.getElementById('condStatus');
                    if (data.conductivite > 600) {
                        condStatus.innerHTML = `🔴 DANGER: ${data.conductivite} µS/cm`;
                        condStatus.className = "status danger";
                    } else if (data.conductivite > 400) {
                        condStatus.innerHTML = `🟡 ATTENTION: ${data.conductivite} µS/cm`;
                        condStatus.className = "status attention";
                    } else {
                        condStatus.innerHTML = `✅ NORMAL: ${data.conductivite} µS/cm`;
                        condStatus.className = "status normal";
                    }
                    
                    // Conclusion
                    let qualiteElem = document.getElementById('qualiteGlobale');
                    qualiteElem.innerHTML = `${data.icone} ${data.qualite_texte}`;
                    qualiteElem.className = "qualite " + (data.qualite == 0 ? "normal" : (data.qualite == 1 ? "attention" : "danger"));
                    
                    // Problèmes
                    let problemesDiv = document.getElementById('problemesContainer');
                    if (data.problemes && data.problemes.length > 0) {
                        let html = '<div class="problemes"><strong>❌ PROBLÈMES DÉTECTÉS :</strong>';
                        data.problemes.forEach(p => {
                            html += `<div class="probleme-item">${p}</div>`;
                        });
                        html += '</div>';
                        problemesDiv.innerHTML = html;
                    } else {
                        problemesDiv.innerHTML = '<div class="ok-item">✅ TOUS LES PARAMÈTRES SONT NORMAUX</div>';
                    }
                })
                .catch(error => console.error("Erreur:", error));
        }
        
        function led(couleur, action) {
            fetch(`/api/led/${couleur}/${action}`)
                .then(r => r.json())
                .then(data => console.log(data));
        }
        
        // Mettre à jour toutes les 2 secondes
        setInterval(mettreAJourAffichage, 2000);
        mettreAJourAffichage();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    threading.Thread(target=run_mqtt, daemon=True).start()
    print("🚀 Serveur Flask: http://localhost:5000")
    print("\n📊 SEUILS DE QUALITÉ:")
    print(f"   🌡️ pH: NORMAL 6.5-8.5 | ATTENTION 5.5-9.5 | DANGER hors limites")
    print(f"   💨 Turbidité: NORMAL <1 | ATTENTION <5 | DANGER ≥5 NTU")
    print(f"   ⚡ Conductivité: NORMAL <400 | ATTENTION <600 | DANGER ≥600 µS/cm")
    print("\n⏳ En attente des données MQTT...\n")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)