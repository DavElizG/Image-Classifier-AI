from flask import Flask
from api.routes import api

app = Flask(__name__)

# Register the API blueprint
app.register_blueprint(api)

@app.route('/')
def home():
    return "Welcome to the Image Classifier API!"

if __name__ == '__main__':
    app.run(debug=True)