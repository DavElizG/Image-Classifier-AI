"""
Script para migrar datos de clasificación desde almacenamiento basado en archivos a MongoDB local.
"""
import os
import sys
import time
from datetime import datetime
from pymongo import MongoClient
from utils.stats_new import ClassificationStats

def migrate_to_local_mongodb():
    """
    Migrar datos del almacenamiento basado en archivos a MongoDB local.
    """
    print("=" * 80)
    print(" MIGRACIÓN DE DATOS A MONGODB LOCAL ".center(80, "="))
    print("=" * 80)
    
    mongo_uri = "mongodb://localhost:27017"
    db_name = "ImageClassifier"
    
    print(f"\nConectando a MongoDB local: {mongo_uri}")
    print(f"Base de datos: {db_name}")
    
    try:
        # Conectar a MongoDB
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Verificar la conexión con un ping
        client.admin.command('ping')
        print("✅ Conexión exitosa a MongoDB local")
        
        # Obtener/crear base de datos
        db = client[db_name]
        
        # Crear colecciones si no existen
        if "classifications" not in db.list_collection_names():
            db.create_collection("classifications")
            db.classifications.create_index([("timestamp", -1)])
            db.classifications.create_index([("category", 1)])
            print("✅ Colección 'classifications' creada con índices")
        
        if "daily_stats" not in db.list_collection_names():
            db.create_collection("daily_stats")
            db.daily_stats.create_index([("date", -1)])
            print("✅ Colección 'daily_stats' creada con índices")
        
        if "statistics" not in db.list_collection_names():
            db.create_collection("statistics")
            # Insertar documento inicial de estadísticas globales si no existe
            if db.statistics.count_documents({"_id": "global"}) == 0:
                db.statistics.insert_one({
                    "_id": "global",
                    "total_classifications": 0,
                    "last_updated": None,
                    "categories": {}
                })
            print("✅ Colección 'statistics' creada")
        
        # Crear instancia de stats basada en archivos
        print("\nCargando datos de archivos...")
        file_stats = ClassificationStats()
        
        # Obtener estadísticas
        stats_data = file_stats.get_stats(days=365)  # Obtener todos los datos diarios disponibles
        
        # Importar estadísticas globales
        print("\nMigrando estadísticas globales...")
        db.statistics.replace_one(
            {"_id": "global"},
            {
                "_id": "global",
                "total_classifications": stats_data.get("total_classifications", 0),
                "categories": stats_data.get("categories", {}),
                "last_updated": stats_data.get("last_updated")
            },
            upsert=True
        )
        print(f"✅ Estadísticas globales migradas: {stats_data.get('total_classifications', 0)} clasificaciones")
        
        # Importar estadísticas diarias
        print("\nMigrando estadísticas diarias...")
        days_migrated = 0
        for date, daily_data in stats_data.get("daily", {}).items():
            db.daily_stats.replace_one(
                {"_id": date},
                {
                    "_id": date,
                    "date": date,
                    "total": daily_data.get("total", 0),
                    "categories": daily_data.get("categories", {})
                },
                upsert=True
            )
            days_migrated += 1
        print(f"✅ Estadísticas diarias migradas: {days_migrated} días")
        
        # Importar historial de clasificaciones
        print("\nMigrando historial de clasificaciones...")
        history = file_stats.get_classification_history(limit=1000000)  # Obtener todo el historial
        items_migrated = 0
        
        for item in history:
            item_id = item.get("id")
            if item_id:
                # Verificar si ya existe
                if db.classifications.count_documents({"id": item_id}) == 0:
                    # Añadir campo _id de MongoDB
                    item["_id"] = item_id
                    db.classifications.insert_one(item)
                    items_migrated += 1
        
        print(f"✅ Historial de clasificaciones migrado: {items_migrated} elementos")
        
        # Mostrar colecciones y conteos
        print("\nResumen de migración:")
        for collection_name in db.list_collection_names():
            count = db.get_collection(collection_name).count_documents({})
            print(f"- {collection_name}: {count} documentos")
        
        print("\n" + "=" * 80)
        print(" MIGRACIÓN COMPLETADA EXITOSAMENTE ".center(80, "="))
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cerrar conexión a MongoDB si existe
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    # Verificar si MongoDB está en ejecución
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        client.close()
    except Exception as e:
        print("❌ No se puede conectar a MongoDB local. Asegúrate de que MongoDB esté instalado y en ejecución.")
        print(f"Error: {e}")
        sys.exit(1)
    
    # Ejecutar migración
    success = migrate_to_local_mongodb()
    
    # Salir con código apropiado
    sys.exit(0 if success else 1)
