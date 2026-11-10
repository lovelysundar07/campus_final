from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import os
from werkzeug.utils import secure_filename
import bcrypt
from db import get_db

auth_bp = Blueprint('auth', __name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _redirect_by_role(role):
    if role == 'admin':
        return redirect(url_for('admin.dashboard'))
    if role == 'staff':
        return redirect(url_for('staff.dashboard'))
    return redirect(url_for('participant.dashboard'))


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return _redirect_by_role(session.get('user_role'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').encode('utf-8')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('auth/login.html')

        db  = get_db()
        cur = db.cursor()

        # 1. Check admins
        cur.execute("SELECT id, name, password_hash FROM admins WHERE email = %s", (email,))
        admin = cur.fetchone()
        if admin and bcrypt.checkpw(password, admin['password_hash'].encode()):
            cur.close()
            session.permanent = True
            session.update({'user_id': admin['id'], 'user_role': 'admin',
                            'user_name': admin['name'], 'user_email': email})
            flash(f"Welcome back, {admin['name']}!", 'success')
            return redirect(url_for('admin.dashboard'))

        # 2. Check staff
        cur.execute(
            "SELECT id, name, password_hash, is_approved, profile_image FROM staff "
            "WHERE email = %s AND is_active = TRUE", (email,))
        staff = cur.fetchone()
        if staff and bcrypt.checkpw(password, staff['password_hash'].encode()):
            cur.close()
            if not staff['is_approved']:
                flash('Your staff account is pending admin approval.', 'warning')
                return render_template('auth/login.html')
            session.permanent = True
            session.update({'user_id': staff['id'], 'user_role': 'staff',
                            'user_name': staff['name'], 'user_email': email, 'profile_image': staff.get('profile_image')})
            flash(f"Welcome, {staff['name']}!", 'success')
            return redirect(url_for('staff.dashboard'))

        # 3. Check participants
        cur.execute(
            "SELECT id, name, password_hash, profile_image FROM users "
            "WHERE email = %s AND is_active = TRUE", (email,))
        user = cur.fetchone()
        if user and bcrypt.checkpw(password, user['password_hash'].encode()):
            cur.close()
            session.permanent = True
            session.update({'user_id': user['id'], 'user_role': 'participant',
                            'user_name': user['name'], 'user_email': email, 'profile_image': user.get('profile_image')})
            flash(f"Welcome, {user['name']}!", 'success')
            return redirect(url_for('participant.dashboard'))

        cur.close()
        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


# ── Participant Registration ───────────────────────────────────────────────────

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        roll_no  = request.form.get('roll_no', '').strip()
        dept     = request.form.get('dept', '').strip()
        year_of_study = request.form.get('year_of_study', '').strip()
        if year_of_study not in ('First Year', 'Second Year', 'Third Year'):
            year_of_study = ''
        email    = request.form.get('email', '').strip().lower()
        phone    = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        profile_upload = request.files.get('profile_image')

        if not all([name, roll_no, dept, year_of_study, email, password]):
            flash('All required fields must be filled.', 'danger')
            return render_template('auth/register.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html')

        db  = get_db()
        cur = db.cursor()
        try:
            cur.execute("SELECT id FROM users WHERE email=%s OR roll_no=%s", (email, roll_no))
            if cur.fetchone():
                flash('An account with this email or roll number already exists.', 'danger')
                return render_template('auth/register.html')
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            profile_image = None
            if profile_upload and profile_upload.filename:
                ext = profile_upload.filename.rsplit('.', 1)[-1].lower() if '.' in profile_upload.filename else ''
                if ext not in {'png', 'jpg', 'jpeg', 'webp'}:
                    flash('Profile picture must be PNG, JPG, JPEG, or WEBP.', 'danger')
                    return render_template('auth/register.html')
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'profiles')
                os.makedirs(upload_dir, exist_ok=True)
                profile_image = f"participant_{secure_filename(roll_no)}.{ext}"
                profile_upload.save(os.path.join(upload_dir, profile_image))
            cur.execute(
                 "INSERT INTO users (name,roll_no,dept,section,year_of_study,email,phone,password_hash,profile_image) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (name, roll_no, dept, year_of_study, year_of_study, email, phone, pw_hash, profile_image))
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Registration failed: {e}', 'danger')
        finally:
            cur.close()

    return render_template('auth/register.html')


# ── Staff Self-Registration ───────────────────────────────────────────────────

@auth_bp.route('/staff/register', methods=['GET', 'POST'])
def staff_register():
    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        email       = request.form.get('email', '').strip().lower()
        phone       = request.form.get('phone', '').strip()
        designation = request.form.get('designation', '').strip()
        department  = request.form.get('department', '').strip()
        password    = request.form.get('password', '')
        confirm     = request.form.get('confirm_password', '')
        profile_upload = request.files.get('profile_image')

        if not all([name, email, password, designation, department]):
            flash('All required fields must be filled.', 'danger')
            return render_template('auth/staff_register.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/staff_register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/staff_register.html')

        db  = get_db()
        cur = db.cursor()
        try:
            cur.execute("SELECT id FROM staff WHERE email=%s", (email,))
            if cur.fetchone():
                flash('An account with this email already exists.', 'danger')
                return render_template('auth/staff_register.html')
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            profile_image = None
            if profile_upload and profile_upload.filename:
                ext = profile_upload.filename.rsplit('.', 1)[-1].lower() if '.' in profile_upload.filename else ''
                if ext not in {'png', 'jpg', 'jpeg', 'webp'}:
                    flash('Profile picture must be PNG, JPG, JPEG, or WEBP.', 'danger')
                    return render_template('auth/staff_register.html')
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'profiles')
                os.makedirs(upload_dir, exist_ok=True)
                profile_image = f"staff_{secure_filename(email)}.{ext}"
                profile_upload.save(os.path.join(upload_dir, profile_image))
            cur.execute(
                "INSERT INTO staff (name,email,phone,designation,department,password_hash,is_approved,profile_image) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (name, email, phone, designation, department, pw_hash, False, profile_image))
            flash('Staff registration submitted. Please wait for admin approval.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Registration failed: {e}', 'danger')
        finally:
            cur.close()

    return render_template('auth/staff_register.html')


# ── Logout ────────────────────────────────────────────────────────────────────

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


# ---------------------------------------------------------------------------
# Self-service profile editing
# ---------------------------------------------------------------------------
@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in to edit your profile.', 'warning')
        return redirect(url_for('auth.login'))
    role = session.get('user_role', 'participant')
    db = get_db()
    cur = db.cursor()
    table = 'staff' if role == 'staff' else ('admins' if role == 'admin' else 'users')
    cur.execute(f"SELECT * FROM {table} WHERE id=%s", (session['user_id'],))
    profile_data = cur.fetchone()
    if not profile_data:
        cur.close()
        session.clear()
        flash('Account not found. Please log in again.', 'danger')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        uploaded = request.files.get('profile_image')
        profile_image = profile_data.get('profile_image') if hasattr(profile_data, 'get') else None
        if uploaded and uploaded.filename:
            ext = uploaded.filename.rsplit('.', 1)[-1].lower() if '.' in uploaded.filename else ''
            if ext not in {'png', 'jpg', 'jpeg', 'webp'}:
                flash('Profile picture must be PNG, JPG, JPEG, or WEBP.', 'danger')
                cur.close()
                return redirect(url_for('auth.profile'))
            safe_name = secure_filename(uploaded.filename)
            filename = f"{role}_{session['user_id']}_{safe_name}"
            upload_dir = os.path.join(current_app.static_folder, 'uploads', 'profiles')
            os.makedirs(upload_dir, exist_ok=True)
            uploaded.save(os.path.join(upload_dir, filename))
            profile_image = filename
        if not name or not email:
            flash('Name and email are required.', 'danger')
        else:
            try:
                cur.execute(f"SELECT id FROM {table} WHERE email=%s AND id<>%s", (email, session['user_id']))
                if cur.fetchone():
                    flash('That email address is already in use.', 'danger')
                elif role == 'participant':
                    dept = request.form.get('dept', '').strip()
                    year = request.form.get('year_of_study', '').strip()
                    if year not in ('First Year', 'Second Year', 'Third Year'):
                        flash('Select a valid year of study (First, Second, or Third Year).', 'danger')
                        cur.close()
                        return redirect(url_for('auth.profile'))
                    cur.execute( "UPDATE users SET name=%s,email=%s,phone=%s,dept=%s,section=%s,year_of_study=%s,profile_image=%s WHERE id=%s",
                                (name,email,phone,dept,year,year,profile_image,session['user_id']))
                    session['user_name'] = name
                    session['user_email'] = email
                    session['profile_image'] = profile_image
                    flash('Profile updated successfully.', 'success')
                    cur.close()
                    return redirect(url_for('auth.profile'))
                elif role == 'staff':
                    dept = request.form.get('department', '').strip()
                    designation = request.form.get('designation', '').strip()
                    cur.execute("UPDATE staff SET name=%s,email=%s,phone=%s,department=%s,designation=%s,profile_image=%s WHERE id=%s",
                                (name,email,phone,dept,designation,profile_image,session['user_id']))
                    session['user_name'] = name
                    session['user_email'] = email
                    session['profile_image'] = profile_image
                    flash('Profile updated successfully.', 'success')
                    cur.close()
                    return redirect(url_for('auth.profile'))
                else:
                    cur.execute("UPDATE admins SET name=%s,email=%s WHERE id=%s", (name,email,session['user_id']))
                    session['user_name'] = name
                    session['user_email'] = email
                    session['profile_image'] = profile_image
                    flash('Profile updated successfully.', 'success')
                    cur.close()
                    return redirect(url_for('auth.profile'))
            except Exception:
                flash('Profile could not be updated. Check the entered details and try again.', 'danger')
    cur.close()
    return render_template('auth/profile.html', profile=profile_data, role=role)
