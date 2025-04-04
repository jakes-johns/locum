from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from .db import db
from . import models  # Ensure models are registered

migrate = Migrate()  # Initialize migrate object

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = '278389u383uru83u84ui384uiojr3u3iu43i4uojioewri3irinu3i'  # Change to a secure key in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://locumdb_owner:npg_BAxjq7pys9aZ@ep-young-cherry-a5c19pys-pooler.us-east-2.aws.neon.tech/locumdb?sslmode=require'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    # Optional: Create tables (only in dev)
    with app.app_context():
        # db.create_all()
        pass

    return app  # ✅ Make sure this is outside the with block!
