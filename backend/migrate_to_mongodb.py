"""
Script para migrar datos de clasificación del almacenamiento basado en archivos a MongoDB.
Este script migra toda la información de clasificaciones, estadísticas y metadatos de imágenes
desde el sistema de archivos a la base de datos MongoDB.
"""
import os
import sys
import time
import shutil
from datetime import datetime
from config import Config
from utils.stats_new import ClassificationStats
from utils.mongodb_stats import MongoDBStats
from utils.db import init_db, get_database, close_mongo_connection
from utils.image_url_helpers import prepare_image_urls_for_frontend

def backup_file_stats():
    """
    Crear una copia de seguridad de los datos basados en archivos.
    
    Returns:
        tuple: (backup_dir, success)
    """
    try:
        # Crear directorio de backup
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        stats_dir = os.path.join(base_dir, 'stats')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f"{stats_dir}_backup_{timestamp}"
        
        if os.path.exists(stats_dir):
            print(f"Creando copia de seguridad de datos en: {backup_dir}")
            shutil.copytree(stats_dir, backup_dir)
            print("✅ Copia de seguridad creada exitosamente")
            return backup_dir, True
        else:
            print("⚠️ No se encontró el directorio de estadísticas para hacer backup")
            return None, False
    except Exception as e:
        print(f"❌ Error al crear copia de seguridad: {e}")
        return None, False

def verify_migration(file_stats, mongo_stats):
    """
    Verificar que la migración fue exitosa comparando los datos.
    
    Args:
        file_stats: Instancia de ClassificationStats
        mongo_stats: Instancia de MongoDBStats
        
    Returns:
        bool: True si la verificación fue exitosa
    """
    print("\nVerificando migración...")
    
    try:
        # Verificar estadísticas globales
        file_data = file_stats.get_stats(days=7)
        mongo_data = mongo_stats.get_stats(days=7)
        
        # Verificar total de clasificaciones
        if file_data['total_classifications'] != mongo_data['total_classifications']:
            print(f"❌ Discrepancia en total de clasificaciones: Archivo={file_data['total_classifications']}, MongoDB={mongo_data['total_classifications']}")
            return False
        
        # Verificar categorías
        file_categories = set(file_data['categories'].keys())
        mongo_categories = set(mongo_data['categories'].keys())
        
        if file_categories != mongo_categories:
            print(f"❌ Discrepancia en categorías: {file_categories} vs {mongo_categories}")
            return False
        
        # Verificar historial
        file_history = file_stats.get_classification_history(limit=5)
        mongo_history = mongo_stats.get_classification_history(limit=5)
        
        if len(file_history) != len(mongo_history):
            print(f"⚠️ Diferente número de elementos en el historial reciente: {len(file_history)} vs {len(mongo_history)}")
            # Esto puede ser normal si hay nuevas clasificaciones durante la migración
        
        # Verificar que los IDs estén presentes en MongoDB
        db = get_database()
        total_file_records = len([f for f in os.listdir(file_stats.history_dir) if f.endswith('.json')])
        total_mongo_records = db.classifications.count_documents({})
        
        print(f"📊 Registros en archivos: {total_file_records}")
        print(f"📊 Registros en MongoDB: {total_mongo_records}")
        
        if total_mongo_records < total_file_records * 0.9:  # Permitir hasta un 10% de diferencia
            print(f"⚠️ Posible pérdida de datos: MongoDB tiene solo {total_mongo_records} de {total_file_records} registros")
            return False
            
        print("✅ Verificación completada exitosamente")
        return True
    
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        return False

def migrate_to_mongodb(verify=True, backup=True):
    """
    Migrar datos de clasificación del almacenamiento basado en archivos a MongoDB.
    
    Args:
        verify: Si se debe verificar la migración después de completarla
        backup: Si se debe crear una copia de seguridad antes de migrar
        
    Returns:
        bool: True si la migración fue exitosa
    """
    print("=" * 80)
    print(" MIGRACIÓN DE DATOS A MONGODB ".center(80, "="))
    print("=" * 80)
    print("\nIniciando migración desde almacenamiento basado en archivos a MongoDB...")
    
    # Verificar configuración de MongoDB
    print("\n[1/6] Verificando configuración de MongoDB...")
    if not Config.MONGO_URI and not os.environ.get('MONGO_URL') and not os.environ.get('MONGO_PUBLIC_URL'):
        print("❌ No se ha configurado una URI de conexión para MongoDB")
        print("Por favor configura MONGO_URI, MONGO_URL o MONGO_PUBLIC_URL en el archivo .env")
        return False
    
    # Crear copia de seguridad si se solicitó
    backup_location = None
    if backup:
        print("\n[2/6] Creando copia de seguridad de datos...")
        backup_location, backup_success = backup_file_stats()
        if not backup_success and backup:
            response = input("⚠️ No se pudo crear la copia de seguridad. ¿Deseas continuar de todas formas? (s/N): ")
            if response.lower() != 's':
                print("Migración cancelada")
                return False
    else:
        print("\n[2/6] Copia de seguridad desactivada, saltando...")
    
    try:
        # Inicializar MongoDB
        print("\n[3/6] Inicializando conexión a MongoDB...")
        init_db()
        
        # Crear instancias de estadísticas
        print("\n[4/6] Preparando migración de datos...")
        file_stats = ClassificationStats()
        mongo_stats = MongoDBStats()
        
        # Realizar migración
        print("\n[5/6] Migrando datos a MongoDB...")
        start_time = time.time()
        success = mongo_stats.migrate_from_file_based(file_stats)
        end_time = time.time()
        
        if not success:
            print("❌ La migración falló. Revisa los logs para más detalles.")
            return False
        
        print(f"✅ Migración completada en {end_time - start_time:.2f} segundos")
        
        # Verificar migración si se solicitó
        if verify:
            print("\n[6/6] Verificando integridad de datos migrados...")
            verification_success = verify_migration(file_stats, mongo_stats)
            if not verification_success:
                print("⚠️ La verificación de la migración encontró discrepancias.")
                print("   Se recomienda revisar los datos y posiblemente reintentar la migración.")
                return False
        else:
            print("\n[6/6] Verificación desactivada, saltando...")
        
        print("\n" + "=" * 80)
        print(" MIGRACIÓN COMPLETADA EXITOSAMENTE ".center(80, "="))
        print("=" * 80)
        
        # Mostrar próximos pasos
        print("\nPróximos pasos:")
        print("1. Asegúrate de que DB_STORAGE_TYPE=mongodb esté configurado en tu archivo .env")
        if backup_location:
            print(f"2. Una vez que confirmes que todo funciona correctamente, puedes eliminar la copia de seguridad en: {backup_location}")
        print("3. Reinicia la aplicación para empezar a usar MongoDB")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cerrar conexión a MongoDB
        close_mongo_connection()

if __name__ == "__main__":
    # Analizar argumentos para opciones
    import argparse
    parser = argparse.ArgumentParser(description='Migrar datos a MongoDB')
    parser.add_argument('--no-verify', action='store_true', help='Omitir verificación post-migración')
    parser.add_argument('--no-backup', action='store_true', help='Omitir creación de copia de seguridad')
    parser.add_argument('--force', action='store_true', help='Forzar migración aunque DB_STORAGE_TYPE ya sea mongodb')
    args = parser.parse_args()
    
    # Verificar si ya está configurado para usar MongoDB
    if Config.DB_STORAGE_TYPE == 'mongodb' and not args.force:
        print("⚠️ Advertencia: DB_STORAGE_TYPE ya está configurado como 'mongodb'.")
        print("Esto podría causar duplicación de datos si ya has migrado anteriormente.")
        response = input("¿Deseas continuar de todas formas? (s/N): ")
        if response.lower() != 's':
            print("Migración cancelada")
            sys.exit(0)
    
    # Ejecutar migración
    success = migrate_to_mongodb(
        verify=not args.no_verify, 
        backup=not args.no_backup
    )
    
    # Salir con código apropiado
    sys.exit(0 if success else 1)
