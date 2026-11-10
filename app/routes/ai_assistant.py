import os
from db import get_db
from flask import Blueprint, request, jsonify, session, current_app
from google import genai
from google.genai import types

ai_bp = Blueprint('ai', __name__)


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------

@ai_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    user_message = data.get('message', '').strip()
    language = data.get('language') or data.get('lang') or 'en'
    user_id = session.get('user_id')  # Never trust a client-supplied identity
    user_type = session.get('user_role', 'participant')

    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Build user context if user_id is provided
    user_context = _build_user_context(user_id, user_type) if user_id else _build_user_context(None, user_type)

    # Prepare language instruction
    lang_instruction = (
        "Respond in Tamil language using natural, friendly Tamil text."
        if language == 'ta'
        else "Respond in English."
    )

    system_prompt = f"""You are the MS College Campus Events Assistant.
Help students with event registrations, schedules, and certificates.
{lang_instruction}
You are helpful, concise, and friendly.
Treat the supplied database context as the only source of truth for MS College events, registrations,
attendance, marks, and certificates. Do not invent or infer missing facts. If the context does not
contain an answer, explicitly say that the information is not available in the current database.
Never disclose another participant's personal data. Do not claim an action was completed unless the
backend actually completed it.

User context:
{user_context}
"""

    ai_response = None

    try:
        api_key = current_app.config.get('GEMINI_API_KEY', '')
        if api_key:
            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(
                    timeout=5000,
                    retry_options=types.HttpRetryOptions(attempts=1)
                )
            )
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=1024,
                    temperature=0.7,
                )
            )
            ai_response = response.text
    except Exception as e:
        # Graceful fallback on API demand spike / network / quota issues
        pass

    if not ai_response:
        ai_response = _generate_fallback_response(user_message, language, user_id, user_context)

    # Log the chat
    _log_chat(user_id if user_type == 'participant' else None, user_type, user_message, ai_response, language)

    return jsonify({'response': ai_response, 'language': language})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_fallback_response(message, language, user_id, user_context):
    """Provide a reliable, contextual response when the remote AI is temporarily busy."""
    msg = message.lower()
    is_ta = (language == 'ta')

    if any(w in msg for w in ['hello', 'hi', 'hey', 'வணக்கம்', 'ஹலோ']):
        if is_ta:
            return "வணக்கம்! நான் MS கல்லூரி வளாக நிகழ்வுகள் உதவியாளர். உங்கள் நிகழ்வுப் பதிவுகள், சான்றிதழ்கள் மற்றும் அட்டவணை பற்றி என்னிடம் கேட்கலாம்."
        return "Hello! I am your MS College Campus Events Assistant. How can I help you with your events, registrations, or certificates today?"

    if any(w in msg for w in ['register', 'registered', 'event', 'workshop', 'seminar', 'symposium', 'நிகழ்வு', 'பதிவு']):
        if is_ta:
            return f"உங்கள் நிகழ்வுப் பதிவு விவரங்கள்:\n\n{user_context}"
        return f"Here are your event registration details:\n\n{user_context}"

    if any(w in msg for w in ['cert', 'certificate', 'சான்றிதழ்']):
        if is_ta:
            return f"உங்கள் சான்றிதழ் விவரங்கள்:\n\n{user_context}\n\nகுறிப்பு: சான்றிதழ்களை 'My Certificates' பக்கத்தில் பதிவிறக்கம் செய்யலாம்."
        return f"Here are your certificate details:\n\n{user_context}\n\nNote: You can download issued certificates from your 'My Certificates' dashboard."

    # General default response
    if is_ta:
        return f"MS கல்லூரி நிகழ்வு உதவியாளர்: தங்களுக்கு உதவ தயாராக உள்ளேன்.\n\n{user_context}"
    return f"MS College Events Assistant: I am here to help you navigate campus events.\n\n{user_context}"


def _build_user_context(user_id, user_type='participant'):
    """Retrieve only database-backed public events and the logged-in participant's own data."""
    try:
        cur = get_db().cursor()
        user = None
        registrations = []
        certificates = []
        lines = []
        if user_type == 'participant' and user_id:
            cur.execute("SELECT name, roll_no, dept, section FROM users WHERE id=%s", (user_id,))
            user = cur.fetchone()
            if not user:
                cur.close()
                return "The logged-in participant record was not found in the database."
            cur.execute(
                "SELECT e.title, e.event_type, e.event_date, e.venue, r.attendance_status, "
                "r.certificate_issued, se.name AS sub_event_name "
                "FROM registrations r JOIN events e ON r.event_id=e.id "
                "LEFT JOIN sub_events se ON r.sub_event_id=se.id "
                "WHERE r.user_id=%s ORDER BY e.event_date DESC LIMIT 20", (user_id,)
            )
            registrations = cur.fetchall()
            cur.execute(
                "SELECT c.certificate_number, e.title AS event_title, c.issued_at "
                "FROM certificates c JOIN registrations r ON c.registration_id=r.id "
                "JOIN events e ON r.event_id=e.id WHERE r.user_id=%s", (user_id,)
            )
            certificates = cur.fetchall()
        elif user_type == 'staff' and user_id:
            cur.execute("SELECT name, email, designation, department FROM staff WHERE id=%s", (user_id,))
            staff_user = cur.fetchone()
            if not staff_user:
                cur.close()
                return "The logged-in staff record was not found in the database."
            lines = [f"Staff account: {staff_user['name']} | Role: staff | Department: {staff_user.get('department') or 'Not specified'} | Designation: {staff_user.get('designation') or 'Not specified'}"]
            cur.execute("SELECT e.id, e.title, e.event_type, e.event_date, e.venue, e.status, COUNT(r.id) AS registrations, SUM(CASE WHEN r.attendance_status='present' THEN 1 ELSE 0 END) AS present_count FROM event_incharge ei JOIN events e ON e.id=ei.event_id LEFT JOIN registrations r ON r.event_id=e.id WHERE ei.staff_id=%s GROUP BY e.id ORDER BY e.event_date DESC LIMIT 30", (user_id,))
            assigned = cur.fetchall()
            lines.append("Events assigned to this staff member:")
            if assigned:
                for ev in assigned:
                    lines.append(f"- {ev['title']} | Type: {ev['event_type']} | Date: {ev['event_date']} | Venue: {ev['venue']} | Status: {ev['status']} | Registrations: {ev['registrations']} | Present: {ev.get('present_count') or 0}")
            else:
                lines.append("- No assigned events found.")
            cur.execute("SELECT COUNT(*) AS cnt FROM event_reports WHERE generated_by=%s", (user_id,))
            report_count = cur.fetchone()['cnt']
            lines.append(f"Reports generated by this staff member: {report_count}")
        elif user_type == 'admin' and user_id:
            cur.execute("SELECT name, email FROM admins WHERE id=%s", (user_id,))
            admin_user = cur.fetchone()
            if not admin_user:
                cur.close()
                return "The logged-in administrator record was not found in the database."
            lines = [f"Administrator account: {admin_user['name']} | Role: admin"]
            cur.execute("SELECT COUNT(*) AS total FROM events")
            total_events = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) AS total FROM registrations")
            total_registrations = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) AS total FROM staff WHERE is_approved=FALSE")
            pending_staff = cur.fetchone()['total']
            lines.append(f"Admin overview from database: total events={total_events}; total registrations={total_registrations}; staff awaiting approval={pending_staff}.")
            cur.execute("SELECT e.title, e.event_type, e.event_date, e.venue, e.status, COUNT(r.id) AS registrations FROM events e LEFT JOIN registrations r ON r.event_id=e.id GROUP BY e.id ORDER BY e.event_date DESC LIMIT 30")
            admin_events = cur.fetchall()
            lines.append("Event management overview:")
            for ev in admin_events:
                lines.append(f"- {ev['title']} | Type: {ev['event_type']} | Date: {ev['event_date']} | Venue: {ev['venue']} | Status: {ev['status']} | Registrations: {ev['registrations']}")

        cur.execute(
            "SELECT title, event_type, event_date, start_time, end_time, venue, description "
            "FROM events WHERE is_published=TRUE AND status <> 'cancelled' "
            "ORDER BY event_date ASC LIMIT 50"
        )
        published_events = cur.fetchall()
        cur.close()

        lines = []
        if user:
            lines.extend([
                f"Participant: {user['name']} | Roll No: {user['roll_no']} | Department: {user['dept']} | Year of Study: {user['section']}",
                "Registered Events:"
            ])
            if registrations:
                for reg in registrations:
                    sub = f" (Sub-event: {reg['sub_event_name']})" if reg.get('sub_event_name') else ""
                    cert = " [Certificate Issued]" if reg['certificate_issued'] else ""
                    lines.append(
                        f"- {reg['title']}{sub} | Type: {reg['event_type']} | Date: {reg['event_date']} | "
                        f"Venue: {reg['venue']} | Attendance: {reg['attendance_status']}{cert}"
                    )
            else:
                lines.append("- No registrations found.")
            lines.append("Certificates:")
            if certificates:
                for cert in certificates:
                    lines.append(f"- {cert['event_title']} | Certificate #: {cert['certificate_number']} | Issued: {cert['issued_at']}")
            else:
                lines.append("- No certificates found.")

        lines.append("Published college events from database:")
        if published_events:
            for event in published_events:
                lines.append(
                    f"- {event['title']} | Type: {event['event_type']} | Date: {event['event_date']} | "
                    f"Time: {event['start_time']}-{event['end_time']} | Venue: {event['venue']} | "
                    f"Description: {event.get('description') or 'Not specified'}"
                )
        else:
            lines.append("- No published events found.")
        return "\\n".join(lines)
    except Exception:
        return "Database context could not be loaded. Do not guess; tell the user the information is currently unavailable."


def _log_chat(user_id, user_type, user_message, ai_response, language):
    """Log chat to database."""
    try:
        cur = get_db().cursor()
        valid_types = ('participant', 'staff', 'admin')
        ut = user_type if user_type in valid_types else 'participant'
        cur.execute(
            "INSERT INTO ai_chat_logs (user_id, user_type, user_message, ai_response, language) "
            "VALUES (%s, %s, %s, %s, %s)",
            (user_id, ut, user_message, ai_response, language)
        )
        get_db().commit()
        cur.close()
    except Exception:
        pass  # Logging failures should not break the chat response
