"""
Script de migración para ejecutar en Railway.
Este script debe copiarse al proyecto en Railway y ejecutarse allí.
"""
import os
import sys
import json
import time
from datetime import datetime
from utils.stats_new import ClassificationStats
from utils.mongodb_stats import MongoDBStats

def railway_migrate():
    """
    Migrar datos desde almacenamiento basado en archivos a MongoDB en Railway.
    """
    print("=" * 80)
    print(" MIGRACIÓN DE DATOS A MONGODB (RAILWAY) ".center(80, "="))
    print("=" * 80)
    
    # Verificar si estamos en Railway
    if not os.environ.get('RAILWAY_SERVICE_NAME'):
        print("⚠️ Este script está diseñado para ejecutarse en Railway.")
        print("Puedes continuar, pero es posible que no funcione correctamente.")
        
    try:
        print("\n[1/3] Preparando migración...")
        # Create file-based stats instance
        file_stats = ClassificationStats()
        
        # Create MongoDB stats instance
        mongo_stats = MongoDBStats()
        
        print("\n[2/3] Iniciando migración de datos...")
        start_time = time.time()
        
        # Migrate data
        success = mongo_stats.migrate_from_file_based(file_stats)
        
        end_time = time.time()
        
        if success:
            print(f"\n[3/3] ✅ Migración completada exitosamente en {end_time - start_time:.2f} segundos!")
            
            # Get stats to verify
            file_data = file_stats.get_stats(days=7)
            mongo_data = mongo_stats.get_stats(days=7)
            
            print("\nEstadísticas:")
            print(f"- Clasificaciones en archivo: {file_data['total_classifications']}")
            print(f"- Clasificaciones en MongoDB: {mongo_data['total_classifications']}")
            
            return True
        else:
            print("\n[3/3] ❌ La migración falló. Revisa los logs para más detalles.")
            return False
    
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = railway_migrate()
    sys.exit(0 if success else 1)
