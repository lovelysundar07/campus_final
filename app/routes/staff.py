from db import get_db
import os
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, current_app, jsonify)

staff_bp = Blueprint('staff', __name__)


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------

def staff_required():
    """Ensure user is an approved staff member."""
    if session.get('user_role') != 'staff':
        flash('Staff access required.', 'danger')
        return redirect(url_for('auth.login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT is_approved FROM staff WHERE id = %s", (session['user_id'],))
    staff = cur.fetchone()
    cur.close()

    if not staff or not staff['is_approved']:
        session.clear()
        flash('Your account is pending admin approval.', 'warning')
        return redirect(url_for('auth.login'))
    return None


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@staff_bp.route('/')
def dashboard():
    guard = staff_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT e.*, COUNT(r.id) AS reg_count, "
        "SUM(CASE WHEN r.attendance_status = 'present' THEN 1 ELSE 0 END) AS present_count "
        "FROM events e "
        "JOIN event_incharge ei ON e.id = ei.event_id "
        "LEFT JOIN registrations r ON e.id = r.event_id "
        "WHERE ei.staff_id = %s "
        "GROUP BY e.id ORDER BY e.event_date DESC",
        (session['user_id'],)
    )
    assigned_events = cur.fetchall()

    cur.execute(
        "SELECT COUNT(*) AS cnt FROM event_reports WHERE generated_by = %s",
        (session['user_id'],)
    )
    rep_row = cur.fetchone()
    reports_count = rep_row['cnt'] if rep_row else 0

    cur.close()
    return render_template('staff/dashboard.html',
                           assigned_events=assigned_events,
                           reports_count=reports_count)


# ---------------------------------------------------------------------------
# Event Detail
# ---------------------------------------------------------------------------

@staff_bp.route('/events/<int:event_id>')
def event_detail(event_id):
    guard = staff_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    # Verify staff is assigned to this event
    cur.execute(
        "SELECT * FROM event_incharge WHERE event_id = %s AND staff_id = %s",
        (event_id, session['user_id'])
    )
    if not cur.fetchone():
        flash('You are not assigned to this event.', 'danger')
        cur.close()
        return redirect(url_for('staff.dashboard'))

    cur.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()

    cur.execute(
        "SELECT COUNT(*) AS total FROM registrations WHERE event_id = %s", (event_id,)
    )
    total = cur.fetchone()['total']

    cur.execute(
        "SELECT COUNT(*) AS present FROM registrations "
        "WHERE event_id = %s AND attendance_status = 'present'", (event_id,)
    )
    present = cur.fetchone()['present']

    cur.execute(
        "SELECT COUNT(*) AS absent FROM registrations "
        "WHERE event_id = %s AND attendance_status = 'absent'", (event_id,)
    )
    absent = cur.fetchone()['absent']

    cur.execute(
        "SELECT r.*, u.name AS user_name, u.name AS participant_name, u.roll_no, u.dept, u.section, u.email, "
        "se.name AS sub_event_name "
        "FROM registrations r "
        "JOIN users u ON r.user_id = u.id "
        "LEFT JOIN sub_events se ON r.sub_event_id = se.id "
        "WHERE r.event_id = %s ORDER BY u.name",
        (event_id,)
    )
    registrations = cur.fetchall()

    if event and event['event_type'] == 'symposium':
        for p in registrations:
            cur.execute("SELECT * FROM team_members WHERE registration_id = %s", (p['id'],))
            p['team_members'] = cur.fetchall()

    cur.close()

    stats = {'total': total, 'present': present, 'absent': absent,
             'pending': total - present - absent}
    return render_template('staff/event_detail.html',
                           event=event,
                           participants=registrations,
                           registrations=registrations,
                           stats=stats)



# ---------------------------------------------------------------------------
# Daily workshop sessions and session-wise attendance
# ---------------------------------------------------------------------------
@staff_bp.route('/events/<int:event_id>/sessions', methods=['GET', 'POST'])
def workshop_sessions(event_id):
    guard = staff_required()
    if guard:
        return guard
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT e.* FROM events e JOIN event_incharge ei ON ei.event_id=e.id "
                "WHERE e.id=%s AND ei.staff_id=%s", (event_id, session['user_id']))
    event = cur.fetchone()
    if not event:
        cur.close()
        flash('You are not assigned to this event.', 'danger')
        return redirect(url_for('staff.dashboard'))
    if request.method == 'POST':
        session_date = request.form.get('session_date', '').strip()
        session_title = request.form.get('session_title', '').strip() or 'Workshop Session'
        try:
            cur.execute("INSERT INTO workshop_sessions (event_id, session_date, session_title, created_by_staff_id) "
                        "VALUES (%s,%s,%s,%s)",
                        (event_id, session_date, session_title, session['user_id']))
            cur.close()
            flash('Workshop session created. Mark attendance below.', 'success')
            return redirect(url_for('staff.workshop_sessions', event_id=event_id))
        except Exception:
            flash('Could not create session. Check the date and ensure the database upgrade has been applied.', 'danger')
    cur.execute("SELECT * FROM workshop_sessions WHERE event_id=%s ORDER BY session_date DESC, id DESC", (event_id,))
    sessions = cur.fetchall()
    cur.execute("SELECT r.id AS registration_id, u.name, u.roll_no, u.dept, u.section "
                "FROM registrations r JOIN users u ON u.id=r.user_id WHERE r.event_id=%s ORDER BY u.name",
                (event_id,))
    participants = cur.fetchall()
    for ws in sessions:
        cur.execute("SELECT registration_id, attendance_status FROM session_attendance WHERE session_id=%s",
                    (ws['id'],))
        ws['attendance'] = {row['registration_id']: row['attendance_status'] for row in cur.fetchall()}
    cur.close()
    return render_template('staff/workshop_sessions.html', event=event, sessions=sessions, participants=participants)


@staff_bp.route('/sessions/<int:session_id>/attendance', methods=['POST'])
def save_session_attendance(session_id):
    guard = staff_required()
    if guard:
        return guard
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT ws.*, ei.staff_id FROM workshop_sessions ws "
                "JOIN event_incharge ei ON ei.event_id=ws.event_id "
                "WHERE ws.id=%s AND ei.staff_id=%s", (session_id, session['user_id']))
    ws = cur.fetchone()
    if not ws:
        cur.close()
        flash('Session not found or not assigned to you.', 'danger')
        return redirect(url_for('staff.dashboard'))
    cur.execute("SELECT id FROM registrations WHERE event_id=%s", (ws['event_id'],))
    reg_ids = [row['id'] for row in cur.fetchall()]
    present_ids = set()
    for value in request.form.getlist('present_registration_ids'):
        try:
            present_ids.add(int(value))
        except ValueError:
            pass
    for reg_id in reg_ids:
        status = 'present' if reg_id in present_ids else 'absent'
        cur.execute("INSERT INTO session_attendance (session_id, registration_id, attendance_status, marked_by_staff_id) "
                    "VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE attendance_status=VALUES(attendance_status), "
                    "marked_by_staff_id=VALUES(marked_by_staff_id)",
                    (session_id, reg_id, status, session['user_id']))
    cur.close()
    flash('Daily attendance saved successfully.', 'success')
    return redirect(url_for('staff.workshop_sessions', event_id=ws['event_id']))


# ---------------------------------------------------------------------------
# Mark Attendance
# ---------------------------------------------------------------------------

@staff_bp.route('/events/<int:event_id>/attendance', methods=['POST'])
def mark_attendance(event_id):
    guard = staff_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    # Verify assignment
    cur.execute(
        "SELECT id FROM event_incharge WHERE event_id = %s AND staff_id = %s",
        (event_id, session['user_id'])
    )
    if not cur.fetchone():
        cur.close()
        return jsonify({'error': 'Not authorized'}), 403

    data = request.get_json(silent=True)
    if not data:
        # Form-based attendance
        attendance_data = request.form.to_dict()
        data = {}
        for key, val in attendance_data.items():
            if key.startswith('attendance_'):
                reg_id = key.replace('attendance_', '')
                data[reg_id] = val
        if 'registration_id' in request.form and 'status' in request.form:
            data[request.form['registration_id']] = request.form['status']
    elif isinstance(data, dict) and 'registration_id' in data and 'status' in data:
        data = {data['registration_id']: data['status']}

    updated = 0
    try:
        for reg_id, status in data.items():
            if status in ('present', 'absent', 'pending'):
                cur.execute(
                    "UPDATE registrations SET attendance_status = %s "
                    "WHERE id = %s AND event_id = %s",
                    (status, reg_id, event_id)
                )
                updated += 1
    except Exception as e:
        cur.close()
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Attendance update failed: {str(e)}', 'danger')
        return redirect(url_for('staff.event_detail', event_id=event_id))

    cur.close()
    if request.is_json:
        return jsonify({'success': True, 'updated': updated})
    flash(f'Attendance updated for {updated} participant(s).', 'success')
    return redirect(url_for('staff.event_detail', event_id=event_id))


# ---------------------------------------------------------------------------
# Participants List
# ---------------------------------------------------------------------------

@staff_bp.route('/events/<int:event_id>/participants')
def participants_list(event_id):
    guard = staff_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT id FROM event_incharge WHERE event_id = %s AND staff_id = %s",
        (event_id, session['user_id'])
    )
    if not cur.fetchone():
        flash('Not authorized to view this event.', 'danger')
        cur.close()
        return redirect(url_for('staff.dashboard'))

    cur.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()

    cur.execute(
        "SELECT r.*, u.name AS user_name, u.name AS participant_name, u.roll_no, u.dept, u.section, u.email, u.phone, "
        "r.ppt_file_path, r.attendance_status, se.name AS sub_event_name "
        "FROM registrations r "
        "JOIN users u ON r.user_id = u.id "
        "LEFT JOIN sub_events se ON r.sub_event_id = se.id "
        "WHERE r.event_id = %s ORDER BY u.name",
        (event_id,)
    )
    participants = cur.fetchall()

    if event and event['event_type'] == 'symposium':
        for p in participants:
            cur.execute("SELECT * FROM team_members WHERE registration_id = %s", (p['id'],))
            p['team_members'] = cur.fetchall()

    cur.close()
    return render_template('staff/event_detail.html', event=event, participants=participants)




# ---------------------------------------------------------------------------
# Score PPT / presentation performance
# ---------------------------------------------------------------------------
@staff_bp.route('/events/<int:event_id>/registrations/<int:registration_id>/score', methods=['POST'])
def score_presentation(event_id, registration_id):
    guard = staff_required()
    if guard:
        return guard
    try:
        score = float(request.form.get('score', ''))
        max_score = float(request.form.get('max_score', '100'))
    except (TypeError, ValueError):
        flash('Enter a valid numeric score.', 'danger')
        return redirect(url_for('staff.event_detail', event_id=event_id))
    if max_score <= 0 or score < 0 or score > max_score:
        flash(f'Score must be between 0 and {max_score:g}.', 'danger')
        return redirect(url_for('staff.event_detail', event_id=event_id))

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM event_incharge WHERE event_id=%s AND staff_id=%s",
                (event_id, session['user_id']))
    assigned = cur.fetchone()
    cur.execute("SELECT id FROM registrations WHERE id=%s AND event_id=%s",
                (registration_id, event_id))
    registration = cur.fetchone()
    if not assigned or not registration:
        cur.close()
        flash('You are not authorized to score this registration.', 'danger')
        return redirect(url_for('staff.dashboard'))
    try:
        cur.execute("INSERT INTO presentation_scores (registration_id, staff_id, score, max_score) "
                    "VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE score=VALUES(score), max_score=VALUES(max_score)",
                    (registration_id, session['user_id'], score, max_score))
        cur.close()
        flash('Presentation score saved and made available for administrator review.', 'success')
    except Exception:
        cur.close()
        flash('Could not save the score. Ensure the database upgrade has been applied.', 'danger')
    return redirect(url_for('staff.event_detail', event_id=event_id))


# ---------------------------------------------------------------------------
# Generate Report
# ---------------------------------------------------------------------------

@staff_bp.route('/events/<int:event_id>/report/generate', methods=['POST'])
def generate_report(event_id):
    guard = staff_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT id FROM event_incharge WHERE event_id = %s AND staff_id = %s",
        (event_id, session['user_id'])
    )
    if not cur.fetchone():
        flash('Not authorized.', 'danger')
        cur.close()
        return redirect(url_for('staff.dashboard'))

    cur.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()

    cur.execute(
        "SELECT r.*, u.name AS user_name, u.name AS participant_name, u.roll_no, u.dept, u.section, "
        "r.attendance_status, se.name AS sub_event_name "
        "FROM registrations r "
        "JOIN users u ON r.user_id = u.id "
        "LEFT JOIN sub_events se ON r.sub_event_id = se.id "
        "WHERE r.event_id = %s ORDER BY u.name",
        (event_id,)
    )
    participants = cur.fetchall()

    total = len(participants)
    present = sum(1 for p in participants if p['attendance_status'] == 'present')
    absent = sum(1 for p in participants if p['attendance_status'] == 'absent')

    stats = {'total': total, 'present': present, 'absent': absent,
             'pending': total - present - absent}

    notes = request.form.get('notes', '')

    try:
        from services.report_service import generate_event_report
        report_path = generate_event_report(
            event_id=event_id,
            event_data=event,
            participants=participants,
            stats=stats,
            report_folder=current_app.config['REPORT_FOLDER']
        )

        filename = os.path.basename(report_path)

        cur.execute(
            "INSERT INTO event_reports (event_id, generated_by, report_path, "
            "total_registered, total_present, notes) VALUES (%s, %s, %s, %s, %s, %s)",
            (event_id, session['user_id'], filename, total, present, notes)
        )
        flash('Report generated successfully!', 'success')
    except Exception as e:
        flash(f'Report generation failed: {str(e)}', 'danger')

    cur.close()
    return redirect(url_for('staff.event_detail', event_id=event_id))


# ---------------------------------------------------------------------------
# Staff Reports List
# ---------------------------------------------------------------------------

@staff_bp.route('/reports')
def staff_reports():
    guard = staff_required()
    if guard:
        return guard

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT er.*, e.title AS event_title, e.event_type, e.event_date "
        "FROM event_reports er "
        "JOIN events e ON er.event_id = e.id "
        "WHERE er.generated_by = %s ORDER BY er.generated_at DESC",
        (session['user_id'],)
    )
    reports_list = cur.fetchall()
    cur.close()
    return render_template('staff/my_reports.html', reports=reports_list)


# ── Aliases for template compatibility ──
@staff_bp.route('/my-events')
def my_events():
    return dashboard()

@staff_bp.route('/my-reports')
def my_reports():
    return staff_reports()
