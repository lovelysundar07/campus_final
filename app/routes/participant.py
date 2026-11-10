from db import get_db
import os
from datetime import date
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, current_app)
from werkzeug.utils import secure_filename

participant_bp = Blueprint('participant', __name__)

def _attach_event_staff(cur, event_id):
    """Return assigned staff contact details for participant-facing event pages."""
    cur.execute("SELECT DISTINCT s.name, s.email, s.phone, s.designation FROM staff s "
                "LEFT JOIN event_incharge ei ON ei.staff_id=s.id AND ei.event_id=%s "
                "LEFT JOIN sub_event_staff ses ON ses.staff_id=s.id "
                "LEFT JOIN sub_events se ON se.id=ses.sub_event_id AND se.event_id=%s "
                "WHERE s.is_active=TRUE AND (ei.id IS NOT NULL OR se.id IS NOT NULL) "
                "ORDER BY s.name", (event_id, event_id))
    return cur.fetchall()


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------

def participant_required():
    if session.get('user_role') != 'participant':
        flash('Please log in as a participant.', 'danger')
        return redirect(url_for('auth.login'))
    return None


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@participant_bp.route('/')
def dashboard():
    guard = participant_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    # User profile
    cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()

    # Upcoming published events
    cur.execute(
        "SELECT * FROM events WHERE is_published = TRUE AND event_date >= CURDATE() "
        "AND status = 'upcoming' ORDER BY event_date ASC LIMIT 5"
    )
    upcoming_events = cur.fetchall()

    # My registrations
    cur.execute(
        "SELECT r.*, e.title AS event_title, e.event_type, e.event_date, e.venue "
        "FROM registrations r "
        "JOIN events e ON r.event_id = e.id "
        "WHERE r.user_id = %s ORDER BY r.registered_at DESC",
        (session['user_id'],)
    )
    registrations = cur.fetchall()

    # PPT count
    ppt_count = sum(1 for r in registrations if r.get('ppt_file_path'))

    # My certificates
    cur.execute(
        "SELECT c.*, e.title AS event_title, e.event_type, e.event_date "
        "FROM certificates c "
        "JOIN registrations r ON c.registration_id = r.id "
        "JOIN events e ON r.event_id = e.id "
        "WHERE r.user_id = %s ORDER BY c.issued_at DESC",
        (session['user_id'],)
    )
    certificates = cur.fetchall()
    cert_count = len(certificates)

    # Unread notifications count
    cur.execute(
        "SELECT COUNT(*) AS cnt FROM notifications WHERE user_id = %s AND is_read = FALSE",
        (session['user_id'],)
    )
    unread_row = cur.fetchone()
    unread_count = unread_row['cnt'] if unread_row else 0

    cur.close()
    return render_template('participant/dashboard.html',
                           user=user,
                           registrations=registrations,
                           upcoming_events=upcoming_events,
                           certificates=certificates,
                           cert_count=cert_count,
                           ppt_count=ppt_count,
                           unread_count=unread_count)


# ---------------------------------------------------------------------------
# Browse Events
# ---------------------------------------------------------------------------

@participant_bp.route('/events')
def browse_events():
    guard = participant_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    event_type = request.args.get('type', '')
    query = "SELECT * FROM events WHERE is_published = TRUE"
    params = []
    if event_type:
        query += " AND event_type = %s"
        params.append(event_type)
    query += " ORDER BY event_date ASC"

    cur.execute(query, params)
    events = cur.fetchall()
    for event in events:
        event['assigned_staff'] = _attach_event_staff(cur, event['id'])

    # Check which events the participant is already registered for
    cur.execute("SELECT event_id FROM registrations WHERE user_id = %s", (session['user_id'],))
    registered_event_ids = {row['event_id'] for row in cur.fetchall()}

    cur.close()
    return render_template('participant/events.html',
                           events=events,
                           registered_event_ids=registered_event_ids,
                           filter_type=event_type)


# ---------------------------------------------------------------------------
# Apply / Register for Event
# ---------------------------------------------------------------------------

@participant_bp.route('/events/<int:event_id>/apply', methods=['GET', 'POST'])
def apply_event(event_id):
    guard = participant_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM events WHERE id = %s AND is_published = TRUE", (event_id,))
    event = cur.fetchone()
    if not event:
        flash('Event not found or not available.', 'danger')
        cur.close()
        return redirect(url_for('participant.browse_events'))

    # Check registration deadline
    if event['registration_deadline'] and date.today() > event['registration_deadline']:
        flash('Registration deadline has passed.', 'warning')
        cur.close()
        return redirect(url_for('participant.browse_events'))

    # Check capacity
    cur.execute("SELECT COUNT(*) AS cnt FROM registrations WHERE event_id = %s", (event_id,))
    reg_count = cur.fetchone()['cnt']
    if reg_count >= event['capacity']:
        flash('This event is full.', 'warning')
        cur.close()
        return redirect(url_for('participant.browse_events'))

    # Fetch participant info
    cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    participant = cur.fetchone()

    # Preserve custom event categories; infer only for legacy rows with a blank type.
    event_type = (event.get('event_type') or '').strip().lower()
    if not event_type:
        cur.execute("SELECT COUNT(*) AS cnt FROM sub_events WHERE event_id = %s", (event_id,))
        event_type = 'symposium' if cur.fetchone()['cnt'] > 0 else 'workshop'
        cur.execute("UPDATE events SET event_type = %s WHERE id = %s", (event_type, event_id))
        event['event_type'] = event_type

    # Sub-events for symposium
    sub_events = []
    if event_type == 'symposium':
        cur.execute("SELECT * FROM sub_events WHERE event_id = %s", (event_id,))
        sub_events = cur.fetchall()

    if request.method == 'POST':
        try:
            if event_type == 'workshop':
                _register_workshop(cur, event_id, participant)

            elif event_type == 'seminar':
                _register_seminar(cur, event_id, participant)

            elif event_type == 'symposium':
                _register_symposium(cur, event_id, participant, sub_events)
            else:
                _register_generic_event(cur, event_id, participant)

            flash('Successfully registered for the event!', 'success')
            cur.close()

            # Add notification
            _add_notification(session['user_id'],
                              'Registration Confirmed',
                              f"You have successfully registered for '{event['title']}'.")
            return redirect(url_for('participant.my_registrations'))

        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')

    assigned_staff = _attach_event_staff(cur, event_id)
    cur.close()
    template_name = f'participant/apply_{event_type}.html'
    if event_type not in ('workshop', 'seminar', 'symposium'):
        template_name = 'participant/apply_other.html'
    return render_template(
        template_name,
        event=event,
        user=participant,
        participant=participant,
        sub_events=sub_events,
        assigned_staff=assigned_staff
    )


def _register_generic_event(cur, event_id, participant):
    """Register a participant for a custom event category."""
    cur.execute("SELECT id FROM registrations WHERE user_id=%s AND event_id=%s",
                (participant['id'], event_id))
    if cur.fetchone():
        raise Exception("You are already registered for this event.")
    cur.execute("INSERT INTO registrations (user_id, event_id) VALUES (%s,%s)",
                (participant['id'], event_id))


def _register_workshop(cur, event_id, participant):
    """Register participant for workshop."""
    cur.execute(
        "SELECT id FROM registrations WHERE user_id = %s AND event_id = %s",
        (participant['id'], event_id)
    )
    if cur.fetchone():
        raise Exception("You are already registered for this event.")
    cur.execute(
        "INSERT INTO registrations (user_id, event_id) VALUES (%s, %s)",
        (participant['id'], event_id)
    )


def _register_seminar(cur, event_id, participant):
    """Register participant for seminar with optional PPT upload."""
    cur.execute(
        "SELECT id FROM registrations WHERE user_id = %s AND event_id = %s",
        (participant['id'], event_id)
    )
    if cur.fetchone():
        raise Exception("You are already registered for this event.")

    ppt_path = None
    from flask import request as req, current_app
    if 'ppt_file' in req.files:
        ppt = req.files['ppt_file']
        if ppt and ppt.filename:
            ext = ppt.filename.rsplit('.', 1)[-1].lower()
            if ext in current_app.config.get('ALLOWED_PPT_EXTENSIONS', {'ppt', 'pptx', 'pdf'}):
                filename = secure_filename(
                    f"{participant['id']}_{event_id}_{ppt.filename}"
                )
                save_path = os.path.join(current_app.config['PPT_FOLDER'], filename)
                ppt.save(save_path)
                ppt_path = f"uploads/ppts/{filename}"
            else:
                raise Exception("Invalid file type. Allowed: ppt, pptx, pdf")

    cur.execute(
        "INSERT INTO registrations (user_id, event_id, ppt_file_path) VALUES (%s, %s, %s)",
        (participant['id'], event_id, ppt_path)
    )


def _register_symposium(cur, event_id, participant, sub_events):
    """Register team for symposium."""
    from flask import request as req
    sub_event_id = req.form.get('sub_event_id')
    team_name = req.form.get('team_name', '').strip()

    if not sub_event_id:
        raise Exception("Please select a sub-event.")
    if not team_name:
        raise Exception("Team name is required.")

    # Check if already registered for this sub-event
    cur.execute(
        "SELECT id FROM registrations WHERE user_id = %s AND event_id = %s AND sub_event_id = %s",
        (participant['id'], event_id, sub_event_id)
    )
    if cur.fetchone():
        raise Exception("You are already registered for this sub-event.")

    # Validate sub-event belongs to event
    sub_event = next((se for se in sub_events if str(se['id']) == str(sub_event_id)), None)
    if not sub_event:
        raise Exception("Invalid sub-event selection.")

    # Collect team members
    member_names = req.form.getlist('member_name[]')
    member_rolls = req.form.getlist('member_roll[]')
    member_depts = req.form.getlist('member_dept[]')
    member_sections = req.form.getlist('member_section[]')
    member_leaders = req.form.getlist('member_leader[]')

    team_size = len(member_names)
    if team_size < sub_event['min_team_size'] or team_size > sub_event['max_team_size']:
        raise Exception(
            f"Team size must be between {sub_event['min_team_size']} and {sub_event['max_team_size']}."
        )

    cur.execute(
        "INSERT INTO registrations (user_id, event_id, sub_event_id, team_name) VALUES (%s, %s, %s, %s)",
        (participant['id'], event_id, sub_event_id, team_name)
    )
    registration_id = cur.lastrowid

    for i, mname in enumerate(member_names):
        is_leader = str(i) in member_leaders or 'leader' in member_leaders
        cur.execute(
            "INSERT INTO team_members (registration_id, name, roll_no, dept, section, is_leader) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (registration_id,
             mname.strip(),
             member_rolls[i].strip() if i < len(member_rolls) else '',
             member_depts[i].strip() if i < len(member_depts) else '',
             member_sections[i].strip() if i < len(member_sections) else '',
             is_leader)
        )


def _add_notification(user_id, title, message):
    """Helper to insert a notification."""
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO notifications (user_id, title, message) VALUES (%s, %s, %s)",
            (user_id, title, message)
        )
        cur.close()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# My Registrations
# ---------------------------------------------------------------------------

@participant_bp.route('/my-registrations')
def my_registrations():
    guard = participant_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT r.*, e.title AS event_title, e.event_type, e.event_date, e.venue, e.status AS event_status, "
        "se.name AS sub_event_name, c.certificate_number, c.certificate_path "
        "FROM registrations r "
        "JOIN events e ON r.event_id = e.id "
        "LEFT JOIN sub_events se ON r.sub_event_id = se.id "
        "LEFT JOIN certificates c ON r.id = c.registration_id "
        "WHERE r.user_id = %s ORDER BY r.registered_at DESC",
        (session['user_id'],)
    )
    registrations = cur.fetchall()

    # Include assigned staff contacts before and after registration.
    for reg in registrations:
        reg['assigned_staff'] = _attach_event_staff(cur, reg['event_id'])

    # Get team members for symposium entries
    for reg in registrations:
        if reg['event_type'] == 'symposium':
            cur.execute("SELECT * FROM team_members WHERE registration_id = %s", (reg['id'],))
            reg['team_members'] = cur.fetchall()

    cur.close()
    return render_template('participant/my_registrations.html', registrations=registrations)


# ---------------------------------------------------------------------------
# My Certificates
# ---------------------------------------------------------------------------

@participant_bp.route('/certificates')
def my_certificates():
    guard = participant_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT c.*, e.title AS event_title, e.event_type, e.event_date "
        "FROM certificates c "
        "JOIN registrations r ON c.registration_id = r.id "
        "JOIN events e ON r.event_id = e.id "
        "WHERE r.user_id = %s ORDER BY c.issued_at DESC",
        (session['user_id'],)
    )
    certificates = cur.fetchall()
    cur.close()
    return render_template('participant/certificates.html', certificates=certificates)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

@participant_bp.route('/notifications')
def notifications():
    guard = participant_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC",
        (session['user_id'],)
    )
    notifs = cur.fetchall()

    # Mark all as read
    cur.execute(
        "UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE",
        (session['user_id'],)
    )
    cur.close()
    return render_template('participant/notifications.html', notifications=notifs)
