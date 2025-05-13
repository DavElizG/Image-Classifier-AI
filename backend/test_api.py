#!/usr/bin/env python
"""
Script de prueba para el Clasificador de Imágenes con OpenAI.
Este script permite probar la API de clasificación enviando una imagen al servidor.
"""

import requests
import argparse
import os
import sys
import json
from datetime import datetime

def test_api_connectivity(base_url):
    """Prueba la conectividad básica con la API."""
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Conexión con la API exitosa")
            return True
        else:
            print(f"❌ Error al conectar con la API: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_openai_connection(base_url):
    """Prueba la conexión con la API de OpenAI."""
    try:
        response = requests.get(f"{base_url}/api/test-openai")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conexión con OpenAI exitosa: {data.get('model_response', '')}")
            return True
        else:
            print(f"❌ Error al conectar con OpenAI: {response.status_code}")
            print(response.json().get('message', 'No message provided'))
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def get_categories(base_url):
    """Obtiene las categorías disponibles para clasificación."""
    try:
        response = requests.get(f"{base_url}/api/categories")
        if response.status_code == 200:
            categories = response.json().get('categories', [])
            print(f"✅ Categorías disponibles: {', '.join(categories)}")
            return categories
        else:
            print(f"❌ Error al obtener categorías: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return []

def classify_image(base_url, image_path):
    """Clasifica una imagen utilizando la API."""
    if not os.path.exists(image_path):
        print(f"❌ Error: El archivo {image_path} no existe")
        return None
    
    try:
        with open(image_path, 'rb') as image_file:
            files = {'file': (os.path.basename(image_path), image_file, 'image/jpeg')}
            response = requests.post(f"{base_url}/api/classify", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Imagen clasificada como: {result.get('category', 'Unknown')}")
                print(f"   Confianza: {result.get('confidence', 0):.2f}%")
                return result
            else:
                print(f"❌ Error al clasificar imagen: {response.status_code}")
                print(response.json().get('error', 'No error message provided'))
                return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None

def get_stats(base_url, days=7):
    """Obtiene las estadísticas de clasificación."""
    try:
        response = requests.get(f"{base_url}/api/stats?days={days}")
        if response.status_code == 200:
            stats = response.json().get('stats', {})
            
            # Formatear y mostrar estadísticas
            print(f"✅ Estadísticas de clasificación:")
            print(f"   Total de clasificaciones: {stats.get('total_classifications', 0)}")
            
            # Mostrar estadísticas por categoría
            print("\n   Estadísticas por categoría:")
            categories = stats.get('categories', {})
            for category, data in categories.items():
                count = data.get('count', 0)
                avg_confidence = data.get('avg_confidence', 0)
                print(f"   - {category}: {count} imágenes (confianza promedio: {avg_confidence:.2f}%)")
            
            # Mostrar estadísticas diarias
            print("\n   Estadísticas diarias:")
            daily = stats.get('daily', {})
            for date, data in sorted(daily.items()):
                total = data.get('total', 0)
                if total > 0:  # Solo mostrar días con clasificaciones
                    print(f"   - {date}: {total} clasificaciones")
            
            # Mostrar fecha de última actualización
            last_updated = stats.get('last_updated', "")
            if last_updated:
                try:
                    # Convertir formato ISO a formato legible
                    dt = datetime.fromisoformat(last_updated)
                    formatted_date = dt.strftime("%d/%m/%Y %H:%M:%S")
                    print(f"\n   Última actualización: {formatted_date}")
                except ValueError:
                    print(f"\n   Última actualización: {last_updated}")
            
            return stats
        else:
            print(f"❌ Error al obtener estadísticas: {response.status_code}")
            error_msg = response.json().get('error', 'No error message provided')
            print(f"   {error_msg}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None

def get_history(base_url, limit=10, offset=0, category=None):
    """Obtiene el historial de clasificaciones con imágenes."""
    try:
        # Construir la URL con los parámetros
        url = f"{base_url}/api/history?limit={limit}&offset={offset}"
        if category:
            url += f"&category={category}"
        
        response = requests.get(url)
        if response.status_code == 200:
            history_data = response.json()
            history = history_data.get('history', [])
            
            # Mostrar información del historial
            print(f"\n✅ Historial de clasificaciones:")
            print(f"   Mostrando {len(history)} de {history_data.get('total', 0)} entradas")
            
            # Mostrar cada entrada del historial
            for i, entry in enumerate(history, 1):
                timestamp = entry.get('timestamp', '')
                try:
                    # Convertir formato ISO a formato legible
                    dt = datetime.fromisoformat(timestamp)
                    formatted_date = dt.strftime("%d/%m/%Y %H:%M:%S")
                except ValueError:
                    formatted_date = timestamp
                
                category = entry.get('category', 'desconocido')
                confidence = entry.get('confidence', 0)
                filename = entry.get('original_filename', 'desconocido')
                
                print(f"\n   {i}. {category} (confianza: {confidence:.2f}%)")
                print(f"      Archivo: {filename}")
                print(f"      Fecha: {formatted_date}")
                print(f"      ID: {entry.get('id', 'no-id')}")
                
                # Indicar que la imagen está disponible pero no mostrarla en consola
                if 'image_data' in entry:
                    print(f"      [Imagen disponible en base64]")
                else:
                    print(f"      [Imagen no disponible]")
            
            return history
        else:
            error_msg = response.json().get('error', 'No error message provided')
            print(f"❌ Error al obtener historial: {response.status_code} - {error_msg}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Prueba del Clasificador de Imágenes con OpenAI")
    parser.add_argument("--url", default="http://localhost:5000", help="URL base de la API")
    parser.add_argument("--image", help="Ruta a la imagen para clasificar")
    parser.add_argument("--stats", action="store_true", help="Obtener estadísticas de clasificación")
    parser.add_argument("--days", type=int, default=7, help="Número de días para estadísticas (1-30)")
    
    args = parser.parse_args()
    
    print("🔍 Probando el Clasificador de Imágenes con OpenAI")
    print(f"   URL de la API: {args.url}")
    
    # Probar conectividad
    if not test_api_connectivity(args.url):
        print("❌ No se pudo conectar con la API. Verificar que el servidor esté en ejecución.")
        sys.exit(1)
    
    # Probar conexión con OpenAI
    if not test_openai_connection(args.url):
        print("⚠️ La conexión con OpenAI falló. La clasificación de imágenes podría no funcionar.")
    
    # Obtener categorías disponibles
    categories = get_categories(args.url)
    if not categories:
        print("⚠️ No se pudieron obtener las categorías disponibles.")
      # Clasificar imagen si se proporcionó una
    if args.image:
        print(f"\n🖼️ Clasificando imagen: {args.image}")
        result = classify_image(args.url, args.image)
        if result:
            print("\n✅ Clasificación completa!")
    
    # Obtener estadísticas si se solicitaron
    if args.stats:
        print(f"\n📊 Obteniendo estadísticas de los últimos {args.days} días...")
        get_stats(args.url, args.days)
    
    # Si no se proporcionó ninguna acción, mostrar ayuda
    if not args.image and not args.stats:
        print("\n⚠️ No se proporcionó ninguna acción para realizar.")
        print("   Uso: python test_api.py --image ruta/a/la/imagen.jpg")
        print("   Uso: python test_api.py --stats [--days N]")

if __name__ == "__main__":
    main()
