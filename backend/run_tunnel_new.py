import subprocess
import time
import sys
import os
from pyngrok import ngrok, conf
from config import Config

def run_api_with_tunnel():
    # Configurar ngrok con el token guardado
    authtoken = "2x07Ob2Bc8YKYYU4dqafWKyzsdU_kCPMxzU8mBDeSDc7mrhj"
    print("Configurando ngrok con el authtoken guardado...")
    conf.get_default().auth_token = authtoken
    
    # Get the absolute path of app.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "app.py")
    
    # Start the Flask app as a subprocess
    flask_process = subprocess.Popen([sys.executable, app_path])
    
    # Give Flask time to start
    print("Starting Flask application...")
    time.sleep(3)
    
    # Get the port from Config (default 5000)
    port = 5000
    try:
        port = Config.PORT
    except:
        print("Couldn't read port from Config, using default 5000")
    
    # Start ngrok tunnel
    print(f"Starting ngrok tunnel to port {port}...")
    try:
        # Configurar para usar HTTPS con bind_tls=True
        http_tunnel = ngrok.connect(addr=f"http://localhost:{port}", bind_tls=True)
        public_url = http_tunnel.public_url
        
        print(f"✅ API now available at: {public_url}")
        print(f"✅ Swagger documentation available at: {public_url}/api/docs")
        print("Press CTRL+C to quit")
        
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Clean up on exit
        print("Closing tunnel and shutting down...")
        ngrok.kill()
        flask_process.terminate()
    except Exception as e:
        print(f"Error al crear el túnel: {str(e)}")
        ngrok.kill()
        flask_process.terminate()

if __name__ == "__main__":
    run_api_with_tunnel()
