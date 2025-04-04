from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, current_app
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
# from app import db
from app.models import User, Locum, Admin
from .db import db

# Create a Blueprint for main routes
main = Blueprint('main', __name__)

# ======================== HOME ROUTE ========================
@main.route('/')
def home():
    """Redirect users to login if not authenticated, else show homepage."""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return render_template('home.html')

# ======================== AUTHENTICATION ========================
@main.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(name=name).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect(url_for('main.home'))

        flash("Invalid credentials", "danger")

    return render_template('login.html')


@main.route('/logout')
def logout():
    """Logs out the user."""
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles user registration."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        password = request.form.get('password')
        photo = request.files.get('photo')

        # Check if the username already exists
        existing_user = User.query.filter_by(name=name).first()
        
        if existing_user:
            flash("Username already exists, please choose a different one.", 'danger')
            return render_template('signup.html')

        # Hash the password
        # hashed_password = generate_password_hash(password)

        # Handle photo upload
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filename = photo.filename.replace("\\", "/")
        photo_path = os.path.join(upload_folder, filename)
        photo.save(photo_path)

        new_user = User(
            name=name,
            description=description,
            password=password,  # ✅ Let the model hash it
            photo=f"uploads/{filename}"
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful!", "success")
        return redirect(url_for('main.login'))

    return render_template('signup.html')


# ======================== ADMIN AUTHENTICATION ========================
@main.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    """Handles admin account creation."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            flash("Admin username already exists. Please choose another.", "danger")
            return render_template("admin_signup.html")

        # Create new admin and hash password via property
        new_admin = Admin(username=username)
        new_admin.password = password  # 🔐 Uses the setter to hash

        db.session.add(new_admin)
        db.session.commit()

        flash("Admin account created successfully. Please log in.", "success")
        return redirect(url_for("main.admin_login"))

    return render_template("admin_signup.html")


@main.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """Handles admin login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            flash('Admin login successful', 'success')
            return redirect(url_for('main.admin_dashboard'))

        flash('Invalid credentials', 'danger')

    return render_template('admin_login.html')


@main.route('/admin_logout')
def admin_logout():
    """Logs out the admin."""
    session.pop('admin_id', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('main.admin_login'))


# ======================== ADMIN DASHBOARD ========================
@main.route('/admin_dashboard')
def admin_dashboard():
    """Admin dashboard to manage users and locums."""
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    users = User.query.all()
    locums = Locum.query.all()

    return render_template('admin_dashboard.html', users=users, locums=locums)


# ======================== USER MANAGEMENT ========================
@main.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Allows admin to delete a user."""
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')

    return redirect(url_for('main.admin_dashboard'))


@main.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """Allows admin to edit user details."""
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    user = User.query.get(user_id)

    if request.method == 'POST':
        user.name = request.form['name']
        user.description = request.form['description']

        db.session.commit()

        flash('User details updated', 'success')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('edit_user.html', user=user)

@main.route('/mark_settled/<int:locum_id>', methods=['POST'])
def mark_settled(locum_id):
    locum = Locum.query.get_or_404(locum_id)
    
    if locum.user_id != session['user_id']:
        return 'You do not have permission to mark this locum as settled.', 403

    locum.status = 'settled'
    db.session.commit()
    return redirect(url_for('main.booked_locums'))


# ======================== LOCUM MANAGEMENT ========================
@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@main.route('/manage_locum')
def manage_locum():
    return render_template('manage_locum.html')

@main.route('/create_locum', methods=['GET', 'POST'])
def create_locum():
    """Allows authenticated users to create locum job listings."""
    if 'user_id' not in session:
        flash("You must be logged in to create a locum.", "danger")
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        new_locum = Locum(
            job_title=request.form['job_title'],
            requirements=request.form['requirements'],
            job_description=request.form['job_description'],
            location=request.form['location'],
            hourly_rate=float(request.form['hourly_rate']),
            start_time=datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M'),
            end_time=datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M'),
            user_id=session['user_id']
        )

        db.session.add(new_locum)
        db.session.commit()

        flash("Locum created successfully!", "success")
        return redirect(url_for('main.available_locums'))

    return render_template('create_locum.html')


@main.route('/available_locums')
def available_locums():
    """Displays all available locum jobs."""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    locums = Locum.query.filter_by(status='open').all()

    return render_template('available_locums.html', locums=locums)

@main.route('/booked_locums')
def booked_locums():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    locums = Locum.query.filter_by(status='booked').all()  # Get all locums that are booked
    return render_template('booked_locums.html', locums=locums)


@main.route('/settled_locums')
def settled_locums():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    locums = Locum.query.filter_by(status='settled').all()  # Get all locums that are settled
    return render_template('settled_locums.html', locums=locums)


@main.route('/book_locum/<int:locum_id>', methods=['POST'])
def book_locum(locum_id):
    """Allows users to book an available locum job."""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    locum = Locum.query.get(locum_id)
    if locum and locum.status == 'open':
        locum.status = 'booked'
        db.session.commit()

    return redirect(url_for('main.available_locums'))


@main.route('/profile')
def profile():
    """Displays user profile."""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('main.login'))

    return render_template('profile.html', user=user)


@main.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """Allow logged-in users to change their password."""
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not user.check_password(current_password):
            flash("Current password is incorrect.", "danger")
        elif new_password != confirm_password:
            flash("New passwords do not match.", "danger")
        else:
            user.password = new_password  # will auto-hash
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for('main.profile'))

    return render_template('change_password.html')


# ======================== STATIC PAGES ========================
@main.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html')
