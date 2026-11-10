"""
Certificate generation service using ReportLab.
Produces a visually styled PDF certificate for MS College events.
"""

import os
import uuid
from datetime import datetime

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader


# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------
MSV_RED = colors.HexColor('#6D28D9')
MSV_GOLD = colors.HexColor('#C4B5FD')
MSV_DARK = colors.HexColor('#171622')
MSV_WHITE = colors.white
MSV_LIGHT_GRAY = colors.HexColor('#F5F5F5')


def generate_certificate(registration_id: int,
                          participant_name: str,
                          event_name: str,
                          event_date: str,
                          event_type: str,
                          cert_folder: str,
                          logo_path: str = None,
                          coordinating_staff: str = 'Event Coordination Team') -> tuple:
    """
    Generate a PDF certificate for a participant.

    Returns:
        tuple: (certificate_file_path: str, certificate_number: str)
    """
    # Generate unique certificate number
    cert_number = f"MSV-{event_type.upper()[:3]}-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"

    # File name
    safe_name = "".join(c if c.isalnum() else "_" for c in participant_name)
    filename = f"cert_{registration_id}_{safe_name}_{cert_number}.pdf"
    filepath = os.path.join(cert_folder, filename)

    # Parse date for display
    try:
        dt = datetime.strptime(str(event_date), '%Y-%m-%d')
        display_date = dt.strftime('%d %B %Y')
    except Exception:
        display_date = str(event_date)

    # Canvas – landscape A4
    page_width, page_height = landscape(A4)
    c = canvas.Canvas(filepath, pagesize=landscape(A4))

    _draw_certificate(c, page_width, page_height,
                      participant_name, event_name, display_date,
                      event_type.capitalize(), cert_number, logo_path, coordinating_staff)

    c.save()
    return filepath, cert_number


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _draw_certificate(c, pw, ph,
                      participant_name, event_name,
                      display_date, event_type_label, cert_number, logo_path=None, coordinating_staff='Event Coordination Team'):
    """Draw all certificate elements onto the canvas."""

    # --- Contemporary violet/white certificate background ---
    c.setFillColor(colors.HexColor('#F8F7FC'))
    c.rect(0, 0, pw, ph, fill=1, stroke=0)
    # Subtle violet side panels and soft shadow-like accents
    c.setFillColor(colors.HexColor('#EDE9FE'))
    c.rect(0, 0, 18, ph, fill=1, stroke=0)
    c.rect(pw-18, 0, 18, ph, fill=1, stroke=0)

    # --- Outer border (gold) ---
    c.setStrokeColor(MSV_RED)
    c.setLineWidth(2)
    c.rect(26, 26, pw - 52, ph - 52, fill=0, stroke=1)

    # --- Inner border (red) ---
    c.setStrokeColor(MSV_GOLD)
    c.setLineWidth(0.8)
    c.rect(34, 34, pw - 68, ph - 68, fill=0, stroke=1)

    # --- Top decorative bar ---
    c.setFillColor(MSV_DARK)
    c.roundRect(36, ph - 100, pw - 72, 66, 12, fill=1, stroke=0)

    # --- Circular college crest and identity ---
    if logo_path and os.path.isfile(logo_path):
        try:
            from reportlab.lib.utils import ImageReader
            logo_size = 48
            logo_x, logo_y = 48, ph - 91
            c.saveState()
            c.setFillColor(colors.white); c.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2 + 2, fill=1, stroke=0)
            c.setStrokeColor(MSV_GOLD); c.setLineWidth(1.5); c.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2 + 2, fill=0, stroke=1)
            c.drawImage(ImageReader(logo_path), logo_x, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto', anchor='c')
            c.restoreState()
        except Exception:
            pass
    c.setFillColor(colors.HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(pw / 2, ph - 63, "MS COLLEGE")
    c.setFont("Helvetica", 10)
    c.drawCentredString(pw / 2, ph - 81, "Virudhunagar, 626001")
    c.setFont("Helvetica", 9)
    c.drawCentredString(pw / 2, ph - 94, "Empowering Minds, Building Futures")

    # --- "Certificate of Participation" ---
    c.setFillColor(MSV_RED)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(pw / 2, ph - 160, "CERTIFICATE OF PARTICIPATION")

    # --- Horizontal gold rule ---
    c.setStrokeColor(MSV_GOLD)
    c.setLineWidth(1.5)
    c.line(80, ph - 175, pw - 80, ph - 175)

    # --- "This is to certify that" ---
    c.setFillColor(MSV_DARK)
    c.setFont("Helvetica", 14)
    c.drawCentredString(pw / 2, ph - 210, "This is to certify that")

    # --- Participant Name ---
    c.setFillColor(MSV_DARK)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(pw / 2, ph - 255, participant_name)

    # --- Underline for name ---
    name_width = c.stringWidth(participant_name, "Helvetica-Bold", 36)
    c.setStrokeColor(MSV_GOLD)
    c.setLineWidth(1)
    c.line(pw / 2 - name_width / 2, ph - 262,
           pw / 2 + name_width / 2, ph - 262)

    # --- "has successfully participated in" ---
    c.setFillColor(MSV_DARK)
    c.setFont("Helvetica", 14)
    c.drawCentredString(pw / 2, ph - 295,
                        f"has successfully participated in the {event_type_label}")

    # --- Event Name ---
    c.setFillColor(MSV_RED)
    c.setFont("Helvetica-Bold", 21)
    # Wrap long event names
    _draw_wrapped_string(c, pw / 2, ph - 330, event_name, "Helvetica-Bold", 22, pw - 160)

    # --- Date ---
    c.setFillColor(MSV_DARK)
    c.setFont("Helvetica", 13)
    c.drawCentredString(pw / 2, ph - 375, f"held on  {display_date}")

    # --- Bottom section: clearly marked sample/demo certificate ---
    c.setStrokeColor(MSV_GOLD)
    c.setLineWidth(1)
    c.line(80, 105, pw - 80, 105)
    c.setFillColor(MSV_DARK)
    c.setFont("Helvetica", 9)
    c.drawString(50, 78, f"Reference: {cert_number}")
    c.drawRightString(pw - 50, 78, f"Issued: {display_date}")
    c.setFillColor(MSV_DARK)
    c.setFont("Helvetica-Bold", 9)
    coordinator = (coordinating_staff or 'Event Coordination Team')
    if len(coordinator) > 78: coordinator = coordinator[:75] + '...'
    c.drawCentredString(pw / 2, 62, f"Coordinating Staff: {coordinator}")
    c.saveState()
    c.setFillColor(colors.Color(0.43, 0.16, 0.85, alpha=0.12))
    c.translate(pw / 2, ph / 2)
    c.rotate(28)
    c.setFont("Helvetica-Bold", 62)
    c.drawCentredString(0, 0, "DEMO CERTIFICATE")
    c.restoreState()
    c.setFillColor(MSV_RED)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(pw / 2, 48, "DEMO CERTIFICATE • FOR PROJECT PREVIEW ONLY")


def _draw_wrapped_string(c, x, y, text, font, size, max_width):
    """Draw text, wrapping if it exceeds max_width."""
    c.setFont(font, size)
    if c.stringWidth(text, font, size) <= max_width:
        c.drawCentredString(x, y, text)
    else:
        # Split into two lines
        words = text.split()
        line1, line2 = [], []
        for word in words:
            if c.stringWidth(' '.join(line1 + [word]), font, size) <= max_width:
                line1.append(word)
            else:
                line2.append(word)
        c.drawCentredString(x, y + 14, ' '.join(line1))
        c.drawCentredString(x, y - 6, ' '.join(line2))
