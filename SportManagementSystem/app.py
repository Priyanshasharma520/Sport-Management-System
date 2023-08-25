from flask import Flask
from flask_smorest import Api
import os
from db import db
from flask_sqlalchemy import SQLAlchemy
from resources.event import blp as EventBlueprint
from resources.selection import blp as SelectionBlueprint
from resources.sport import blp as SportBlueprint
import models



def create_app(db_url=None):
    app = Flask(__name__)
    app.debug = True
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Sports REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config['SERVER_NAME'] = '127.0.0.1:5000'  # Replace with your actual host and port
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///new_data_10.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    api = Api(app)

    with app.app_context():
        db.create_all()
    
    api.register_blueprint(EventBlueprint)
    api.register_blueprint(SelectionBlueprint) 
    api.register_blueprint(SportBlueprint)
    
    return app