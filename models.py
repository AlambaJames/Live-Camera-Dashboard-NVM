from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class AdminUser(UserMixin, db.Model):
    """Stores administrator accounts with role context and secure credentials."""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)        # e.g., "001"
    full_name = db.Column(db.String(100), nullable=False)                 # e.g., "John Doe"
    username = db.Column(db.String(64), unique=True, nullable=False)       # e.g., "jdoe"
    email = db.Column(db.String(120), unique=True, nullable=False)         # e.g., "j.doe@university.edu"
    office_position = db.Column(db.String(100), nullable=False)           # e.g., "Senior Network Engineer"
    password_hash = db.Column(db.String(256), nullable=False)              # Secure hashed password/PIN
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SystemSettings(db.Model):
    """Holds UI-configurable parameters for NVR hardware and storage retention."""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    nvr_ip = db.Column(db.String(50), default="10.10.10.8", nullable=False)
    rtsp_port = db.Column(db.Integer, default=554, nullable=False)
    nvr_username = db.Column(db.String(50), default="admin", nullable=False)
    nvr_password = db.Column(db.String(100), default="", nullable=False)
    retention_days = db.Column(db.Integer, default=30, nullable=False)
    storage_path = db.Column(db.String(255), default="./storage/recordings", nullable=False)


class ActivityLog(db.Model):
    """Records an audit trail stamped with the active admin's profile data."""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    admin_name = db.Column(db.String(100), nullable=False)       # Full name of the admin who performed the action
    office_position = db.Column(db.String(100), nullable=False)  # Position (e.g., "Network Intern")
    action_type = db.Column(db.String(50), nullable=False)       # e.g., "ADD_CAMERA", "UPDATE_CONFIG", "ADD_ADMIN"
    description = db.Column(db.String(255), nullable=False)      # Detailed description of what happened