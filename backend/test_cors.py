#!/usr/bin/env python3
"""
Script para probar la configuración de CORS de la aplicación Flask
"""

import requests
import json
from config import Config

def test_cors_configuration():
    """Prueba la configuración de CORS"""
    
    # URL base de la aplicación (cambia según tu configuración)
    base_url = f"http://{Config.HOST}:{Config.PORT}"
    
    print(f"🔄 Probando configuración de CORS en: {base_url}")
    print("-" * 50)
    
    # Headers que simularán una petición desde el frontend
    test_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173", 
        "https://proyectofundweb.vercel.app"
    ]
    
    for origin in test_origins:
        print(f"\n🌐 Probando desde origen: {origin}")
        
        headers = {
            'Origin': origin,
            'Content-Type': 'application/json',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type, Authorization'
        }
        
        try:
            # Probar endpoint de health check
            print("  📍 Probando endpoint /health...")
            response = requests.get(f"{base_url}/health", headers=headers, timeout=10)
            print(f"     Status: {response.status_code}")
            print(f"     CORS Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("     ✅ Health check exitoso")
            else:
                print(f"     ❌ Health check falló: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"     ❌ Error de conexión: {e}")
            print("     💡 Asegúrate de que la aplicación esté ejecutándose")
    
    print("\n" + "=" * 50)
    print("🎯 Prueba de CORS completada")
    print("\n📋 Para usar este script:")
    print("1. Asegúrate de que la aplicación Flask esté ejecutándose")
    print("2. Ejecuta: python test_cors.py")

def test_endpoints():
    """Prueba endpoints básicos de la API"""
    base_url = f"http://{Config.HOST}:{Config.PORT}"
    
    endpoints_to_test = [
        "/",
        "/health", 
        "/api/categories",
        "/api/stats"
    ]
    
    print(f"\n🔍 Probando endpoints en: {base_url}")
    print("-" * 50)
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\n📍 Probando: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"     Status: {response.status_code}")
            
            if response.status_code == 200:
                print("     ✅ Endpoint disponible")
                # Mostrar respuesta para endpoints pequeños
                if len(response.text) < 500:
                    try:
                        data = response.json()
                        print(f"     Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    except:
                        print(f"     Respuesta: {response.text}")
            else:
                print(f"     ❌ Endpoint no disponible: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"     ❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("🚀 SCRIPT DE PRUEBA DE CORS Y ENDPOINTS")
    print("=" * 50)
    
    try:
        test_cors_configuration()
        test_endpoints()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
