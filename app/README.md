# MS College Campus Events & Workshop Management System

A Flask + MySQL college event portal for participants, staff, and administrators.

## Technology stack
- Frontend: HTML, CSS, JavaScript, Jinja templates
- Backend: Python 3.12 + Flask
- Database: MySQL (XAMPP for local development)
- DB driver: PyMySQL
- AI assistant: Google Gemini API (optional; the app has a fallback response)
- PDF reports/certificates: ReportLab

## First-time setup on Windows 11

### 1. Install required software
1. Install **Python 3.12 (64-bit)** and enable **Add Python to PATH**.
2. Install **XAMPP**.
3. Install a code editor such as VS Code.
4. Start **Apache (optional)** and **MySQL** in the XAMPP Control Panel. Flask itself serves the website; Apache is not required.

### 2. Configure environment variables
1. Open this project folder.
2. Copy `.env.example` and rename the copy to `.env`.
3. Open `.env` and set `SECRET_KEY` to a long random value.
4. Set `MYSQL_HOST=127.0.0.1`, `MYSQL_USER=root`, and `MYSQL_PASSWORD=` to match your local XAMPP configuration.
5. Set `MYSQL_DB=campus_events`.
6. Add a Google Gemini API key to `GEMINI_API_KEY` only if you want the AI assistant enabled.

Do not share `.env`, API keys, database passwords, or production secrets.

### 3. Install Python packages
Double-click `setup.bat`.

Or run these commands in PowerShell from the `app` folder:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, use `setup.bat` / `run.bat` or run `venv\Scripts\python.exe app.py` directly.

### 4. Create the database and tables
1. Start MySQL in XAMPP.
2. Run `run.bat`.
3. On first startup, `app.py` creates the `campus_events` database and creates tables from `schema.sql`.

If you already have an older database, **back it up first** and then import these files from the extracted `campus` folder in phpMyAdmin: `database/migrations/001_project_upgrade.sql`, followed by `database/migrations/002_profile_images_and_custom_event_types.sql`. Each migration is intended to run once; do not re-run an `ALTER TABLE` migration after it has succeeded. The second migration adds participant/staff profile-picture columns and enables custom event categories.

### 5. Open the website
Visit `http://127.0.0.1:5000`.

On first startup, the application creates `admin@msvcollege.ac.in` and prints a randomly generated initial password in the terminal once. Save it securely and log in. If you set `ADMIN_INITIAL_PASSWORD` in `.env` before the first startup, that value is used instead. If the admin already exists in the database, startup does not reset its password.

Change the initial password after login and before exposing the project to any network or cloud.

## Main routes
- Public events: `/`
- Login: `/login`
- Student registration: `/register`
- Staff registration: `/staff/register`
- Profile editing: `/profile`
- Admin dashboard: `/admin/`
- Staff dashboard: `/staff/`
- Participant dashboard: `/participant/`

Staff registration requires administrator approval. Staff can manage attendance only for events assigned to them.

## Included changes in this refresh
- Violet, purple, and black theme with a restrained animated background.
- Light/dark mode toggle and centralized language toggle in the main navigation.
- MS College crest in the navigation and sidebars; college location shown as Virudhunagar, 626001.
- Arts and Science departments and Year of Study in participant registration.
- Self-service profile editing for participant, staff, and admin accounts.
- Per-sub-event venue on symposium creation.
- Admin sub-event editing and staff assignment screen.
- Daily workshop sessions and session-wise attendance.
- 75% attendance threshold for issuing workshop certificates when daily sessions exist; if no daily sessions exist, the legacy attendance status must be present.
- Staff PPT scoring saved to the database and shown in the administrator reports panel.
- Participant PDF export for each event.
- Database-grounded Gemini context for published events and the logged-in participant's own registrations.
- Fixed undefined `MSV_WHITE` reference in event PDF report generation.
- Certificate color palette updated to violet and lavender.
- Event publication notifications to registered participant accounts.

## Database / AI accuracy notes
The assistant uses retrieved database context as its source of truth for event and account-specific facts and is instructed not to invent missing information. No generative AI system can guarantee 100% factual correctness, so critical decisions should be verified against the database. The backend does not trust a user ID sent by the browser; it uses the logged-in session identity.

## Cloud deployment checklist
For deployment outside your laptop:
1. This package includes a `Procfile` for Render-like platforms (`gunicorn app:app --workers 2 --timeout 120`).
2. Create a web service from the GitHub repository and use `pip install -r requirements.txt` as the build command.
3. Create a managed MySQL database that is reachable from the web service. Import `schema.sql` into that database (select the database first and omit the local `CREATE DATABASE` / `USE` statements if your provider does not allow them).
4. Set the service start command to `gunicorn app:app --workers 2 --timeout 120`.
5. Add `SECRET_KEY`, `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`, and optional `GEMINI_API_KEY` in the host's environment settings.
6. Use a production WSGI server such as Waitress or Gunicorn (depending on the host OS).
2. Use a managed MySQL database with backups and restricted network access.
3. Configure environment variables in the hosting provider; never upload `.env`.
4. Set a unique production `SECRET_KEY`.
5. Disable Flask debug mode.
6. Configure HTTPS, allowed upload sizes, and backup/retention policies.
7. Keep API keys private and apply per-role authorization checks.
8. Test the entire workflow against a staging database before publishing.

XAMPP's MySQL service on your laptop is for local development; it is not the recommended database for a public cloud deployment.

## Important verification
The source files and templates were syntax-checked during packaging. A live end-to-end test still requires your Windows environment, XAMPP/MySQL credentials, database migration, and (optionally) a working Gemini API key.


## Recent UI and workflow refinements
- Navigation stays in document flow rather than covering the first page content.
- Login no longer shows project feature key points or the stray “M” branding.
- Participant year of study is limited to First, Second, and Third Year.
- Participant event cards, application pages, and registrations show assigned staff contacts when available.
- Staff can save PPT scores; event report generation imports `os` correctly.
- Profile pictures are supported for participant and staff profiles (PNG/JPG/JPEG/WEBP).
- The loader uses the college crest with restrained motion and respects reduced-motion preferences.
- Event type storage supports custom categories; apply the database migration before using the new profile fields.


## v3 visual and results updates
- The MS crest is used as the browser favicon and the circularly cropped navbar/loading/profile visual.
- Participant and staff registration forms accept an optional profile picture (PNG/JPG/JPEG/WEBP).
- Certificates are explicitly marked DEMO CERTIFICATE and no longer include a college seal or principal signature.
- Admin can review staff-entered marks in Reports, then publish event results. Published leaderboards are visible to all signed-in roles and participants receive notifications.
- Apply `database/migrations/003_leaderboard_results.sql` once after migrations 001 and 002 to add the event results-publication flag. Back up first.
