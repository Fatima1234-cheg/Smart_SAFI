from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import threading
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

# Topics MQTT pour les deux quartiers
TOPICS = {
    'A': {
        'etat': "ville/quartierA/lampadaire/1/etat",
        'evenement': "ville/quartierA/lampadaire/1/evenement",
        'commande': "ville/quartierA/lampadaire/1/commande",
        'nom': "Quartier A",
        'couleur': "#2ecc71",
        'couleur_foncee': "#1a7a3a",
        'has_panne': True,  # Quartier A a 3 pots (gestion panne)
        'has_intensite': True
    },
    'B': {
        'etat': "ville/quartierB/lampadaire/1/etat",
        'evenement': "ville/quartierB/lampadaire/1/evenement",
        'commande': "ville/quartierB/lampadaire/1/commande",
        'nom': "Quartier B",
        'couleur': "#e74c3c",
        'couleur_foncee': "#8b1a1a",
        'has_panne': False,  # Quartier B simple (1 pot)
        'has_intensite': False
    }
}

# Stockage des données pour chaque quartier
donnees_quartiers = {
    'A': {
        'nuit': False,
        'led1': 0, 'led2': 0, 'led3': 0, 'led4': 0,
        'allumees': 0,
        'panne': {'active': False, 'niveau': 0, 'led_grillee': -1},
        'intensite_manuelle': 0,
        'timestamp': None,
        'historique': []
    },
    'B': {
        'nuit': False,
        'led1': 0, 'led2': 0, 'led3': 0, 'led4': 0,
        'allumees': 0,
        'timestamp': None,
        'historique': []
    }
}

# Callbacks MQTT
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"✅ MQTT connecté (code: {rc})")
    for quartier in ['A', 'B']:
        client.subscribe(TOPICS[quartier]['etat'])
        client.subscribe(TOPICS[quartier]['evenement'])

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        
        # Identifier le quartier
        quartier = None
        if 'quartierA' in msg.topic:
            quartier = 'A'
        elif 'quartierB' in msg.topic:
            quartier = 'B'
        
        if not quartier:
            return
        
        if 'etat' in msg.topic:
            donnees_quartiers[quartier]['nuit'] = data.get('nuit', False)
            donnees_quartiers[quartier]['led1'] = data.get('led1', 0)
            donnees_quartiers[quartier]['led2'] = data.get('led2', 0)
            donnees_quartiers[quartier]['led3'] = data.get('led3', 0)
            donnees_quartiers[quartier]['led4'] = data.get('led4', 0)
            
            # Compter LEDs allumées
            allumees = 0
            for led in ['led1', 'led2', 'led3', 'led4']:
                if data.get(led, 0) >= 200:
                    allumees += 1
            donnees_quartiers[quartier]['allumees'] = allumees
            donnees_quartiers[quartier]['timestamp'] = datetime.now().strftime('%H:%M:%S')
            
            socketio.emit(f'maj_etat_{quartier}', donnees_quartiers[quartier])
            print(f"📊 [{quartier}] Nuit={donnees_quartiers[quartier]['nuit']} | LEDs: {donnees_quartiers[quartier]['led1']},{donnees_quartiers[quartier]['led2']},{donnees_quartiers[quartier]['led3']},{donnees_quartiers[quartier]['led4']}")
            
        elif 'evenement' in msg.topic:
            action = data.get('action', '')
            
            # Gestion des pannes pour Quartier A
            if quartier == 'A':
                if "PANNE" in action:
                    if "LÉGÈRE" in action:
                        donnees_quartiers['A']['panne'] = {'active': True, 'niveau': 1, 'led_grillee': -1}
                    elif "MOYENNE" in action:
                        match = re.search(r'LED(\d+)', action)
                        led = int(match.group(1)) if match else -1
                        donnees_quartiers['A']['panne'] = {'active': True, 'niveau': 2, 'led_grillee': led}
                    elif "GRAVE" in action:
                        donnees_quartiers['A']['panne'] = {'active': True, 'niveau': 3, 'led_grillee': -1}
                    elif "Aucune" in action:
                        donnees_quartiers['A']['panne'] = {'active': False, 'niveau': 0, 'led_grillee': -1}
            
            donnees_quartiers[quartier]['historique'].insert(0, {
                'time': datetime.now().strftime('%H:%M:%S'),
                'action': action,
                'nuit': donnees_quartiers[quartier]['nuit']
            })
            if len(donnees_quartiers[quartier]['historique']) > 20:
                donnees_quartiers[quartier]['historique'].pop()
            
            socketio.emit(f'maj_evenement_{quartier}', {'action': action, 'time': datetime.now().strftime('%H:%M:%S')})
            print(f"🎬 [{quartier}] {action}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

# Client MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def run_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_forever()

# Routes Flask
@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/quartier/<quartier>')
def get_quartier(quartier):
    if quartier in donnees_quartiers:
        return jsonify(donnees_quartiers[quartier])
    return jsonify({'error': 'Quartier non trouvé'}), 404

@app.route('/api/commande/<quartier>/<action>')
def envoyer_commande(quartier, action):
    if quartier not in TOPICS:
        return jsonify({'error': 'Quartier invalide'}), 400
    
    mqtt_client.publish(TOPICS[quartier]['commande'], action)
    print(f"📤 [{quartier}] Commande: {action}")
    return jsonify({'status': 'ok', 'quartier': quartier, 'commande': action})

# Page HTML
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Smart City - Éclairage Public</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Segoe UI',Arial;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);color:white;padding:20px;min-height:100vh}
        .container{max-width:1400px;margin:auto}
        h1{text-align:center;color:#ffd700;margin-bottom:10px;font-size:2.2em}
        .subtitle{text-align:center;color:#aaa;margin-bottom:30px}
        
        .quartiers{display:grid;grid-template-columns:repeat(2,1fr);gap:25px}
        
        /* Cartes quartier */
        .quartier-card{background:rgba(255,255,255,0.1);border-radius:20px;padding:20px;backdrop-filter:blur(10px)}
        .quartier-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;padding-bottom:10px;border-bottom:2px solid}
        .quartier-A .quartier-header{border-bottom-color:#2ecc71}
        .quartier-B .quartier-header{border-bottom-color:#e74c3c}
        .quartier-title{font-size:1.5em;font-weight:bold}
        .quartier-A .quartier-title{color:#2ecc71}
        .quartier-B .quartier-title{color:#e74c3c}
        .mode-badge{padding:5px 15px;border-radius:20px;font-size:0.8em}
        .mode-nuit{background:#2c3e50;color:#3498db}
        .mode-jour{background:#f39c12;color:#fff}
        
        /* LEDs */
        .leds{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:20px 0}
        .led{text-align:center}
        .led-bulb{width:60px;height:60px;border-radius:50%;margin:5px auto;display:flex;align-items:center;justify-content:center;font-size:1.5em;transition:0.3s}
        .led-bulb.on100{background:radial-gradient(circle,#ffff00,#ffaa00);box-shadow:0 0 20px #ffaa00;color:#333}
        .led-bulb.on25{background:radial-gradient(circle,#ffff88,#ffcc44);box-shadow:0 0 10px #ffcc44;color:#333;opacity:0.6}
        .led-bulb.off{background:#333;color:#666}
        .led-bulb.panne{background:#555;color:#ff4444;text-decoration:line-through}
        .led-label{font-size:0.7em}
        .led-value{font-size:0.6em;margin-top:3px;color:#aaa}
        
        /* Boutons */
        .boutons{display:flex;justify-content:center;gap:15px;margin:15px 0}
        .btn{padding:10px 20px;border:none;border-radius:10px;cursor:pointer;font-weight:bold;transition:0.3s}
        .btn:hover{transform:scale(1.05);opacity:0.9}
        .btn-success{background:#2ecc71;color:white}
        .btn-danger{background:#e74c3c;color:white}
        .btn-primary{background:#3498db;color:white}
        .btn-warning{background:#f39c12;color:white}
        
        .btn-vert{background:linear-gradient(135deg,#00ff00,#008800);color:white;padding:12px 20px}
        .btn-rouge{background:linear-gradient(135deg,#ff4444,#880000);color:white;padding:12px 20px}
        
        /* Panne card */
        .panne-card{background:rgba(255,0,0,0.2);border:2px solid #ff4444;border-radius:10px;padding:10px;margin:10px 0}
        .panne-card.normal{background:rgba(0,255,0,0.1);border-color:#00ff00}
        .panne-texte{font-size:0.8em}
        
        /* Historique */
        .historique{background:rgba(0,0,0,0.3);border-radius:10px;padding:10px;max-height:150px;overflow-y:auto;margin-top:10px}
        .event{padding:5px;border-bottom:1px solid #333;font-size:0.75em}
        .event-time{color:#aaa}
        .event-action{color:#ffd700}
        
        .footer{text-align:center;margin-top:30px;color:#aaa;font-size:0.75em}
        .statut{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px}
        .statut.online{background:#2ecc71;box-shadow:0 0 5px #2ecc71}
        
        @media(max-width:900px){
            .quartiers{grid-template-columns:1fr}
            .leds{grid-template-columns:repeat(2,1fr)}
        }
    </style>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>🏙️ SMART CITY - ÉCLAIRAGE PUBLIC</h1>
        <div class="subtitle">Quartier A (3 Pots + Pannes) | Quartier B (Simple) | Extinction auto 8s</div>
        
        <div class="quartiers">
            <!-- ==================== QUARTIER A ==================== -->
            <div class="quartier-card quartier-A" id="quartierA">
                <div class="quartier-header">
                    <span class="quartier-title">🏘️ Quartier A</span>
                    <span class="mode-badge" id="modeA">🌙 NUIT</span>
                </div>
                
                <!-- Panneau panne pour Quartier A -->
                <div id="panneCardA" class="panne-card normal">
                    <div class="panne-texte" id="panneTexteA">✅ Système normal</div>
                </div>
                
                <!-- LEDs -->
                <div class="leds" id="ledsA"></div>
                
                <!-- Boutons -->
                <div class="boutons">
                    <button class="btn-vert" onclick="envoyerCommande('A', 'GAUCHE')">🟢 Allumer ← →</button>
                    <button class="btn-rouge" onclick="envoyerCommande('A', 'DROITE')">🔴 Allumer → ←</button>
                </div>
                <div class="boutons">
                    <button class="btn btn-success" onclick="envoyerCommande('A', 'ALLUMER_TOUT')">🔆 Tout allumer</button>
                    <button class="btn btn-danger" onclick="envoyerCommande('A', 'ETEINDRE_TOUT')">⬛ Tout éteindre</button>
                </div>
                
                <!-- Historique -->
                <div class="historique" id="historiqueA">
                    <div class="event">⏳ En attente...</div>
                </div>
                <div style="font-size:0.7em;color:#aaa;margin-top:8px;text-align:center">
                    🎛️ 3 Pots: J/N | Panne | Intensité
                </div>
            </div>
            
            <!-- ==================== QUARTIER B ==================== -->
            <div class="quartier-card quartier-B" id="quartierB">
                <div class="quartier-header">
                    <span class="quartier-title">🏘️ Quartier B</span>
                    <span class="mode-badge" id="modeB">🌙 NUIT</span>
                </div>
                
                <!-- LEDs -->
                <div class="leds" id="ledsB"></div>
                
                <!-- Boutons -->
                <div class="boutons">
                    <button class="btn-vert" onclick="envoyerCommande('B', 'GAUCHE')">🟢 Allumer ← →</button>
                    <button class="btn-rouge" onclick="envoyerCommande('B', 'DROITE')">🔴 Allumer → ←</button>
                </div>
                <div class="boutons">
                    <button class="btn btn-success" onclick="envoyerCommande('B', 'ALLUMER_TOUT')">🔆 Tout allumer</button>
                    <button class="btn btn-danger" onclick="envoyerCommande('B', 'ETEINDRE_TOUT')">⬛ Tout éteindre</button>
                </div>
                
                <!-- Historique -->
                <div class="historique" id="historiqueB">
                    <div class="event">⏳ En attente...</div>
                </div>
                <div style="font-size:0.7em;color:#aaa;margin-top:8px;text-align:center">
                    🎛️ 1 Pot: Jour/Nuit
                </div>
            </div>
        </div>
        
        <div class="footer">
            <span class="statut online"></span> MQTT Connecté |
            🔆 Allumage progressif (2s) | ⏱️ Extinction auto après 8s |
            🎛️ Quartier A: 3 pots (J/N, Panne, Intensité) | Quartier B: 1 pot (J/N)
        </div>
    </div>
    
    <script>
        const socket = io();
        
        function getPourcentage(valeur) {
            if (valeur >= 200) return 100;
            if (valeur >= 50) return 25;
            return 0;
        }
        
        function updateLEDs(quartier, data, panneInfo) {
            const container = document.getElementById(`leds${quartier}`);
            if (!container) return;
            
            const leds = [
                {id: 1, valeur: data.led1, nom: 'GAUCHE'},
                {id: 2, valeur: data.led2, nom: 'LED2'},
                {id: 3, valeur: data.led3, nom: 'LED3'},
                {id: 4, valeur: data.led4, nom: 'DROITE'}
            ];
            
            let html = '';
            leds.forEach(led => {
                const pourcent = getPourcentage(led.valeur);
                let classe = 'off';
                let icon = '⚫';
                
                // Vérifier panne pour Quartier A
                let estEnPanne = false;
                if (panneInfo && panneInfo.active && panneInfo.led_grillee === led.id) {
                    classe = 'panne';
                    icon = '❌';
                } else if (pourcent === 100) {
                    classe = 'on100';
                    icon = '💡';
                } else if (pourcent === 25) {
                    classe = 'on25';
                    icon = '💡';
                } else {
                    classe = 'off';
                    icon = '⚫';
                }
                
                let texte = pourcent === 100 ? '100%' : (pourcent === 25 ? '25%' : '0%');
                if (estEnPanne) texte = 'PANNE';
                
                html += `
                    <div class="led">
                        <div class="led-bulb ${classe}">${icon}</div>
                        <div class="led-label">LED${led.id}<br>(${led.nom})</div>
                        <div class="led-value">${texte}</div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }
        
        function updateMode(quartier, nuit) {
            const modeElement = document.getElementById(`mode${quartier}`);
            if (modeElement) {
                if (nuit) {
                    modeElement.innerHTML = "🌙 NUIT";
                    modeElement.className = "mode-badge mode-nuit";
                } else {
                    modeElement.innerHTML = "☀️ JOUR";
                    modeElement.className = "mode-badge mode-jour";
                }
            }
        }
        
        function updatePanneCard(quartier, panne) {
            if (quartier !== 'A') return;
            const card = document.getElementById('panneCardA');
            const texte = document.getElementById('panneTexteA');
            
            if (!card || !texte) return;
            
            if (!panne.active || panne.niveau === 0) {
                card.className = "panne-card normal";
                texte.innerHTML = "✅ Système normal - Aucune panne";
            } else if (panne.niveau === 1) {
                card.className = "panne-card";
                texte.innerHTML = "⚠️ PANNE LÉGÈRE - Intensité réduite de 50%";
            } else if (panne.niveau === 2) {
                card.className = "panne-card";
                texte.innerHTML = `🔴 PANNE MOYENNE - LED${panne.led_grillee} est grillée !`;
            } else {
                card.className = "panne-card";
                texte.innerHTML = "💀 PANNE GRAVE - Système défaillant !";
            }
        }
        
        function ajouterEvenement(quartier, event) {
            const container = document.getElementById(`historique${quartier}`);
            if (!container) return;
            
            const newEvent = document.createElement('div');
            newEvent.className = 'event';
            let actionHtml = event.action;
            if (actionHtml.includes("PANNE")) {
                actionHtml = `⚠️ ${actionHtml}`;
            } else if (actionHtml.includes("ALLUMAGE")) {
                actionHtml = `🔆 ${actionHtml}`;
            }
            newEvent.innerHTML = `<span class="event-time">🕐 ${event.time}</span> - <span class="event-action">${actionHtml}</span>`;
            container.insertBefore(newEvent, container.firstChild);
            
            while (container.children.length > 8) {
                container.removeChild(container.lastChild);
            }
        }
        
        // Socket listeners pour Quartier A
        socket.on('maj_etat_A', function(data) {
            updateMode('A', data.nuit);
            const panne = data.panne || {active: false, niveau: 0, led_grillee: -1};
            updateLEDs('A', data, panne);
            updatePanneCard('A', panne);
        });
        
        socket.on('maj_evenement_A', function(data) {
            ajouterEvenement('A', data);
        });
        
        // Socket listeners pour Quartier B
        socket.on('maj_etat_B', function(data) {
            updateMode('B', data.nuit);
            updateLEDs('B', data, null);
        });
        
        socket.on('maj_evenement_B', function(data) {
            ajouterEvenement('B', data);
        });
        
        function envoyerCommande(quartier, action) {
            console.log(`Commande ${quartier}: ${action}`);
            fetch(`/api/commande/${quartier}/${action}`)
                .then(r => r.json())
                .then(data => console.log(data));
        }
        
        // Chargement initial
        async function chargerDonnees() {
            for (let q of ['A', 'B']) {
                try {
                    const reponse = await fetch(`/api/quartier/${q}`);
                    const data = await reponse.json();
                    if (data.led1 !== undefined) {
                        const panne = data.panne || {active: false, niveau: 0, led_grillee: -1};
                        updateLEDs(q, data, q === 'A' ? panne : null);
                        updateMode(q, data.nuit);
                        if (q === 'A') updatePanneCard(q, panne);
                    }
                    if (data.historique) {
                        const container = document.getElementById(`historique${q}`);
                        if (container) {
                            container.innerHTML = '';
                            data.historique.slice(0, 8).forEach(event => {
                                const newEvent = document.createElement('div');
                                newEvent.className = 'event';
                                newEvent.innerHTML = `<span class="event-time">🕐 ${event.time}</span> - <span class="event-action">${event.action}</span>`;
                                container.appendChild(newEvent);
                            });
                        }
                    }
                } catch(e) {
                    console.error("Erreur chargement", q, e);
                }
            }
        }
        
        chargerDonnees();
        setInterval(chargerDonnees, 5000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    threading.Thread(target=run_mqtt, daemon=True).start()
    print("🚀 Serveur Flask: http://localhost:5000")
    print("=" * 70)
    print("📡 QUARTIERS CONFIGURÉS:")
    print(f"\n   🏘️ QUARTIER A (3 Pots + Gestion panne)")
    print(f"      - État: {TOPICS['A']['etat']}")
    print(f"      - Événements: {TOPICS['A']['evenement']}")
    print(f"      - Commandes: {TOPICS['A']['commande']}")
    print(f"\n   🏘️ QUARTIER B (Simple)")
    print(f"      - État: {TOPICS['B']['etat']}")
    print(f"      - Événements: {TOPICS['B']['evenement']}")
    print(f"      - Commandes: {TOPICS['B']['commande']}")
    print("=" * 70)
    print("🎮 COMMANDES DISPONIBLES:")
    print("   - GAUCHE : Allumage progressif GAUCHE → DROITE")
    print("   - DROITE : Allumage progressif DROITE → GAUCHE")
    print("   - ALLUMER_TOUT : Allume tous les lampadaires")
    print("   - ETEINDRE_TOUT : Éteint tous les lampadaires")
    print("=" * 70)
    print("🎛️ SPÉCIFICITÉS:")
    print("   - Quartier A: 3 potentiomètres (Jour/Nuit, Panne, Intensité manuelle)")
    print("   - Quartier B: 1 potentiomètre (Jour/Nuit)")
    print("=" * 70)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)