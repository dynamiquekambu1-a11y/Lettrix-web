
import os
import datetime

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import cm
from reportlab.lib.colors import black, HexColor
from reportlab.lib.colors import Color

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, HRFlowable
from reportlab.lib.colors import black, HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor


EXPORT_WORD_DIR = "export/word"
EXPORT_PDF_DIR = "export/pdf"

def make_filename(prefix="file", ext="pdf"):
    import datetime
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{ts}.{ext}"

# ---------------------------
# Export Word
# ---------------------------
def export_to_word(text, metadata=None):
    metadata = metadata or {}
    applicant = metadata.get("applicant_name", "applicant").strip() or "applicant"
    safe_name = applicant.replace(" ", "_")
    filename = f"{safe_name}_Job_Application.docx"
    path = os.path.join(EXPORT_WORD_DIR, filename)

    doc = Document()

    # Title
    doc.add_heading("JOB APPLICATION LETTER", level=1)

    # Header table: Company info vs Applicant info
    company_name = metadata.get("company_name", "")
    company_address = metadata.get("company_address", "")
    company_email = metadata.get("company_email", "")
    company_phone = metadata.get("company_phone", "")

    applicant_email = metadata.get("applicant_email", "")
    applicant_phone = metadata.get("applicant_phone", "")

    if any([company_name, company_address, company_email, company_phone,
            applicant, applicant_email, applicant_phone]):
        table = doc.add_table(rows=1, cols=2)
        table.autofit = True
        # Left cell = Company
        left_cell = table.cell(0,0)
        left_text = "\n".join(filter(None, [
            company_name, company_address,
            f"Email: {company_email}" if company_email else "",
            f"Phone: {company_phone}" if company_phone else ""
        ]))
        left_cell.text = left_text
        # Right cell = Applicant
        right_cell = table.cell(0,1)
        right_text = "\n".join(filter(None, [
            f"Applicant: {applicant}",
            f"Email: {applicant_email}" if applicant_email else "",
            f"Phone: {applicant_phone}" if applicant_phone else ""
        ]))
        right_cell.text = right_text

    doc.add_paragraph()  # Spacer

    # Add the text, preserve paragraphs
    for line in text.split("\n"):
        if not line.strip():
            doc.add_paragraph()
        else:
            p = doc.add_paragraph(line)
            p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

    # Optional signature block
    signer = metadata.get("signer_name", "").strip()
    signer_role = metadata.get("signer_role", "").strip()
    if signer or signer_role:
        doc.add_paragraph()
        s = doc.add_paragraph()
        s.add_run("Sincerely,\n")
        if signer:
            s.add_run(f"{signer}\n")
        if signer_role:
            s.add_run(f"{signer_role}\n")

    # Adjust default font size
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    doc.save(path)
    return path

def export_to_word(text, metadata=None):
    """
    Export the generated letter to a .docx file.
    - title: JOB APPLICATION LETTER
    - preserve paragraphs
    """
    metadata = metadata or {}
    applicant = metadata.get("applicant_name", "applicant").strip() or "applicant"
    safe_name = applicant.replace(" ", "_")
    filename = f"{safe_name}_Job_Application.docx"
    path = os.path.join(EXPORT_WORD_DIR, filename)

    doc = Document()

    # Title
    doc.add_heading("JOB APPLICATION LETTER", level=1)

    # Optional company header
    company = metadata.get("company_name", "").strip()
    if company:
        p = doc.add_paragraph(company)
        p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # Add the text, preserve blank lines as paragraphs
    for line in text.split("\n"):
        if not line.strip():
            doc.add_paragraph()
        else:
            p = doc.add_paragraph(line)
            p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

    # Optional signature block
    signer = metadata.get("signer_name", "").strip()
    signer_role = metadata.get("signer_role", "").strip()
    if signer or signer_role:
        doc.add_paragraph()
        s = doc.add_paragraph()
        s.add_run("Sincerely,\n")
        if signer:
            s.add_run(f"{signer}\n")
        if signer_role:
            s.add_run(f"{signer_role}\n")

    # Adjust default font size (normal style)
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    doc.save(path)
    return path



def export_to_pdf(text, metadata=None):
    metadata = metadata or {}

    company_name = metadata.get("company_name", "")
    company_address = metadata.get("company_address", "")
    applicant_name = metadata.get("applicant_name", "")
    position_applied = metadata.get("position_applied", "")
    skills = metadata.get("skills", "")
    experience_years = metadata.get("experience_years", "")
    achievements = metadata.get("achievements", "")
    cover_letter_text = metadata.get("cover_letter_text", "")
    signer_name = metadata.get("signer_name", "")
    signer_role = metadata.get("signer_role", "")
    signature_place = metadata.get("signature_place", "")
    signature_date = metadata.get("signature_date", "")
    logo = metadata.get("company_logo", "static/logo.png").replace("\\", "/")
    applicant_email = metadata.get("applicant_email", "")
    applicant_phone = metadata.get("applicant_phone", "")
    company_phone = metadata.get("company_phone", "")
    company_email = metadata.get("company_email", "")

    safe_app = (applicant_name or "applicant").replace(" ", "_")
    filename = make_filename(prefix=f"{safe_app}_job_application", ext="pdf")
    path = os.path.join(EXPORT_PDF_DIR, filename)

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=1.6*cm,
        rightMargin=1.6*cm,
        topMargin=1.2*cm,
        bottomMargin=1.2*cm
    )

    story = []

    approx_lines = sum(len(p.splitlines()) for p in text.split("\n\n"))
    font_size = 11 if approx_lines < 45 else 9

    title_style = ParagraphStyle(
        "Title", fontSize=16, alignment=TA_CENTER,
        fontName="Helvetica-Bold", textColor=HexColor("#0066cc")
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", fontSize=9, alignment=TA_CENTER, textColor=HexColor("#666666")
    )
    normal = ParagraphStyle(
        "Normal", fontSize=font_size, leading=font_size+3, alignment=TA_JUSTIFY
    )
    heading_style = ParagraphStyle(
        "Heading", fontSize=font_size+1, fontName="Helvetica-Bold",
        textColor=HexColor("#ff8c00")
    )
    small_center = ParagraphStyle(
        "SmallCenter", fontSize=8, alignment=TA_CENTER, textColor=HexColor("#666666")
    )
    signature_style = ParagraphStyle(
        "Signature", fontSize=9, alignment=TA_RIGHT, italic=True
    )

    def add_watermark(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(Color(0.6, 0.6, 0.6, alpha=0.18))
        canvas.setFont("Helvetica-Bold", 48)
        canvas.translate(A4[0] / 2, A4[1] / 2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "LETTRIX")
        canvas.restoreState()

    if os.path.exists(logo):
        img = Image(logo, width=2.5*cm, height=2.5*cm)
        img.hAlign = "RIGHT"
        story.append(img)

    if company_name:
        story.append(Paragraph(company_name, title_style))
    header = []
    if company_address:
        header.append(company_address)
    contacts = []
    if company_phone:
        contacts.append(f"Phone: {company_phone}")
    if company_email:
        contacts.append(f"Email: {company_email}")
    if contacts:
        header.append(" | ".join(contacts))
    if header:
        story.append(Paragraph("<br/>".join(header), subtitle_style))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=black))
    story.append(Spacer(1, 8))

    story.append(Paragraph("JOB APPLICATION LETTER", title_style))
    story.append(Spacer(1, 10))

    info_rows = []
    if applicant_name: info_rows.append(["Applicant:", applicant_name])
    if applicant_email: info_rows.append(["Email:", applicant_email])
    if applicant_phone: info_rows.append(["Phone:", applicant_phone])
    if position_applied: info_rows.append(["Position:", position_applied])
    if experience_years: info_rows.append(["Experience:", experience_years])
    if skills: info_rows.append(["Skills:", skills])

    if info_rows:
        tbl = Table(info_rows, colWidths=[120, doc.width-120])
        tbl.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 10))

    story.append(Paragraph("Dear Hiring Manager,", normal))
    story.append(Spacer(1, 4))

    for p in text.split("\n\n"):
        if p.strip():
            story.append(Paragraph(p.replace("\n", "<br/>"), normal))
            story.append(Spacer(1, 4))

    if achievements:
        story.append(Paragraph("Key achievements:", heading_style))
        story.append(Paragraph(achievements, normal))

    if cover_letter_text:
        story.append(Paragraph("Additional notes:", heading_style))
        story.append(Paragraph(cover_letter_text, normal))

    story.append(Spacer(1, 24))

    sig_lines = []
    if signature_place or signature_date:
        sig_lines.append(f"{signature_place}, {signature_date}".strip(", "))
    if signer_name:
        sig_lines.append(f"<b>{signer_name}</b>")
    if signer_role:
        sig_lines.append(signer_role)

    if sig_lines:
        story.append(Paragraph("<br/>".join(sig_lines), signature_style))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "This letter was generated by Lettrix - Job Application Generator.",
        small_center
    ))

    doc.build(
        story,
        onFirstPage=add_watermark,
        onLaterPages=add_watermark
    )

    return path


def validate_required_fields(data: dict, required=None):
    required = required or []
    missing = []
    for k in required:
        if not data.get(k) or not str(data.get(k)).strip():
            missing.append(k)
    return missing