# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Atlas (cloud) ou local
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'smart_city_safi')
    
    # Ou utilisez MongoDB Atlas gratuit :
    # MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/"
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'smart_city_safi_2024')