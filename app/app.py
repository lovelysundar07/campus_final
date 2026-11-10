import os
import pymysql
import pymysql.cursors
import bcrypt
import secrets
from flask import Flask, redirect, url_for, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# ── Create upload directories ─────────────────────────────────────────────────
for _folder in [
    app.config['PPT_FOLDER'],
    app.config['CERT_FOLDER'],
    app.config['REPORT_FOLDER'],
    os.path.join(app.config['UPLOAD_FOLDER'], 'banners'),
]:
    os.makedirs(_folder, exist_ok=True)

# ── DB teardown ───────────────────────────────────────────────────────────────
@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ── Register blueprints ───────────────────────────────────────────────────────
from routes.auth        import auth_bp
from routes.admin       import admin_bp
from routes.staff       import staff_bp
from routes.participant import participant_bp
from routes.events      import events_bp
from routes.ai_assistant import ai_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp,       url_prefix='/admin')
app.register_blueprint(staff_bp,       url_prefix='/staff')
app.register_blueprint(participant_bp, url_prefix='/participant')
app.register_blueprint(events_bp)
app.register_blueprint(ai_bp,          url_prefix='/ai')

# ── Context processor ─────────────────────────────────────────────────────────
@app.context_processor
def inject_globals():
    return {
        'college_name':    app.config['COLLEGE_NAME'],
        'college_tagline': app.config['COLLEGE_TAGLINE'],
    }

# ── Root redirect ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('events.public_events'))

# ── DB initialisation ─────────────────────────────────────────────────────────
def init_db():
    # Step 1: connect without selecting a DB to create it first
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE DATABASE IF NOT EXISTS campus_events "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            print("  [OK] Database campus_events ready")
    finally:
        conn.close()

    # Step 2: reconnect WITH the DB selected, run schema
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database='campus_events',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                raw = f.read()

            # Strip block comments /* ... */
            import re
            raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)
            # Strip line comments and blank lines
            lines = []
            for line in raw.splitlines():
                line = line.split('--')[0].strip()
                if line:
                    lines.append(line)
            clean_sql = ' '.join(lines)

            # Split into individual statements
            for stmt in clean_sql.split(';'):
                stmt = stmt.strip()
                if not stmt:
                    continue
                # Skip CREATE DATABASE / USE — already handled
                if stmt.upper().startswith('CREATE DATABASE') or \
                   stmt.upper().startswith('USE '):
                    continue
                try:
                    cur.execute(stmt)
                except pymysql.err.OperationalError as e:
                    if e.args[0] not in (1050, 1061, 1062):  # table/index/key exists
                        print(f"  Schema note: {e}")
                except Exception as e:
                    print(f"  Schema note: {e}")

            print("  [OK] Tables created")

            # Default admin
            cur.execute("SELECT id FROM admins WHERE email=%s",
                        ('admin@msvcollege.ac.in',))
            if not cur.fetchone():
                initial_password = os.environ.get('ADMIN_INITIAL_PASSWORD') or secrets.token_urlsafe(12)
                pw = bcrypt.hashpw(initial_password.encode('utf-8'), bcrypt.gensalt()).decode()
                cur.execute(
                    "INSERT INTO admins (name,email,password_hash) VALUES (%s,%s,%s)",
                    ('MSV Admin', 'admin@msvcollege.ac.in', pw))
                print("  [OK] Initial admin email: admin@msvcollege.ac.in")
                print(f"  [IMPORTANT] Initial admin password (shown once): {initial_password}")
    finally:
        conn.close()



@app.context_processor
def inject_nav_context():
    """Make unread participant notifications visible in the shared navbar."""
    count = 0
    try:
        from flask import session
        from db import get_db
        if session.get('user_id') and session.get('user_role') == 'participant':
            db = get_db(); cur = db.cursor()
            cur.execute("SELECT COUNT(*) AS cnt FROM notifications WHERE user_id=%s AND is_read=FALSE", (session['user_id'],))
            row = cur.fetchone(); count = int(row['cnt'] if row else 0)
            cur.close()
    except Exception:
        count = 0
    return {'unread_notifications_count': count}

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("Initialising database...")
    try:
        init_db()
        print("[OK] Database ready.")
    except Exception as e:
        print(f"[ERROR] DB error (is MySQL running?): {e}")
    app.run(debug=True, host='0.0.0.0', port=5000)
