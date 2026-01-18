from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
from werkzeug.utils import secure_filename

from .generator import generate_leave_text
from .utils import export_to_word_leave, export_leave_pdf, validate_required_fields

# ----- Flask App avec static_url_path pour DispatcherMiddleware -----
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/project2/static/uploads"  # CHEMIN Render
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
    context = {k: "" for k in [
        "employee_full_name","position","department","company_name","supervisor_name",
        "leave_type","start_date","end_date","total_days","reason","emergency_contact",
        "backup_plan","submission_date","company_logo","signer_name","signer_role"
    ]}
    context["generated_text"] = ""
    context["company_logo"] = "/leave_request/static/logo.png"  # <-- CHEMIN Render
    return render_template("index_leave.html", fields=context, **context)


# ==============================
#          GENERATE
# ==============================
@app.route("/generate_leave", methods=["POST"])
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

    # Champs obligatoires
    required = [
        "employee_full_name", "position", "company_name", "supervisor_name",
        "leave_type", "start_date", "end_date", "total_days", "reason", "submission_date"
    ]

    missing = validate_required_fields(form, required)
    if missing:
        flash(f"Missing required fields: {', '.join(missing)}", "danger")
        return render_template("index_leave.html", generated_text="", fields=form, **form)

    # Générer texte
    result = generate_leave_text(form)
    generated_text = result["full_text"]

    return render_template("index_leave.html", generated_text=generated_text, fields=form, **form)


# ==============================
#            PREVIEW
# ==============================
@app.route("/preview_leave", methods=["POST"], endpoint="preview_leave")
def preview():
    form = request.form.to_dict()
    generated_text = form.get("generated_text", "")
    context = form.copy()
    context["generated_text"] = generated_text
    return render_template("preview_leave.html", **context, fields=form)


# ==============================
#         EXPORT WORD
# ==============================
@app.route("/export_leave/word", methods=["POST"])
def export_word_route():
    form = request.form.to_dict()
    text = form.get("generated_text", "")
    if not text:
        flash("No generated text to export.", "danger")
        return redirect(url_for("index"))
    filename = export_to_word_leave(text, form)
    return send_file(filename, as_attachment=True)


# ==============================
#         EXPORT PDF
# ==============================
@app.route("/export_leave/pdf", methods=["POST"])
def export_pdf_route():
    form = request.form.to_dict()
    text = form.get("generated_text", "")
    if not text:
        flash("No generated text to export.", "danger")
        return redirect(url_for("index"))
    filename = export_leave_pdf(text, form)
    return send_file(filename, as_attachment=True)


# ==============================
#         DEV LOCAL
# ==============================
if __name__ == "__main__":
    app.run(debug=True, port=5003)
