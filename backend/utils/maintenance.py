#!/usr/bin/env python
"""
Script para limpiar archivos de caché expirados del clasificador de imágenes.
Este script puede ser ejecutado manualmente o programado como una tarea cron/programada.
"""

import os
import sys
import argparse
from datetime import datetime

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.cache import ImageClassificationCache
from utils.stats import ClassificationStats

def clean_cache(verbose=False):
    """
    Limpia los archivos de caché expirados.
    
    Args:
        verbose: Si es True, muestra información detallada durante la limpieza
    
    Returns:
        int: Número de archivos eliminados
    """
    # Inicializar el cache
    cache = ImageClassificationCache()
    
    # Limpiar entradas expiradas
    if verbose:
        print(f"Limpiando archivos de caché expirados en {cache.cache_dir}...")
    
    count = cache.clear_expired()
    
    if verbose:
        if count > 0:
            print(f"✅ Se eliminaron {count} archivos de caché expirados.")
        else:
            print("✅ No se encontraron archivos de caché expirados para eliminar.")
    
    return count

def summarize_stats(verbose=False, days=30):
    """
    Muestra un resumen de las estadísticas de clasificación.
    
    Args:
        verbose: Si es True, muestra información detallada
        days: Número de días a incluir en el resumen
    """
    # Inicializar las estadísticas
    stats = ClassificationStats()
    
    # Obtener estadísticas
    stats_data = stats.get_stats(days=days)
    
    if verbose:
        print("\n📊 Resumen de Estadísticas de Clasificación:")
        print(f"   Total de clasificaciones: {stats_data['total_classifications']}")
        
        # Mostrar las categorías más populares
        categories = stats_data.get('categories', {})
        if categories:
            print("\n   Top categorías:")
            sorted_categories = sorted(
                categories.items(), 
                key=lambda x: x[1].get('count', 0), 
                reverse=True
            )
            
            for i, (category, data) in enumerate(sorted_categories[:5], 1):
                count = data.get('count', 0)
                avg_confidence = data.get('avg_confidence', 0)
                print(f"   {i}. {category}: {count} imágenes (confianza: {avg_confidence:.2f}%)")
        
        # Mostrar actividad reciente
        daily = stats_data.get('daily', {})
        if daily:
            print("\n   Actividad reciente:")
            sorted_days = sorted(daily.items(), reverse=True)
            total_recent = sum(day_data.get('total', 0) for _, day_data in sorted_days[:7])
            
            print(f"   Últimos 7 días: {total_recent} clasificaciones")
    
    return stats_data

def main():
    parser = argparse.ArgumentParser(description="Utilidad de mantenimiento para el Clasificador de Imágenes")
    parser.add_argument("--clean-cache", action="store_true", help="Limpiar archivos de caché expirados")
    parser.add_argument("--stats", action="store_true", help="Mostrar resumen de estadísticas")
    parser.add_argument("--days", type=int, default=30, help="Número de días para estadísticas (1-90)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostrar información detallada")
    
    args = parser.parse_args()
    
    # Si no se especificaron acciones, mostrar ayuda
    if not args.clean_cache and not args.stats:
        parser.print_help()
        return
    
    # Ejecutar acciones solicitadas
    if args.clean_cache:
        clean_cache(verbose=args.verbose)
    
    if args.stats:
        summarize_stats(verbose=args.verbose, days=min(max(args.days, 1), 90))
    
    if args.verbose:
        print("\n✅ Operaciones de mantenimiento completadas.")

if __name__ == "__main__":
    main()
