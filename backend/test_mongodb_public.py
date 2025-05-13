"""
Script simple para probar la conexión y migración a MongoDB usando la URL pública.
"""
import os
import sys
import json
import time
from pymongo import MongoClient
from datetime import datetime

def test_migrate():
    print("Testing MongoDB connection...")
    
    # Obtener la URL pública de MongoDB de las variables de entorno
    mongo_public_url = os.environ.get('MONGO_PUBLIC_URL', 'mongodb://mongo:bWgsojLFnVDtiYwGqFyQbSdqSuyqttCY@gondola.proxy.rlwy.net:18973')
    print(f"URL a usar: {mongo_public_url.replace(mongo_public_url.split('@')[0], 'mongodb://[CREDENTIALS_HIDDEN]')}")
    
    # Intentar conectar con MongoDB usando la URL pública
    print(f"Connecting to MongoDB using public URL...")
    
    try:
        # Crear cliente de MongoDB
        client = MongoClient(mongo_public_url, serverSelectionTimeoutMS=20000)
        
        # Verificar la conexión
        print("Sending ping command...")
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # Obtener/crear base de datos
        db_name = os.environ.get('MONGO_DB_NAME', 'image_classifier_db')
        db = client[db_name]
        print(f"Using database: {db_name}")
        
        # Crear una colección de prueba
        print("Creating test document...")
        test_collection = db.test_collection
        test_doc = {
            "test_id": "test_" + datetime.now().isoformat(),
            "message": "Test connection successful",
            "timestamp": datetime.now().isoformat()
        }
        
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Verificar si ya existen colecciones
        print("Listing collections...")
        collections = db.list_collection_names()
        print(f"Existing collections: {', '.join(collections)}")
        
        # Cerrar conexión
        client.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_migrate()
    sys.exit(0 if success else 1)
