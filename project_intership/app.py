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
    static_url_path="/project_internship/static/uploads"
)
app.secret_key = "secure_internship_key"

# ----- Créer les dossiers export et uploads si pas existants -----
os.makedirs("export/word", exist_ok=True)
os.makedirs("export/pdf", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- HOME -----------------
@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        applicant_name="",
        email="",
        phone="",
        university="",
        field_of_study="",
        current_level="",
        company_name="",
        internship_position="",
        motivation="",
        key_skills="",
        academic_projects="",
        internship_duration="",
        letter_date="",
        company_logo="/project_internship/static/uploads",  # chemin par défaut
        generated_text=""
    )

# ----------------- GENERATE -----------------
@app.route("/generate", methods=["POST"])
def generate():
    form = request.form.to_dict()

    # --- Upload du logo ---
    file = request.files.get("company_logo_file")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join("static/uploads", filename)
        file.save(upload_path)
        # ⚡ On met le chemin relatif correct pour utils.py
        form["company_logo"] = upload_path.replace("\\", "/")
    else:
        form["company_logo"] = form.get("company_logo", "static/logo.png")

    # --- Champs obligatoires ---
    missing = validate_required_fields(
        form,
        required=["applicant_name", "email", "company_name", "internship_position"]
    )
    if missing:
        flash(f"Missing required fields: {', '.join(missing)}", "danger")
        return render_template("index.html", generated_text="", **form)

    # --- Génération du texte automatique ---
    generated_text = generate_text(form)["full_text"]

    # ⚡ Ajouter chemin absolu du logo pour export PDF
    form["company_logo_path"] = os.path.abspath(form["company_logo"])

    return render_template("index.html", generated_text=generated_text, **form)


# ----------------- PREVIEW -----------------
@app.route("/preview", methods=["POST"])
def preview():
    form = request.form.to_dict()
    return render_template(
        "preview.html",
        generated_text=form.get("generated_text", ""),
        fields=form
    )

# ----------------- EXPORT WORD -----------------
@app.route("/export/word", methods=["POST"])
def export_word_route():
    form = request.form.to_dict()
    text = form.get("generated_text", "")
    filepath = export_to_word(text, form)
    return send_file(filepath, as_attachment=True)

# ----------------- EXPORT PDF -----------------
@app.route("/export/pdf", methods=["POST"])
def export_pdf_route():
    form = request.form.to_dict()
    text = form.get("generated_text", "")
    filepath = export_to_pdf(text, form)
    return send_file(filepath, as_attachment=True)

# ----------------- DEV LOCAL -----------------
if __name__ == "__main__":
    app.run(debug=True, port=5002)
