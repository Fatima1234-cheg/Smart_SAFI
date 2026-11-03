# create_user_standalone.py
import bcrypt
from pymongo import MongoClient
from datetime import datetime

# ===== CONFIGURATION (à modifier selon votre projet) =====
MONGO_URI = "mongodb://localhost:27017/"   # ou l'URI de votre cluster MongoDB Atlas
DB_NAME = "smart_city_safi"                # nom de votre base de données

def add_user(username, password, role='chauffeur', email="", telephone="", nom="", regions=None):
    if regions is None:
        regions = []
    if role not in ['admin', 'chauffeur']:
        print(f"❌ Rôle invalide : {role}. Choisissez 'admin' ou 'chauffeur'.")
        return False

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users = db['users']

    if users.find_one({'username': username}):
        print(f"❌ L'utilisateur '{username}' existe déjà.")
        client.close()
        return False

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {
        'username': username,
        'password': hashed,
        'role': role,
        'nom': nom or username,
        'email': email,
        'telephone': telephone,
        'regions': regions,
        'actif': True,
        'created_at': datetime.now(),
        'last_login': None
    }
    users.insert_one(user)
    print(f"✅ Utilisateur '{username}' ({role}) ajouté avec succès.")
    client.close()
    return True

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python create_user.py <username> <password> [role] [email] [telephone] [nom]")
        print("Exemple: python create_user.py karim karim123 chauffeur karim@exemple.com '0612345678' 'Karim Sbai'")
        print("       python create_user.py admin admin123 admin admin@exemple.com '0523456789' 'Administrateur'")
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else 'chauffeur'
    email = sys.argv[4] if len(sys.argv) > 4 else ""
    telephone = sys.argv[5] if len(sys.argv) > 5 else ""
    nom = sys.argv[6] if len(sys.argv) > 6 else username
    regions = []   # ou ['nord', 'sud'] si vous voulez assigner des régions
    add_user(username, password, role, email, telephone, nom, regions)