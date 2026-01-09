from flask import Flask, render_template, request, send_file
import os
from .util import export_to_word, export_to_pdf  # assure-toi que utils.py est dans le même dossier

# ----- Flask App avec static_url_path pour DispatcherMiddleware -----
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/projects/static/uplaods"  # <-- IMPORTANT pour Render
)
app.secret_key = "secure_resignation_key"

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
    return render_template("index.html",
                           company_name="",
                           company_email="",
                           company_phone="",
                           employee_full_name="",
                           current_job_title="",
                           manager_name="",
                           letter_date="",
                           last_working_day="",
                           reason_for_resignation="",
                           thank_you_message="",
                           transition_help="",
                           generated_text=None,
                           fields={})

# ----------------- GENERATE -----------------
@app.route("/generate", methods=["POST"])
def generate():
    form = request.form.to_dict()

    file = request.files.get("company_logo_file")
    if file and allowed_file(file.filename) and file.filename.strip():
        filename = file.filename.replace(" ", "_")
        path = os.path.join("static/uploads", filename)
        file.save(path)
        # On renvoie le chemin relatif pour utils.py
        form["company_logo"] = path.replace("\\", "/")
    else:
        form["company_logo"] = "static/logo.png"  # logo par défaut

    generated_text = f"""
{form.get('company_name','')}
Email: {form.get('company_email','')} | Phone: {form.get('company_phone','')}

Date: {form.get('letter_date','')}

To: {form.get('manager_name','')}

Subject: Resignation Letter

Dear {form.get('manager_name','')},

I am writing to formally resign from my position as {form.get('current_job_title','')} at {form.get('company_name','')}, effective {form.get('last_working_day','')}.

{form.get('reason_for_resignation','')}

I sincerely thank you and the entire team for the opportunities I have had during my tenure.

{form.get('thank_you_message','')}

I am willing to assist with the transition: {form.get('transition_help','')}

Sincerely,
{form.get('employee_full_name','')}
"""
    fields = form.copy()
    fields["generated_text"] = generated_text

    return render_template("index.html",
                           generated_text=generated_text,
                           fields=fields,
                           **form)

# ----------------- PREVIEW -----------------
@app.route("/preview", methods=["POST"])
def preview():
    fields = request.form.to_dict()
    generated_text = fields.get("generated_text", "")
    return render_template("preview.html",
                           generated_text=generated_text,
                           fields=fields)

# ----------------- EXPORT -----------------
@app.route("/export_word_route", methods=["POST"])
def export_word_route():
    fields = request.form.to_dict()
    text = fields.get("generated_text", "")
    path = export_to_word(text, metadata=fields)
    return send_file(path, as_attachment=True)

@app.route("/export_pdf_route", methods=["POST"])
def export_pdf_route():
    fields = request.form.to_dict()
    text = fields.get("generated_text", "")
    path = export_to_pdf(text, metadata=fields)
    return send_file(path, as_attachment=True)

# ----------------- DEV LOCAL -----------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
