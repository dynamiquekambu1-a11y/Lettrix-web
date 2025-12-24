from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
from werkzeug.utils import secure_filename

from generator import generate_text
from utils import export_to_word, export_to_pdf, validate_required_fields

app = Flask(__name__)
app.secret_key = "secure_internship_key"

os.makedirs("export/word", exist_ok=True)
os.makedirs("export/pdf", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html",
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
        date="",
        company_logo="static/logo.png",
        generated_text=""
    )


@app.route("/generate", methods=["POST"])
def generate():
    form = request.form.to_dict()

    file = request.files.get("company_logo_file")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join("static/uploads", filename)
        file.save(path)
        form["company_logo"] = path.replace("\\", "/")
    else:
        form["company_logo"] = form.get("company_logo", "static/logo.png")

    missing = validate_required_fields(
        form,
        required=["applicant_name", "email", "company_name", "internship_position"]
    )

    if missing:
        flash(f"Missing required fields: {', '.join(missing)}", "danger")
        return render_template("index.html", generated_text="", **form)

    generated_text = generate_text(form)["full_text"]

    return render_template("index.html", generated_text=generated_text, **form)


@app.route("/preview", methods=["POST"])
def preview():
    form = request.form.to_dict()
    return render_template("preview.html",
        generated_text=form.get("generated_text", ""),
        fields=form
    )


@app.route("/export/word", methods=["POST"])
def export_word_route():
    form = request.form.to_dict()
    filename = export_to_word(form.get("generated_text", ""), form)
    return send_file(filename, as_attachment=True)


@app.route("/export/pdf", methods=["POST"])
def export_pdf_route():
    form = request.form.to_dict()
    filename = export_to_pdf(form.get("generated_text", ""), form)
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
