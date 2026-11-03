from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from models import db, AdminUser, SystemSettings, ActivityLog

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-campus-vms-secure-secret-key'  # Change this to a secure random key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions with app
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

# Helper function to log audit events automatically
def log_activity(action_type, description):
    if current_user.is_authenticated:
        log = ActivityLog(
            admin_name=current_user.full_name,
            office_position=current_user.office_position,
            action_type=action_type,
            description=description
        )
        db.session.add(log)
        db.session.commit()

# --- ROUTES ---

@app.route('/')
@login_required
def dashboard():
    # Fetch system health metrics & settings for display
    settings = SystemSettings.query.first()
    return render_template('dashboard.html', settings=settings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password/PIN.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    config = SystemSettings.query.first()
    if not config:
        config = SystemSettings()
        db.session.add(config)
        db.session.commit()

    if request.method == 'POST':
        config.retention_days = int(request.form.get('retention_days', 30))
        config.storage_path = request.form.get('storage_path', './storage/recordings')
        config.nvr_ip = request.form.get('nvr_ip')
        config.rtsp_port = int(request.form.get('rtsp_port', 554))
        config.nvr_username = request.form.get('nvr_username')
        
        new_pass = request.form.get('nvr_password')
        if new_pass:
            config.nvr_password = new_pass
            
        db.session.commit()
        log_activity("UPDATE_CONFIG", "Updated system and NVR hardware configurations.")
        flash('System configuration updated successfully.', 'success')
        return redirect(url_for('settings'))

    return render_template('settings.html', config=config)

@app.route('/admins', methods=['GET', 'POST'])
@login_required
def manage_admins():
    if request.method == 'POST':
        action = request.form.get('action')
        admin_password = request.form.get('admin_password')
        
        # Privileged Action Verification: Require current admin's password
        if not current_user.check_password(admin_password):
            flash('Privileged Action Denied: Incorrect password verification.', 'danger')
            return redirect(url_for('manage_admins'))
            
        if action == 'add':
            staff_id = request.form.get('staff_id')
            full_name = request.form.get('full_name')
            username = request.form.get('username')
            email = request.form.get('email')
            office_position = request.form.get('office_position')
            password = request.form.get('password')
            
            new_admin = AdminUser(
                staff_id=staff_id,
                full_name=full_name,
                username=username,
                email=email,
                office_position=office_position
            )
            new_admin.set_password(password)
            db.session.add(new_admin)
            db.session.commit()
            
            log_activity("ADD_ADMIN", f"Added new administrator account for {full_name} ({office_position}).")
            flash(f'Administrator {full_name} added successfully.', 'success')
            
        elif action == 'delete':
            admin_id = request.form.get('admin_id')
            admin_to_delete = AdminUser.query.get(admin_id)
            if admin_to_delete:
                if admin_to_delete.id == current_user.id:
                    flash('You cannot delete your own active account.', 'warning')
                else:
                    db.session.delete(admin_to_delete)
                    db.session.commit()
                    log_activity("REMOVE_ADMIN", f"Removed administrator ID {admin_id}.")
                    flash('Administrator removed successfully.', 'success')
                    
        return redirect(url_for('manage_admins'))

    admins = AdminUser.query.all()
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(50).all()
    return render_template('admins.html', admins=admins, logs=logs)

# Database initialization setup
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create a default admin account if none exists
        if not AdminUser.query.first():
            default_admin = AdminUser(
                staff_id="001",
                full_name="Simon James",
                username="simon",
                email="simon@university.edu",
                office_position="Senior Network Engineer"
            )
            default_admin.set_password("admin123")
            db.session.add(default_admin)
            db.session.commit()
            print("Default admin created: username 'simon' / password 'admin123'")
            
    app.run(host='0.0.0.0', port=5000, debug=True)