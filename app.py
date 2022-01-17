import os
import secrets
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from routes.authentication import authentication_router
from routes.files import files_router

load_dotenv()

app = Flask(__name__)

# CORS
# https://flask-cors.corydolphin.com/en/latest/api.html#extension
CORS(app)

# JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", default=secrets.token_hex())
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 72)))
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)

# Files Path
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploaded_files')
app.config['MAX_CONTENT_LENGTH'] = os.getenv('MAX_CONTENT_LENGTH', 16 * 1000 * 1000)

# Routes
app.register_blueprint(authentication_router, url_prefix='/auth')
app.register_blueprint(files_router, url_prefix='/files')

if __name__ == '__main__':
    # https://flask.palletsprojects.com/en/2.0.x/config/
    app.run(host=os.getenv('SERVER_HOSTNAME', default='localhost'), port=int(os.getenv('SERVER_PORT', default='8080')))
