import os
import secrets
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from database import mongo
from routes.authentication import authentication_router
from routes.files import files_router
from routes.instances import instances_router
from routes.mapping import mapping_router
from routes.ontology import ontology_router
from routes.users import users_router


def create_app():
    load_dotenv()

    app = Flask(__name__)

    # CORS
    # https://flask-cors.corydolphin.com/en/latest/api.html#extension
    CORS(app)

    # JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", default=secrets.token_hex())
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 72)))
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 30)))
    jwt = JWTManager(app)

    # MongoDB
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    mongo.init_app(app)

    # Routes
    app.register_blueprint(authentication_router, url_prefix='/auth')
    app.register_blueprint(files_router, url_prefix='/files')
    app.register_blueprint(instances_router, url_prefix='/instances')
    app.register_blueprint(users_router, url_prefix='/users')
    app.register_blueprint(ontology_router, url_prefix='/ontology')
    app.register_blueprint(mapping_router, url_prefix='/mapping')
    return app
