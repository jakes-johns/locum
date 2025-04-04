from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

# ------------------------------ USER MODEL ------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    _password = db.Column("password", db.String(255), nullable=False)  # Hidden attribute
    photo = db.Column(db.String(255), nullable=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    locums = db.relationship('Locum', backref='poster', lazy=True, cascade="all, delete")

    @property
    def password(self):
        """Remove this property to avoid AttributeError."""
        raise AttributeError("Password should not be directly accessed.")

    @password.setter
    def password(self, raw_password):
        """Auto-hash password on assignment."""
        self._password = generate_password_hash(raw_password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    def __repr__(self):
        return f"<User {self.name}>"

# ------------------------------ ADMIN MODEL ------------------------------
class Admin(db.Model):
    """Model representing administrators who manage users and locums."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    _password = db.Column("password", db.String(255), nullable=False)  # Hidden attribute

    @property
    def password(self):
        """Prevent direct password access."""
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, raw_password):
        """Auto-hash password on assignment."""
        self._password = generate_password_hash(raw_password)

    def check_password(self, password):
        """Check if the provided password matches the hashed password."""
        return check_password_hash(self._password, password)

    def __repr__(self):
        return f"<Admin {self.username}>"


# ------------------------------ LOCUM MODEL ------------------------------
class Locum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(150), nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='open', nullable=False)  # Now default is set in DB
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Locum {self.job_title} - {self.location}>"

