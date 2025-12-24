from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
from werkzeug.utils import secure_filename

from generator import generate_text
from utils import export_to_word, export_to_pdf, validate_required_fields

app = Flask(__name__)
app.secret_key = "change_this_to_a_secure_random_key"

# Create necessary folders
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
        "applicant_address": "",
        "applicant_email": "",
        "company_logo": "static/uploads",

        # ---- NEW FIELDS ----
        "applicant_name": "",
        "company_email": "",
        "company_phone": "",
        "why_you_want": "",
        "company_address": "",
        "position_applied": "",
        "skills": "",
        "experience_years": "",
        "achievements": "",
        "cover_letter_text": "",
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

    # ----- HANDLE LOGO UPLOAD -----
    file = request.files.get("company_logo_file")
    if file and allowed_file(file.filename) and file.filename.strip():
        filename = secure_filename(file.filename)
        upload_folder = "static/uploads"
        save_path = os.path.join(upload_folder, filename)
        file.save(save_path)
        form["company_logo"] = save_path.replace("\\", "/")
    else:
        if not form.get("company_logo"):
            form["company_logo"] = "static/logo.png"

    # ----- REQUIRED -----
    missing = validate_required_fields(form, required=["company_name", "applicant_name"])
    if missing:
        flash(f"Missing required fields: {', '.join(missing)}", "danger")
        return render_template("index.html", generated_text="", **form)

    # ----- EXTRA FIELDS (VERY IMPORTANT) -----
    form["applicant_email"] = form.get("applicant_email", "")
    form["applicant_phone"] = form.get("applicant_phone", "")
    form["why_you_want"] = form.get("why_you_want", "")
    form["skills"] = form.get("skills", "")
    form["experience_years"] = form.get("experience_years", "")
    form["achievements"] = form.get("achievements", "")
    form["cover_letter_text"] = form.get("cover_letter_text", "")
    form["company_email"] = form.get("company_email", "")
    form["company_phone"] = form.get("company_phone", "")
    form["company_address"] = form.get("company_address", "")

    # ----- GENERATE THE TEXT -----
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

    # Pass the entire form as metadata to include company + applicant info
    filename = export_to_pdf(metadata=form, text=text)
    return send_file(filename, as_attachment=True)


# ==============================
#            RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True, port=5004)
