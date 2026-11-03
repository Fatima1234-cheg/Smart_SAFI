"""
MQTT Service for Smart City - SmartSafi
"""

import json
import threading
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from flask import current_app


class MQTTClient:
    """Client MQTT pour la communication IoT"""
    
    def __init__(self):
        self.client = None
        self.connected = False
        self.topics = []
        self.message_handlers = {}
        self._thread = None
        self._stop_event = threading.Event()
    
    def init_app(self, app):
        """Initialiser avec l'application Flask"""
        self.broker = app.config.get('MQTT_BROKER_HOST', 'localhost')
        self.port = app.config.get('MQTT_BROKER_PORT', 1883)
        self.username = app.config.get('MQTT_USERNAME', '')
        self.password = app.config.get('MQTT_PASSWORD', '')
        self.keepalive = app.config.get('MQTT_KEEPALIVE', 60)
        self.use_tls = app.config.get('MQTT_USE_TLS', False)
        
        # Topics
        self.topics = [
            app.config.get('MQTT_TOPIC_WASTE', 'smartcity/waste'),
            app.config.get('MQTT_TOPIC_WATER', 'smartcity/water'),
            app.config.get('MQTT_TOPIC_AIR', 'smartcity/air'),
            app.config.get('MQTT_TOPIC_AGRICULTURE', 'smartcity/agriculture'),
            app.config.get('MQTT_TOPIC_LIGHTING', 'smartcity/lighting')
        ]
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback de connexion"""
        if rc == 0:
            self.connected = True
            print(f"MQTT: Connecté à {self.broker}:{self.port}")
            
            # Souscrire aux topics
            for topic in self.topics:
                client.subscribe(topic)
                print(f"MQTT: Souscrit à {topic}")
        else:
            print(f"MQTT: Échec de connexion, code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback de déconnexion"""
        self.connected = False
        print(f"MQTT: Déconnecté, code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback de réception de message"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
            
            print(f"MQTT: Message reçu sur {topic}: {payload[:100]}...")
            
            # Traiter le message selon le topic
            self._process_message(topic, data)
            
        except Exception as e:
            print(f"MQTT: Erreur de traitement du message: {e}")
    
    def _process_message(self, topic, data):
        """Traiter un message MQTT selon son topic"""
        with current_app.app_context():
            try:
                if 'waste' in topic:
                    from app.models.waste import Waste
                    Waste.create(data)
                elif 'water' in topic:
                    from app.models.water import Water
                    Water.create(data)
                elif 'air' in topic:
                    from app.models.air import Air
                    Air.create(data)
                elif 'agriculture' in topic:
                    from app.models.agriculture import Agriculture
                    Agriculture.create(data)
                elif 'lighting' in topic:
                    from app.models.lighting import Lighting
                    Lighting.create(data)
                
                print(f"MQTT: Données enregistrées pour {topic}")
                
            except Exception as e:
                print(f"MQTT: Erreur d'enregistrement: {e}")
    
    def start(self):
        """Démarrer le client MQTT dans un thread séparé"""
        if self._thread and self._thread.is_alive():
            print("MQTT: Client déjà en cours d'exécution")
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("MQTT: Thread démarré")
    
    def _run(self):
        """Boucle principale du client MQTT"""
        self.client = mqtt.Client()
        
        # Configurer les callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Authentification
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # TLS/SSL
        if self.use_tls:
            self.client.tls_set()
        
        try:
            # Connexion
            self.client.connect(self.broker, self.port, self.keepalive)
            
            # Boucle de traitement des messages
            while not self._stop_event.is_set():
                self.client.loop(timeout=1.0)
                
        except Exception as e:
            print(f"MQTT: Erreur dans la boucle: {e}")
        finally:
            self.client.disconnect()
            print("MQTT: Déconnecté")
    
    def stop(self):
        """Arrêter le client MQTT"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)
        print("MQTT: Arrêté")
    
    def publish(self, topic, payload, qos=0, retain=False):
        """Publier un message sur un topic"""
        if not self.connected or not self.client:
            print("MQTT: Non connecté, impossible de publier")
            return False
        
        try:
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            
            result = self.client.publish(topic, payload, qos, retain)
            return result.rc == 0
        except Exception as e:
            print(f"MQTT: Erreur de publication: {e}")
            return False


# Instance globale du client MQTT
mqtt_client = MQTTClient()
