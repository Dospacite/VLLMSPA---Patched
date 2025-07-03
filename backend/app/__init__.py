from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure CORS
    CORS(app, resources={
        r"/*": {
            "origins": app.config.get("CORS_ORIGINS", ["http://localhost:3000", "http://127.0.0.1:3000"]),
            "methods": app.config.get("CORS_METHODS", ["GET", "POST", "PUT", "DELETE", "OPTIONS"]),
            "allow_headers": app.config.get("CORS_ALLOW_HEADERS", ["Content-Type", "Authorization"])
        }
    })

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth_routes import auth_bp
    from app.routes.protected_routes import protected_bp
    from app.routes.ai_chat_routes import ai_chat_bp
    from app.routes.message_routes import message_bp
    from app.routes.feedback_routes import feedback_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(protected_bp)
    app.register_blueprint(ai_chat_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(feedback_bp)

    return app
