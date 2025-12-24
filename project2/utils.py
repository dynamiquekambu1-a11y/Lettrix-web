import os, datetime
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4


EXPORT_WORD_DIR = "export/word"
EXPORT_PDF_DIR = "export/pdf"
os.makedirs(EXPORT_WORD_DIR, exist_ok=True)
os.makedirs(EXPORT_PDF_DIR, exist_ok=True)

def make_filename(prefix="document", ext="pdf"):
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{ts}.{ext}"

def export_to_word_leave(text, metadata=None):
    doc = Document()
    doc.add_heading("LEAVE REQUEST LETTER", level=1)
    for line in text.split("\n"):
        if not line.strip():
            doc.add_paragraph()
        else:
            doc.add_paragraph(line)
    filename = make_filename("leave_request","docx")
    path = os.path.join(EXPORT_WORD_DIR, filename)
    doc.save(path)
    return path

def export_leave_pdf(text, metadata=None):
    metadata = metadata or {}
    path = os.path.join(EXPORT_PDF_DIR, f"leave_request_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    title_style = ParagraphStyle("Title", fontSize=16, alignment=TA_CENTER, textColor=HexColor("#0033cc"))
    normal = ParagraphStyle("Normal", fontSize=11, leading=14, alignment=TA_JUSTIFY)
    right_style = ParagraphStyle("Right", fontSize=11, alignment=TA_RIGHT)
    footer_style = ParagraphStyle("Footer", fontSize=9, alignment=TA_RIGHT, textColor=HexColor("#888888"))

    logo = metadata.get("company_logo","")
    if logo and os.path.exists(logo):
        img = Image(logo, width=3*cm, height=3*cm)
        img.hAlign = "RIGHT"
        story.append(img)

    company_name = metadata.get("company_name","")
    if company_name:
        story.append(Paragraph(company_name, title_style))
        story.append(Spacer(1,6))
        story.append(HRFlowable(width="100%", color=HexColor("#0033cc")))
        story.append(Spacer(1,10))

    for p in text.split("\n\n"):
        story.append(Paragraph(p.replace("\n","<br/>"), normal))
        story.append(Spacer(1,6))

    story.append(Spacer(1,12))
    story.append(Paragraph("This letter was generated professionally using LETTRIX – WEB.", footer_style))

    def add_watermark(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Bold",60)
        canvas.setFillColor(Color(0.6,0.6,0.6,alpha=0.12))
        canvas.translate(300,400)
        canvas.rotate(45)
        canvas.drawCentredString(0,0,"LETTRIX – WEB")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
    return path

def validate_required_fields(data: dict, required=None):
    required = required or []
    missing = []
    for k in required:
        if not data.get(k) or not str(data.get(k)).strip():
            missing.append(k)
    return missing
