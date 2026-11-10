"""
Event report generation service using ReportLab.
Produces a professional PDF report for an event's participant attendance.
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.platypus import KeepTogether


# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------
MSV_RED = colors.HexColor('#6D28D9')
MSV_GOLD = colors.HexColor('#C4B5FD')
MSV_DARK = colors.HexColor('#171622')
MSV_LIGHT = colors.HexColor('#F8F9FA')
MSV_GRAY = colors.HexColor('#6C757D')
TABLE_HEADER = colors.HexColor('#2C3E50')
PRESENT_COLOR = colors.HexColor('#D4EDDA')
ABSENT_COLOR = colors.HexColor('#F8D7DA')
PENDING_COLOR = colors.HexColor('#FFF3CD')


def generate_event_report(event_id: int,
                           event_data: dict,
                           participants: list,
                           stats: dict,
                           report_folder: str) -> str:
    """
    Generate a PDF event attendance report.

    Returns:
        str: Absolute path of the generated report file.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"report_event{event_id}_{timestamp}.pdf"
    filepath = os.path.join(report_folder, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    story = []

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=20,
        textColor=MSV_DARK,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    college_style = ParagraphStyle(
        'CollegeStyle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=MSV_RED,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    tagline_style = ParagraphStyle(
        'TaglineStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=MSV_GRAY,
        alignment=TA_CENTER,
        spaceAfter=8
    )
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=MSV_GRAY,
        fontName='Helvetica-Bold'
    )
    value_style = ParagraphStyle(
        'ValueStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=MSV_DARK
    )
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=MSV_GRAY,
        alignment=TA_CENTER
    )

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    story.append(Paragraph("MS COLLEGE", college_style))
    story.append(Paragraph("Empowering Minds, Building Futures", tagline_style))
    story.append(HRFlowable(width="100%", thickness=3, color=MSV_RED, spaceAfter=6))
    story.append(Paragraph("EVENT ATTENDANCE REPORT", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=MSV_GOLD, spaceAfter=12))

    # ------------------------------------------------------------------
    # Event Details Table
    # ------------------------------------------------------------------
    event_date = event_data.get('event_date', '')
    if hasattr(event_date, 'strftime'):
        event_date = event_date.strftime('%d %B %Y')

    start_time = str(event_data.get('start_time', ''))
    end_time = str(event_data.get('end_time', ''))

    details_data = [
        [_bold_para("Event Title:", label_style), Paragraph(str(event_data.get('title', '')), value_style)],
        [_bold_para("Event Type:", label_style), Paragraph(str(event_data.get('event_type', '')).capitalize(), value_style)],
        [_bold_para("Date:", label_style), Paragraph(str(event_date), value_style)],
        [_bold_para("Time:", label_style), Paragraph(f"{start_time} – {end_time}", value_style)],
        [_bold_para("Venue:", label_style), Paragraph(str(event_data.get('venue', '')), value_style)],
        [_bold_para("Capacity:", label_style), Paragraph(str(event_data.get('capacity', '')), value_style)],
        [_bold_para("Report Generated:", label_style),
         Paragraph(datetime.now().strftime('%d %B %Y, %I:%M %p'), value_style)],
    ]

    details_table = Table(details_data, colWidths=[4 * cm, None])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), MSV_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [MSV_LIGHT, colors.white]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 16))

    # ------------------------------------------------------------------
    # Statistics Summary
    # ------------------------------------------------------------------
    story.append(_section_header("ATTENDANCE SUMMARY", MSV_RED))
    story.append(Spacer(1, 6))

    stat_data = [
        ["Total Registered", "Present", "Absent", "Pending"],
        [
            str(stats.get('total', 0)),
            str(stats.get('present', 0)),
            str(stats.get('absent', 0)),
            str(stats.get('pending', 0))
        ]
    ]

    stat_table = Table(stat_data, colWidths=[None, None, None, None])
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, 1), 18),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 1), (0, 1), MSV_DARK),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#28A745')),
        ('TEXTCOLOR', (2, 1), (2, 1), MSV_RED),
        ('TEXTCOLOR', (3, 1), (3, 1), colors.HexColor('#FFC107')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, 1), [MSV_LIGHT]),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 20))

    # ------------------------------------------------------------------
    # Participant Table
    # ------------------------------------------------------------------
    story.append(_section_header("PARTICIPANT LIST", MSV_DARK))
    story.append(Spacer(1, 6))

    table_headers = ["#", "Name", "Roll No", "Dept", "Sec", "Attendance"]
    has_sub_event = any(p.get('sub_event_name') for p in participants)
    if has_sub_event:
        table_headers.insert(5, "Sub-Event")

    rows = [table_headers]
    for idx, p in enumerate(participants, 1):
        status = p.get('attendance_status', 'pending')
        row = [
            str(idx),
            str(p.get('participant_name', '')),
            str(p.get('roll_no', '')),
            str(p.get('dept', '')),
            str(p.get('section', '')),
        ]
        if has_sub_event:
            row.append(str(p.get('sub_event_name', '-') or '-'))
        row.append(status.upper())
        rows.append(row)

    # Column widths
    if has_sub_event:
        col_widths = [0.7 * cm, 4.5 * cm, 2.5 * cm, 2.5 * cm, 1 * cm, 2.5 * cm, 2.5 * cm]
    else:
        col_widths = [0.8 * cm, 5 * cm, 3 * cm, 3 * cm, 1.2 * cm, 3 * cm]

    p_table = Table(rows, colWidths=col_widths, repeatRows=1)

    # Base style
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#DEE2E6')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, MSV_LIGHT]),
    ]

    # Color attendance rows
    for i, p in enumerate(participants, 1):
        status = p.get('attendance_status', 'pending')
        last_col = -1
        if status == 'present':
            t_style.append(('TEXTCOLOR', (last_col, i), (last_col, i), colors.HexColor('#155724')))
            t_style.append(('BACKGROUND', (last_col, i), (last_col, i), PRESENT_COLOR))
        elif status == 'absent':
            t_style.append(('TEXTCOLOR', (last_col, i), (last_col, i), colors.HexColor('#721C24')))
            t_style.append(('BACKGROUND', (last_col, i), (last_col, i), ABSENT_COLOR))
        else:
            t_style.append(('TEXTCOLOR', (last_col, i), (last_col, i), colors.HexColor('#856404')))
            t_style.append(('BACKGROUND', (last_col, i), (last_col, i), PENDING_COLOR))

    p_table.setStyle(TableStyle(t_style))
    story.append(p_table)
    story.append(Spacer(1, 24))

    # ------------------------------------------------------------------
    # Footer / Signatures
    # ------------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=1, color=MSV_GOLD))
    story.append(Spacer(1, 10))

    sig_data = [
        ["Event Incharge", "", "Principal"],
        ["Signature & Seal", "", "MS College"]
    ]
    sig_table = Table(sig_data, colWidths=[None, 3 * cm, None])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), MSV_DARK),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            f"Generated by MS College Events Management System | {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            footer_style
        )
    )

    doc.build(story)
    return filepath


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bold_para(text, style):
    from reportlab.platypus import Paragraph
    return Paragraph(f"<b>{text}</b>", style)


def _section_header(text, bg_color):
    """Return a colored section header paragraph wrapped in a Table."""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT

    header_style = ParagraphStyle(
        'SH',
        fontSize=11,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        leftPadding=8,
        rightPadding=8,
        topPadding=5,
        bottomPadding=5
    )
    p = Paragraph(text, header_style)
    t = Table([[p]], colWidths=['100%'])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('PADDING', (0, 0), (-1, -1), 0),
    ]))
    return t
