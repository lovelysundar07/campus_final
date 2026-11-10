from flask import Blueprint, render_template, abort, session
from db import get_db

events_bp = Blueprint('events', __name__)


@events_bp.route('/events')
def public_events():
    db  = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT e.*, COUNT(r.id) AS reg_count FROM events e "
        "LEFT JOIN registrations r ON e.id = r.event_id "
        "WHERE e.is_published = TRUE "
        "GROUP BY e.id ORDER BY e.event_date ASC"
    )
    events = cur.fetchall()

    cur.execute("SELECT COUNT(*) AS cnt FROM events WHERE is_published=TRUE")
    total_events = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(DISTINCT user_id) AS cnt FROM registrations")
    total_participants = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) AS cnt FROM events WHERE is_published=TRUE AND event_date >= CURDATE()")
    upcoming_count = cur.fetchone()['cnt']

    cur.close()
    return render_template('index.html',
                           events=events,
                           total_events=total_events,
                           total_participants=total_participants,
                           upcoming_count=upcoming_count)


@events_bp.route('/events/<int:event_id>')
def event_detail(event_id):
    db  = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM events WHERE id=%s AND is_published=TRUE", (event_id,))
    event = cur.fetchone()
    if not event:
        cur.close()
        abort(404)

    sub_events = []
    if event['event_type'] == 'symposium':
        cur.execute("SELECT * FROM sub_events WHERE event_id=%s", (event_id,))
        sub_events = cur.fetchall()

    cur.execute("SELECT COUNT(*) AS cnt FROM registrations WHERE event_id=%s", (event_id,))
    reg_count = cur.fetchone()['cnt']

    cur.execute(
        "SELECT s.name, s.designation, s.department FROM event_incharge ei "
        "JOIN staff s ON ei.staff_id = s.id WHERE ei.event_id=%s", (event_id,))
    incharge_staff = cur.fetchall()
    cur.close()

    return render_template('index.html',
                           event=event, sub_events=sub_events,
                           reg_count=reg_count, incharge_staff=incharge_staff)


@events_bp.route('/leaderboard/<int:event_id>')
def leaderboard(event_id):
    """Show staff-scored results only after administrator publication."""
    from flask import session, redirect, url_for
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT id,title,event_type,results_published FROM events WHERE id=%s", (event_id,))
    event = cur.fetchone()
    if not event:
        cur.close(); abort(404)
    results = []
    if event.get('results_published'):
        cur.execute("SELECT r.sub_event_id, COALESCE(se.name, e.title) AS sub_event_name, u.name AS participant_name, u.dept, u.year_of_study, AVG(ps.score/ps.max_score*100) AS score_pct FROM registrations r JOIN users u ON u.id=r.user_id JOIN events e ON e.id=r.event_id LEFT JOIN sub_events se ON se.id=r.sub_event_id JOIN presentation_scores ps ON ps.registration_id=r.id WHERE r.event_id=%s GROUP BY r.id,r.sub_event_id,sub_event_name,u.name,u.dept,u.year_of_study ORDER BY r.sub_event_id, score_pct DESC, u.name", (event_id,))
        ranks = {}
        for row in cur.fetchall():
            key = row['sub_event_id'] or 0
            ranks[key] = ranks.get(key, 0) + 1
            row['rank'] = ranks[key]
            row['prize'] = 'First Prize' if row['rank']==1 else ('Second Prize' if row['rank']==2 else ('Third Prize' if row['rank']==3 else 'Participant'))
            results.append(row)
    cur.close()
    return render_template('leaderboard.html', event=event, results=results)


@events_bp.route('/leaderboards')
def all_leaderboards():
    from flask import session, redirect, url_for
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT id,title,event_type,event_date FROM events WHERE results_published=TRUE ORDER BY event_date DESC")
    published_events = cur.fetchall(); cur.close()
    return render_template('leaderboards.html', published_events=published_events)
