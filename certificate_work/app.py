from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
from werkzeug.utils import secure_filename

from .generator import generate_text
from .utils import export_to_word, export_to_pdf, validate_required_fields

# ----- Flask App avec static_url_path pour DispatcherMiddleware -----
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/work_certificate/static/uploads"  # CHEMIN Render
)
app.secret_key = "secure_work_certificate_key"

# ----- Créer dossiers export et uploads si pas existants -----
os.makedirs("export/word", exist_ok=True)
os.makedirs("export/pdf", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ==============================
#            HOME
# ==============================
@app.route("/", methods=["GET"])
def index():
    context = {
        "company_name": "",
        "company_address": "",
        "company_phone": "",
        "company_email": "",
        "company_logo": "/work_certificate/static/uploads",  # CHEMIN Render

        "employee_name": "",
        "position": "",
        "department": "",
        "start_date": "",
        "end_date": "",
        "contract_type": "",
        "work_summary": "",
        "skills": "",
        "behaviour": "",
        "final_statement": "",
        "signer_name": "",
        "signer_role": "",
        "signature_place": "",
        "signature_date": "",
        "generated_text": ""
    }
    return render_template("index.html", **context)


# ==============================
#          GENERATE
# ==============================
@app.route("/generate", methods=["POST"])
def generate():
    form = request.form.to_dict()

    file = request.files.get("company_logo_file")
    if file and allowed_file(file.filename) and file.filename.strip():
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(app.root_path, "static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        save_path = os.path.join(upload_folder, filename)
        file.save(save_path)

        # 🔴 CHEMIN DISQUE RELATIF POUR ReportLab
        form["company_logo"] = os.path.join("static", "uploads", filename).replace("\\", "/")
    else:
        form["company_logo"] = ""

    missing = validate_required_fields(form, required=["company_name", "employee_name"])
    if missing:
        flash(f"Missing required fields: {', '.join(missing)}", "danger")
        return render_template("index.html", generated_text="", **form)

    result = generate_text(form)
    generated_text = result["full_text"]

    return render_template("index.html", generated_text=generated_text, **form)


# ==============================
#            PREVIEW
# ==============================
@app.route("/preview", methods=["POST"])
def preview():
    form = request.form.to_dict()
    generated_text = form.get("generated_text", "")
    return render_template("preview.html", generated_text=generated_text, fields=form)


# ==============================
#         EXPORT WORD
# ==============================
@app.route("/export/word", methods=["POST"])
def export_word_route():
    form = request.form.to_dict()
    text = form.get("generated_text", "")
    if not text:
        flash("No generated text to export.", "danger")
        return redirect(url_for("index"))
    filename = export_to_word(text, form)
    return send_file(filename, as_attachment=True)


# ==============================
#         EXPORT PDF
# ==============================
@app.route("/export/pdf", methods=["POST"])
def export_pdf_route():
    form = request.form.to_dict()
    text = form.get("generated_text", "")
    if not text:
        flash("No generated text to export.", "danger")
        return redirect(url_for("index"))
    filename = export_to_pdf(text, form)
    return send_file(filename, as_attachment=True)


# ==============================
#         DEV LOCAL
# ==============================
if __name__ == "__main__":
    app.run(debug=True, port=5003)
