import os
import datetime

from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import cm
from reportlab.lib.colors import black, HexColor

EXPORT_WORD_DIR = "export/word"
EXPORT_PDF_DIR = "export/pdf"

os.makedirs(EXPORT_WORD_DIR, exist_ok=True)
os.makedirs(EXPORT_PDF_DIR, exist_ok=True)

def make_filename(prefix="certificate", ext="pdf"):
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{ts}.{ext}"

def export_to_word(text, metadata=None):
    doc = Document()
    doc.add_heading("WORK CERTIFICATE", level=1)

    for line in text.split("\n"):
        if not line.strip():
            doc.add_paragraph()
        else:
            doc.add_paragraph(line)

    filename = make_filename(prefix="certificate", ext="docx")
    path = os.path.join(EXPORT_WORD_DIR, filename)
    doc.save(path)
    return path

def export_to_pdf(text, metadata=None):
    metadata = metadata or {}

    # --- Données employé / société ---
    company_name = metadata.get("company_name", "")
    company_address = metadata.get("company_address", "")
    company_phone = metadata.get("company_phone", "")
    company_email = metadata.get("company_email", "")
    employee_name = metadata.get("employee_name", "")
    position = metadata.get("position", "")
    department = metadata.get("department", "")
    start_date = metadata.get("start_date", "")
    end_date = metadata.get("end_date", "")
    contract_type = metadata.get("contract_type", "")
    work_summary = metadata.get("work_summary", "")
    skills = metadata.get("skills", "")
    behaviour = metadata.get("behaviour", "")
    final_statement = metadata.get("final_statement", "")
    signer_name = metadata.get("signer_name", "")
    signer_role = metadata.get("signer_role", "")
    signature_place = metadata.get("signature_place", "")
    signature_date = metadata.get("signature_date", "")
    logo = metadata.get("company_logo", "static/logo.png").replace("\\", "/")

    filename = make_filename(prefix="certificate", ext="pdf")
    path = os.path.join(EXPORT_PDF_DIR, filename)

    # --- Marges réduites ---
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    story = []

    # --- Estimation de la taille de police auto ---
    base_font_size = 10
    num_lines = len(text.split("\n")) + sum([bool(work_summary), bool(skills), bool(behaviour), bool(final_statement)])
    font_size = max(7, base_font_size - max(0, (num_lines - 40) * 0.15))

    # --- Styles adaptatifs ---
    title_style = ParagraphStyle("Title", fontSize=16, alignment=TA_CENTER, leading=18,
                                 fontName="Helvetica-Bold", textColor=HexColor("#0033cc"))
    subtitle_style = ParagraphStyle("Subtitle", fontSize=9, alignment=TA_CENTER, leading=11, textColor=HexColor("#666666"))
    heading_style = ParagraphStyle("Heading", fontSize=font_size + 1, fontName="Helvetica-Bold", leading=font_size + 2,
                                   spaceBefore=6, textColor=HexColor("#d4af37"))
    normal = ParagraphStyle("Normal", fontSize=font_size, leading=font_size + 2, alignment=TA_JUSTIFY)
    small_center = ParagraphStyle("SmallCenter", fontSize=font_size - 2, alignment=TA_CENTER, textColor=HexColor("#666666"))
    right_style = ParagraphStyle("Right", fontSize=font_size, alignment=TA_RIGHT, fontName="Helvetica-Bold")

    # --- Logo dynamique ---
    if os.path.exists(logo):
        try:
            max_logo_height = 3 * cm
            if num_lines > 60:
                max_logo_height = 2 * cm
            elif num_lines > 80:
                max_logo_height = 1.5 * cm

            img = Image(logo, width=max_logo_height, height=max_logo_height)
            img.hAlign = "RIGHT"
            story.append(img)
        except:
            pass

    # --- Watermark plus visible ---
    from reportlab.lib.colors import Color
    def add_watermark(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 70)  # plus grand
        canvas.setFillColor(Color(0.6, 0.6, 0.6, alpha=0.15))  # plus foncé et visible
        canvas.translate(300, 400)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "LETTRIX - WEB")
        canvas.restoreState()


    # --- Company info ---
    if company_name:
        story.append(Paragraph(company_name, title_style))

    header_lines = []
    if company_address:
        header_lines.append(company_address)
    contact = []
    if company_phone:
        contact.append(f"Phone: {company_phone}")
    if company_email:
        contact.append(f"Email: {company_email}")
    if contact:
        header_lines.append(" | ".join(contact))
    if header_lines:
        story.append(Paragraph("<br/>".join(header_lines), subtitle_style))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=black))
    story.append(Spacer(1, 6))

    # --- Document title ---
    story.append(Paragraph("WORK CERTIFICATE", title_style))
    story.append(Spacer(1, 6))

    # --- Table employee data ---
    info_rows = []
    if employee_name:
        info_rows.append(["Employee:", employee_name])
    if position:
        info_rows.append(["Position:", position])
    if department:
        info_rows.append(["Department:", department])
    if contract_type:
        info_rows.append(["Contract type:", contract_type])
    if start_date:
        info_rows.append(["Start date:", start_date])
    if end_date:
        info_rows.append(["End date:", end_date])

    if info_rows:
        tbl = Table(info_rows, colWidths=[80, 360])
        tbl.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), font_size),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 6))

    # --- Intro & texte ---
    story.append(Paragraph("To whom it may concern,", normal))
    story.append(Spacer(1, 4))

    for paragraph in text.split("\n\n"):
        if paragraph.strip():
            story.append(Paragraph(paragraph.replace("\n", "<br/>"), normal))
            story.append(Spacer(1, 4))

    # --- Sections facultatives ---
    if work_summary:
        story.append(Paragraph("Work summary:", heading_style))
        story.append(Paragraph(work_summary, normal))
    if skills:
        story.append(Paragraph("Skills & competencies:", heading_style))
        story.append(Paragraph(skills, normal))
    if behaviour:
        story.append(Paragraph("Professional conduct:", heading_style))
        story.append(Paragraph(behaviour, normal))
    if final_statement:
        story.append(Paragraph(final_statement, normal))

    story.append(Spacer(1, 16))

    # --- Signature ---
    sig_lines = []
    if signer_name:
        sig_lines.append(signer_name)
    if signer_role:
        sig_lines.append(signer_role)
    if signature_place or signature_date:
        sig_lines.append(f"{signature_place} {signature_date}".strip())
    for ln in sig_lines:
        story.append(Paragraph(ln, right_style))

    story.append(Spacer(1, 12))
    story.append(Paragraph("This certificate is issued upon the request of the concerned employee.", small_center))

    story.append(Spacer(1, 36))
    story.append(Paragraph("Signature: ____________________" ))

    # --- Build PDF avec watermark ---
    doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)

    return path

def validate_required_fields(data: dict, required=None):
    required = required or []
    missing = []
    for k in required:
        if not data.get(k) or not str(data.get(k)).strip():
            missing.append(k)
    return missing