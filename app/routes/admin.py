from db import get_db
import os
import json
from datetime import datetime
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, current_app, jsonify, send_file)
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)





# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------

def admin_required():
    if session.get('user_role') != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    return None


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@admin_bp.route('/')
def dashboard():
    guard = admin_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT COUNT(*) AS cnt FROM events")
    total_events = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) AS cnt FROM registrations")
    total_registrations = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) AS cnt FROM staff WHERE is_approved = FALSE")
    pending_staff = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) AS cnt FROM events WHERE event_date >= CURDATE() AND status = 'upcoming'")
    upcoming_events = cur.fetchone()['cnt']

    cur.execute(
        "SELECT e.*, COUNT(r.id) AS reg_count FROM events e "
        "LEFT JOIN registrations r ON e.id = r.event_id "
        "GROUP BY e.id ORDER BY e.event_date DESC LIMIT 5"
    )
    recent_events = cur.fetchall()

    cur.close()
    return render_template('admin/dashboard.html',
                           total_events=total_events,
                           total_registrations=total_registrations,
                           pending_staff=pending_staff,
                           upcoming_events=upcoming_events,
                           recent_events=recent_events)


# ---------------------------------------------------------------------------
# Events – Create
# ---------------------------------------------------------------------------

@admin_bp.route('/events/create', methods=['GET', 'POST'])
def create_event():
    guard = admin_required()
    if guard:
        return guard

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        event_type = request.form.get('event_type', '').strip().lower() or 'workshop'
        if event_type == 'other':
            custom_type = request.form.get('custom_event_type', '').strip().lower()
            custom_type = ''.join(ch for ch in custom_type if ch.isalnum() or ch in (' ', '-', '_')).strip()[:50]
            event_type = custom_type or 'other'
        elif event_type not in ('workshop', 'seminar', 'symposium'):
            event_type = 'workshop'
        description = request.form.get('description', '').strip()
        event_date = request.form.get('event_date', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        venue = request.form.get('venue', '').strip()
        try:
            capacity = int(request.form.get('capacity') or 100)
        except Exception:
            capacity = 100
        registration_deadline = request.form.get('registration_deadline', '').strip() or None
        is_published = True if request.form.get('is_published', '1') in ('1', 'true', 'on') else False

        if not all([title, event_type, event_date, start_time, end_time, venue]):
            flash('Please fill all required fields.', 'danger')
            return render_template('admin/create_event.html')

        # Handle banner upload
        banner_image = None
        banner_file = request.files.get('banner_image') or request.files.get('banner')
        if banner_file and banner_file.filename:
            ext = banner_file.filename.rsplit('.', 1)[-1].lower()
            if ext in current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'}):
                filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{banner_file.filename}")
                banner_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners', filename)
                banner_file.save(banner_path)
                banner_image = filename

        db = get_db()
        cur = db.cursor()

        try:
            cur.execute(
                "INSERT INTO events (title, event_type, description, event_date, start_time, end_time, "
                "venue, capacity, registration_deadline, banner_image, is_published, created_by) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (title, event_type, description, event_date, start_time, end_time,
                 venue, capacity, registration_deadline, banner_image, is_published, session['user_id'])
            )
            event_id = cur.lastrowid

            # Save sub-events for symposium
            if event_type == 'symposium':
                sub_names = request.form.getlist('sub_event_name[]')
                sub_descs = request.form.getlist('sub_event_desc[]')
                sub_venues = request.form.getlist('sub_event_venue[]')
                sub_teams = request.form.getlist('sub_event_allowed_teams[]')
                sub_mins  = request.form.getlist('sub_event_min_team[]')
                sub_maxs  = request.form.getlist('sub_event_max_team[]')

                for i, sname in enumerate(sub_names):
                    if not sname.strip():
                        continue
                    cur.execute(
                        "INSERT INTO sub_events (event_id, name, description, allowed_teams, min_team_size, max_team_size, venue) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (event_id,
                         sname.strip(),
                         sub_descs[i].strip() if i < len(sub_descs) else '',
                         int(sub_teams[i]) if i < len(sub_teams) and sub_teams[i] else 10,
                         int(sub_mins[i]) if i < len(sub_mins) and sub_mins[i] else 1,
                         int(sub_maxs[i]) if i < len(sub_maxs) and sub_maxs[i] else 4,
                         sub_venues[i].strip() if i < len(sub_venues) and sub_venues[i].strip() else None)
                    )
            if is_published:
                cur.execute("INSERT INTO notifications (user_id, title, message) "
                            "SELECT id, %s, %s FROM users WHERE is_active=TRUE",
                            ('New event published', f'{title} has been published. Open the events page for details.'))
            flash('Event created successfully!', 'success')
            cur.close()
            return redirect(url_for('admin.events_list'))
        except Exception as e:
            flash(f'Failed to create event: {str(e)}', 'danger')
            cur.close()

    return render_template('admin/create_event.html')


# ---------------------------------------------------------------------------
# Events – List
# ---------------------------------------------------------------------------

@admin_bp.route('/events')
def events_list():
    guard = admin_required()
    if guard:
        return guard

    event_type = request.args.get('type', '')
    status = request.args.get('status', '')

    db = get_db()
    cur = db.cursor()

    query = ("SELECT e.*, COUNT(r.id) AS reg_count FROM events e "
             "LEFT JOIN registrations r ON e.id = r.event_id")
    conditions = []
    params = []

    if event_type:
        conditions.append("e.event_type = %s")
        params.append(event_type)
    if status:
        conditions.append("e.status = %s")
        params.append(status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " GROUP BY e.id ORDER BY e.event_date DESC"

    cur.execute(query, params)
    events = cur.fetchall()
    cur.close()

    return render_template('admin/manage_events.html', events=events,
                           filter_type=event_type, filter_status=status)


# ---------------------------------------------------------------------------
# Events – Edit
# ---------------------------------------------------------------------------

@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    guard = admin_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()
    if not event:
        flash('Event not found.', 'danger')
        cur.close()
        return redirect(url_for('admin.events_list'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        event_type = request.form.get('event_type', '').strip().lower()
        if event_type == 'other':
            custom_type = request.form.get('custom_event_type', '').strip().lower()
            custom_type = ''.join(ch for ch in custom_type if ch.isalnum() or ch in (' ', '-', '_')).strip()[:50]
            event_type = custom_type or 'other'
        elif not event_type:
            event_type = (event.get('event_type') or 'other').lower()
        elif event_type not in ('workshop', 'seminar', 'symposium'):
            event_type = ''.join(ch for ch in event_type if ch.isalnum() or ch in (' ', '-', '_')).strip()[:50] or 'other'
        description = request.form.get('description', '').strip()
        event_date = request.form.get('event_date', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        venue = request.form.get('venue', '').strip()
        capacity = request.form.get('capacity', 100)
        registration_deadline = request.form.get('registration_deadline', '').strip() or None
        status = request.form.get('status', 'upcoming')

        banner_image = event['banner_image']
        if 'banner' in request.files:
            banner = request.files['banner']
            if banner and banner.filename:
                ext = banner.filename.rsplit('.', 1)[-1].lower()
                if ext in current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'}):
                    filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{banner.filename}")
                    banner_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners', filename)
                    banner.save(banner_path)
                    banner_image = f"uploads/banners/{filename}"

        try:
            cur.execute(
                "UPDATE events SET title=%s, event_type=%s, description=%s, event_date=%s, "
                "start_time=%s, end_time=%s, venue=%s, capacity=%s, registration_deadline=%s, "
                "banner_image=%s, status=%s WHERE id=%s",
                (title, event_type, description, event_date, start_time, end_time,
                 venue, capacity, registration_deadline, banner_image, status, event_id)
            )
            flash('Event updated successfully!', 'success')
            cur.close()
            return redirect(url_for('admin.events_list'))
        except Exception as e:
            flash(f'Update failed: {str(e)}', 'danger')

    cur.execute("SELECT * FROM sub_events WHERE event_id = %s", (event_id,))
    sub_events = cur.fetchall()
    cur.close()
    return render_template('admin/edit_event.html', event=event, sub_events=sub_events)



# ---------------------------------------------------------------------------
# Edit symposium sub-event details and assign responsible staff
# ---------------------------------------------------------------------------
@admin_bp.route('/sub-events/<int:sub_event_id>/edit', methods=['GET', 'POST'])
def edit_sub_event(sub_event_id):
    guard = admin_required()
    if guard:
        return guard
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT se.*, e.title AS symposium_title, e.id AS parent_event_id "
                "FROM sub_events se JOIN events e ON e.id=se.event_id WHERE se.id=%s",
                (sub_event_id,))
    sub_event = cur.fetchone()
    if not sub_event:
        cur.close()
        flash('Sub-event not found.', 'danger')
        return redirect(url_for('admin.events_list'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        venue = request.form.get('venue', '').strip()
        description = request.form.get('description', '').strip()
        allowed_teams = max(1, int(request.form.get('allowed_teams') or 10))
        min_team_size = max(1, int(request.form.get('min_team_size') or 1))
        max_team_size = max(min_team_size, int(request.form.get('max_team_size') or 4))
        staff_ids = request.form.getlist('staff_ids')
        if not name:
            flash('Sub-event name is required.', 'danger')
        else:
            cur.execute("UPDATE sub_events SET name=%s, venue=%s, description=%s, allowed_teams=%s, "
                        "min_team_size=%s, max_team_size=%s WHERE id=%s",
                        (name, venue or None, description, allowed_teams, min_team_size, max_team_size, sub_event_id))
            cur.execute("DELETE FROM sub_event_staff WHERE sub_event_id=%s", (sub_event_id,))
            for staff_id in staff_ids:
                try:
                    selected_staff_id = int(staff_id)
                    cur.execute("INSERT IGNORE INTO sub_event_staff (sub_event_id, staff_id) VALUES (%s,%s)",
                                (sub_event_id, selected_staff_id))
                    # The existing staff dashboard authorizes at event level, so ensure the
                    # assigned sub-event staff member can open the parent event workspace.
                    cur.execute("INSERT IGNORE INTO event_incharge (event_id, staff_id) VALUES (%s,%s)",
                                (sub_event['parent_event_id'], selected_staff_id))
                except (TypeError, ValueError):
                    continue
            cur.close()
            flash('Sub-event updated and staff assignments saved.', 'success')
            return redirect(url_for('admin.edit_event', event_id=sub_event['parent_event_id']))
    cur.execute("SELECT id, name, department, designation FROM staff WHERE is_active=TRUE AND is_approved=TRUE ORDER BY name")
    staff_list = cur.fetchall()
    cur.execute("SELECT staff_id FROM sub_event_staff WHERE sub_event_id=%s", (sub_event_id,))
    assigned_ids = {row['staff_id'] for row in cur.fetchall()}
    cur.close()
    return render_template('admin/edit_sub_event.html', sub_event=sub_event,
                           staff_list=staff_list, assigned_ids=assigned_ids)


# ---------------------------------------------------------------------------
# Events – Publish Toggle
# ---------------------------------------------------------------------------

@admin_bp.route('/events/<int:event_id>/publish', methods=['POST'])
def toggle_publish(event_id):
    guard = admin_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT is_published FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()
    if event:
        new_status = not event['is_published']
        cur.execute("UPDATE events SET is_published = %s WHERE id = %s", (new_status, event_id))
        if new_status:
            cur.execute("SELECT title FROM events WHERE id=%s", (event_id,))
            published = cur.fetchone()
            cur.execute("INSERT INTO notifications (user_id, title, message) "
                        "SELECT id, %s, %s FROM users WHERE is_active=TRUE",
                        ('New event published', f"{published['title']} is now open. Visit the events page for details."))
        state = 'published' if new_status else 'unpublished'
        flash(f'Event {state} successfully.', 'success')
    else:
        flash('Event not found.', 'danger')

    cur.close()
    return redirect(url_for('admin.events_list'))


# ---------------------------------------------------------------------------
# Events – Delete
# ---------------------------------------------------------------------------

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    guard = admin_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
        flash('Event deleted successfully.', 'success')
    except Exception as e:
        flash(f'Delete failed: {str(e)}', 'danger')

    cur.close()
    return redirect(url_for('admin.events_list'))


# ---------------------------------------------------------------------------
# Events – Registrations
# ---------------------------------------------------------------------------

@admin_bp.route('/events/<int:event_id>/registrations')
def event_registrations(event_id):
    guard = admin_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()
    if not event:
        flash('Event not found.', 'danger')
        cur.close()
        return redirect(url_for('admin.events_list'))

    cur.execute(
        "SELECT r.*, u.name AS user_name, u.name AS participant_name, u.roll_no, u.dept, u.section, u.email, u.phone, "
        "se.name AS sub_event_name, "
        "c.certificate_number, c.certificate_path "
        "FROM registrations r "
        "JOIN users u ON r.user_id = u.id "
        "LEFT JOIN sub_events se ON r.sub_event_id = se.id "
        "LEFT JOIN certificates c ON r.id = c.registration_id "
        "WHERE r.event_id = %s ORDER BY r.registered_at DESC",
        (event_id,)
    )
    registrations = cur.fetchall()

    # For symposium, get team members
    for reg in registrations:
        if event['event_type'] == 'symposium':
            cur.execute("SELECT * FROM team_members WHERE registration_id = %s", (reg['id'],))
            reg['team_members'] = cur.fetchall()

    cur.close()
    return render_template('admin/registrations.html', event=event, registrations=registrations)



# ---------------------------------------------------------------------------
# Export registered participant list as printable PDF
# ---------------------------------------------------------------------------
@admin_bp.route('/events/<int:event_id>/registrations/pdf')
def registrations_pdf(event_id):
    guard = admin_required()
    if guard:
        return guard
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM events WHERE id=%s", (event_id,))
    event = cur.fetchone()
    if not event:
        cur.close()
        flash('Event not found.', 'danger')
        return redirect(url_for('admin.events_list'))
    cur.execute("SELECT r.id, u.name AS user_name, u.name AS participant_name, u.roll_no, u.dept, "
                "u.section, u.email, u.phone, r.attendance_status, r.registered_at, "
                "se.name AS sub_event_name FROM registrations r JOIN users u ON u.id=r.user_id "
                "LEFT JOIN sub_events se ON se.id=r.sub_event_id WHERE r.event_id=%s ORDER BY u.name",
                (event_id,))
    participants = cur.fetchall()
    cur.close()
    from services.report_service import generate_event_report
    present = sum(1 for p in participants if p.get('attendance_status') == 'present')
    stats = {'total': len(participants), 'present': present,
             'absent': sum(1 for p in participants if p.get('attendance_status') == 'absent'),
             'pending': sum(1 for p in participants if p.get('attendance_status') == 'pending')}
    path = generate_event_report(event_id, event, participants, stats, current_app.config['REPORT_FOLDER'])
    return send_file(path, as_attachment=True, download_name=f"MSV_{event_id}_registered_participants.pdf",
                     mimetype='application/pdf')


# ---------------------------------------------------------------------------
# Certificates – Issue
# ---------------------------------------------------------------------------

@admin_bp.route('/certificates/issue', methods=['POST'])
def issue_certificates():
    guard = admin_required()
    if guard:
        return guard

    reg_ids = request.form.getlist('registration_ids') or request.form.getlist('registration_ids[]')
    if not reg_ids:
        flash('No registrations selected.', 'warning')
        return redirect(request.referrer or url_for('admin.events_list'))

    db = get_db()
    cur = db.cursor()

    from services.certificate_service import generate_certificate
    cert_folder = current_app.config['CERT_FOLDER']
    issued_count = 0

    for reg_id in reg_ids:
        try:
            cur.execute(
                "SELECT r.*, u.name AS participant_name, e.title AS event_name, "
                "e.event_date, e.event_type, e.id AS event_id "
                "FROM registrations r "
                "JOIN users u ON r.user_id = u.id "
                "JOIN events e ON r.event_id = e.id "
                "WHERE r.id = %s",
                (reg_id,)
            )
            reg = cur.fetchone()
            if not reg or reg['certificate_issued']:
                continue

            # Workshop certificate eligibility: 75% of recorded daily sessions.
            if reg['event_type'] == 'workshop':
                cur.execute("SELECT COUNT(*) AS total FROM workshop_sessions WHERE event_id=%s", (reg['event_id'],))
                session_total = cur.fetchone()['total']
                if session_total:
                    cur.execute("SELECT COUNT(*) AS present FROM session_attendance sa "
                                "JOIN workshop_sessions ws ON ws.id=sa.session_id "
                                "WHERE ws.event_id=%s AND sa.registration_id=%s "
                                "AND sa.attendance_status='present'", (reg['event_id'], reg_id))
                    present_total = cur.fetchone()['present']
                    if (present_total / session_total) < 0.75:
                        continue
                elif reg['attendance_status'] != 'present':
                    continue

            # PPT achievement certificates require at least one staff score and 60% average.
            if reg['event_type'] == 'seminar' and reg.get('ppt_file_path'):
                cur.execute("SELECT AVG(score / max_score * 100) AS pct, COUNT(*) AS evaluations "
                            "FROM presentation_scores WHERE registration_id=%s", (reg_id,))
                score_row = cur.fetchone()
                if not score_row or not score_row['evaluations'] or float(score_row['pct'] or 0) < 60:
                    continue

            cur.execute("SELECT GROUP_CONCAT(DISTINCT s.name ORDER BY s.name SEPARATOR ', ') AS coordinator_names "
                        "FROM event_incharge ei JOIN staff s ON s.id=ei.staff_id WHERE ei.event_id=%s", (reg['event_id'],))
            coordinator_row = cur.fetchone() or {}
            coordinator_names = coordinator_row.get('coordinator_names') or 'Event Coordination Team'
            cert_path, cert_number = generate_certificate(
                registration_id=int(reg_id),
                participant_name=reg['participant_name'],
                event_name=reg['event_name'],
                event_date=str(reg['event_date']),
                event_type=reg['event_type'],
                cert_folder=cert_folder,
                logo_path=os.path.join(current_app.static_folder, 'images', 'ms-college-logo.png'),
                coordinating_staff=coordinator_names
            )

            cert_filename = os.path.basename(cert_path)
            # Save certificate record
            cur.execute(
                "INSERT INTO certificates (registration_id, certificate_path, certificate_number, issued_by) "
                "VALUES (%s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE certificate_path=%s, certificate_number=%s, issued_by=%s",
                (reg_id, cert_filename, cert_number, session['user_id'],
                 cert_filename, cert_number, session['user_id'])
            )
            cur.execute(
                "UPDATE registrations SET certificate_issued = TRUE WHERE id = %s", (reg_id,)
            )

            # Notify participant
            cur.execute(
                "INSERT INTO notifications (user_id, title, message) VALUES (%s, %s, %s)",
                (reg['user_id'],
                 'Certificate Issued',
                 f"Your certificate for '{reg['event_name']}' is ready. Cert #: {cert_number}")
            )
            issued_count += 1
        except Exception as e:
            continue
    cur.close()
    flash(f'{issued_count} certificate(s) issued successfully.', 'success')
    return redirect(request.referrer or url_for('admin.events_list'))


# ---------------------------------------------------------------------------
# Staff Requests
# ---------------------------------------------------------------------------

@admin_bp.route('/staff/requests')
def staff_requests():
    guard = admin_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM staff WHERE is_approved = FALSE ORDER BY created_at DESC")
    pending = cur.fetchall()
    cur.execute("SELECT * FROM staff WHERE is_approved = TRUE ORDER BY is_active DESC, name")
    approved = cur.fetchall()
    cur.close()
    return render_template('admin/staff_requests.html', pending_staff=pending, approved_staff=approved)


@admin_bp.route('/staff/approve/<int:staff_id>', methods=['POST'])
def approve_staff(staff_id):
    guard = admin_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("UPDATE staff SET is_approved = TRUE WHERE id = %s", (staff_id,))
        flash('Staff approved successfully.', 'success')
    except Exception as e:
        flash(f'Approval failed: {str(e)}', 'danger')

    cur.close()
    return redirect(url_for('admin.staff_requests'))


@admin_bp.route('/staff/reject/<int:staff_id>', methods=['POST'])
def reject_staff(staff_id):
    guard = admin_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("DELETE FROM staff WHERE id = %s AND is_approved = FALSE", (staff_id,))
        flash('Staff request rejected and removed.', 'success')
    except Exception as e:
        flash(f'Rejection failed: {str(e)}', 'danger')

    cur.close()
    return redirect(url_for('admin.staff_requests'))


@admin_bp.route('/staff/<int:staff_id>/toggle-active', methods=['POST'])
def toggle_staff_active(staff_id):
    """Temporarily pause or reactivate an approved staff account."""
    guard = admin_required()
    if guard:
        return guard
    db = get_db(); cur = db.cursor()
    try:
        cur.execute("UPDATE staff SET is_active = NOT is_active WHERE id=%s AND is_approved=TRUE", (staff_id,))
        if cur.rowcount:
            cur.execute("SELECT is_active FROM staff WHERE id=%s", (staff_id,))
            active = bool(cur.fetchone()['is_active'])
            flash('Staff account reactivated.' if active else 'Staff account temporarily paused.', 'success' if active else 'warning')
        else:
            flash('Approved staff member not found.', 'warning')
    except Exception as e:
        flash(f'Could not update staff status: {e}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('admin.staff_requests'))


@admin_bp.route('/staff/<int:staff_id>/remove', methods=['POST'])
def remove_staff(staff_id):
    """Remove staff from active work without deleting historical event records."""
    guard = admin_required()
    if guard:
        return guard
    db = get_db(); cur = db.cursor()
    try:
        cur.execute("UPDATE staff SET is_active=FALSE WHERE id=%s", (staff_id,))
        cur.execute("DELETE FROM event_incharge WHERE staff_id=%s", (staff_id,))
        cur.execute("DELETE FROM sub_event_staff WHERE staff_id=%s", (staff_id,))
        flash('Staff access removed and current assignments cleared. Historical records were retained.', 'success')
    except Exception as e:
        flash(f'Could not remove staff access: {e}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('admin.staff_requests'))


# ---------------------------------------------------------------------------
# Assign Staff Incharge
# ---------------------------------------------------------------------------

@admin_bp.route('/events/<int:event_id>/assign-staff', methods=['GET', 'POST'])
def assign_staff(event_id):
    guard = admin_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()
    if not event:
        flash('Event not found.', 'danger')
        cur.close()
        return redirect(url_for('admin.events_list'))

    # Handle remove staff incharge
    remove_id = request.args.get('remove_staff_id') or request.form.get('remove_staff_id')
    if remove_id:
        try:
            cur.execute("DELETE FROM event_incharge WHERE event_id = %s AND staff_id = %s", (event_id, remove_id))
            flash('Incharge staff removed successfully.', 'info')
        except Exception as e:
            flash(f'Failed to remove staff: {str(e)}', 'danger')
        cur.close()
        return redirect(url_for('admin.assign_staff', event_id=event_id))

    if request.method == 'POST':
        staff_ids = request.form.getlist('staff_ids[]') or request.form.getlist('staff_id')
        if not staff_ids and request.form.get('staff_id'):
            staff_ids = [request.form.get('staff_id')]

        try:
            for sid in staff_ids:
                if sid:
                    cur.execute(
                        "INSERT IGNORE INTO event_incharge (event_id, staff_id) VALUES (%s, %s)",
                        (event_id, sid)
                    )
            flash('Staff assigned successfully.', 'success')
            cur.close()
            return redirect(url_for('admin.assign_staff', event_id=event_id))
        except Exception as e:
            flash(f'Assignment failed: {str(e)}', 'danger')

    # Get approved staff
    cur.execute("SELECT * FROM staff WHERE is_approved = TRUE AND is_active = TRUE ORDER BY name")
    all_staff = cur.fetchall()

    cur.execute("SELECT staff_id FROM event_incharge WHERE event_id = %s", (event_id,))
    assigned_ids = {row['staff_id'] for row in cur.fetchall()}

    cur.execute(
        "SELECT s.* FROM event_incharge ei JOIN staff s ON ei.staff_id = s.id WHERE ei.event_id = %s",
        (event_id,)
    )
    assigned_staff = cur.fetchall()

    cur.close()
    return render_template('admin/assign_staff.html',
                           event=event, all_staff=all_staff,
                           assigned_ids=assigned_ids, assigned_staff=assigned_staff)


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

@admin_bp.route('/reports')
def reports():
    guard = admin_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT er.*, e.title AS event_title, e.event_type, s.name AS staff_name, s.name AS generated_by_name "
        "FROM event_reports er "
        "JOIN events e ON er.event_id = e.id "
        "JOIN staff s ON er.generated_by = s.id "
        "ORDER BY er.generated_at DESC"
    )
    reports_list = cur.fetchall()
    cur.execute(
        "SELECT ps.score, ps.max_score, ps.feedback, ps.updated_at, u.name AS participant_name, "
        "u.roll_no, e.title AS event_title, s.name AS evaluator_name "
        "FROM presentation_scores ps JOIN registrations r ON r.id=ps.registration_id "
        "JOIN users u ON u.id=r.user_id JOIN events e ON e.id=r.event_id "
        "JOIN staff s ON s.id=ps.staff_id ORDER BY ps.updated_at DESC"
    )
    presentation_scores = cur.fetchall()
    cur.execute("SELECT DISTINCT e.id,e.title FROM events e JOIN registrations r ON r.event_id=e.id JOIN presentation_scores ps ON ps.registration_id=r.id ORDER BY e.event_date DESC")
    publishable_events = cur.fetchall()
    cur.close()
    return render_template('admin/reports.html', reports=reports_list, presentation_scores=presentation_scores, publishable_events=publishable_events)


@admin_bp.route('/events/<int:event_id>/publish-results', methods=['POST'])
def publish_event_results(event_id):
    """Publish reviewed event/sub-event rankings and notify registered participants."""
    guard = admin_required()
    if guard: return guard
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT id, title FROM events WHERE id=%s", (event_id,))
    event = cur.fetchone()
    if not event:
        cur.close(); flash('Event not found.', 'danger'); return redirect(url_for('admin.reports'))
    cur.execute("SELECT COUNT(*) AS cnt FROM presentation_scores ps JOIN registrations r ON r.id=ps.registration_id WHERE r.event_id=%s", (event_id,))
    if not cur.fetchone()['cnt']:
        cur.close(); flash('No staff scores are available to publish for this event yet.', 'warning'); return redirect(url_for('admin.reports'))
    cur.execute("UPDATE events SET results_published=TRUE WHERE id=%s", (event_id,))
    cur.execute("SELECT DISTINCT user_id FROM registrations WHERE event_id=%s", (event_id,))
    for user in cur.fetchall():
        cur.execute("INSERT INTO notifications (user_id,title,message) VALUES (%s,%s,%s)", (user['user_id'], 'Results published', f"Results and leaderboard for {event['title']} are now available: /leaderboard/{event_id}"))
    cur.close()
    flash('Results published and participants notified.', 'success')
    return redirect(url_for('events.leaderboard', event_id=event_id))

@admin_bp.route('/results/publish', methods=['POST'])
def publish_selected_results():
    guard = admin_required()
    if guard: return guard
    try: event_id = int(request.form.get('event_id', ''))
    except (TypeError, ValueError):
        flash('Choose a valid event.', 'danger'); return redirect(url_for('admin.reports'))
    return redirect(url_for('admin.publish_event_results', event_id=event_id), code=307)
