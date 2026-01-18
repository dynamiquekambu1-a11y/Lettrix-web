from flask import Flask, render_template, redirect, url_for, session, request, flash
import sqlite3
from datetime import date, datetime
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Response

# ----- Import des mini-apps -----
from certificate_work.app import app as work_certificate_app
from job_application_app.app import app as job_application_app
from project_intership.app import app as project_internship_app
from project2.app import app as project2_app
from projects.app import app as projects_app

from flask import Response, url_for

# ================= FLASK PRINCIPAL =================
app = Flask(__name__)
app.secret_key = "LETTRIX_SECRET_KEY"

DB_NAME = "database.db"

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            visit_date TEXT PRIMARY KEY,
            count INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mini_app TEXT,
            action TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS exports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            export_date TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


# ================= VISITORS COUNTER =================
@app.before_request
def count_visits():
    if not session.get("visited_today"):
        today = date.today().isoformat()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT count FROM visits WHERE visit_date = ?", (today,))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE visits SET count = count + 1 WHERE visit_date = ?", (today,))
        else:
            cur.execute("INSERT INTO visits (visit_date, count) VALUES (?, 1)", (today,))
        conn.commit()
        conn.close()
        session["visited_today"] = True  # empêche les reloads de gonfler le compteur

# ================= AUTH =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("Missing fields")
            return redirect(url_for("register"))
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            conn.commit()
            flash("Account created. Please login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["is_admin"] = user["is_admin"]
            flash("Login successful")
            return redirect(url_for("home"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out")
    return redirect(url_for("home"))

# ================= HOME =================
@app.route("/")
def home():
    conn = get_db()
    cur = conn.cursor()

    # visiteurs aujourd'hui
    cur.execute(
        "SELECT count FROM visits WHERE visit_date = ?",
        (date.today().isoformat(),)
    )
    today_row = cur.fetchone()
    visitors_today = today_row["count"] if today_row else 0

    # visiteurs total (somme de tous les jours)
    cur.execute("SELECT SUM(count) AS total FROM visits")
    total_row = cur.fetchone()
    visitors_total = total_row["total"] if total_row["total"] else 0

    conn.close()

    return render_template(
        "home.html",
        visitors_today=visitors_today,
        visitors_total=visitors_total
    )
def log_event(mini_app, action):
    if not session.get("user_id"):
        return

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO analytics (user_id, mini_app, action, created_at) VALUES (?, ?, ?, ?)",
        (
            session["user_id"],
            mini_app,
            action,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    conn.commit()
    conn.close()

def can_export_today():
    if not session.get("user_id"):
        return False

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM exports WHERE user_id = ? AND export_date = ?",
        (session["user_id"], date.today().isoformat())
    )
    count = cur.fetchone()[0]
    conn.close()

    return count < 3





# ================= EXPORT CONTROL =================
@app.route("/can-export")
def can_export():
    return "YES"

# ================= COMMENTS =================
@app.route("/comments", methods=["GET", "POST"])
def comments():
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        name = request.form.get("name")
        message = request.form.get("message")
        if name and message:
            cur.execute(
                "INSERT INTO comments (name, message, created_at) VALUES (?, ?, ?)",
                (name, message, datetime.now().strftime("%Y-%m-%d %H:%M"))
            )
            conn.commit()
            return redirect(url_for("comments"))
    cur.execute("SELECT * FROM comments ORDER BY id DESC")
    comments_list = cur.fetchall()
    conn.close()
    return render_template("comments.html", comments=comments_list)

# ================= CONTACT =================
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        new_message = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "message": request.form.get("message"),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        os.makedirs("data", exist_ok=True)
        path = "data/messages.json"
        messages = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                messages = json.load(f)
        messages.append(new_message)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        flash("Your message has been sent successfully.")
    return render_template("contact.html")

# ================= ADMIN DASHBOARD =================
@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT visit_date, count FROM visits ORDER BY visit_date")
    visits = cur.fetchall()
    cur.execute("SELECT COUNT(*) as total FROM comments")
    comments_count = cur.fetchone()["total"]
    cur.execute("SELECT name, message, created_at FROM comments ORDER BY id DESC LIMIT 10")
    comments = cur.fetchall()
    conn.close()
    return render_template("admin.html", visits=visits, comments_count=comments_count, comments=comments)

# ================= STATIC PAGES =================
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html", last_update=date.today().strftime("%Y-%m-%d"))

@app.route("/terms")
def terms():
    return render_template("terms.html")

from flask import Response, url_for

# ---------------- SEO DATA ----------------
SEO_DATA = {
    "projects": {
        "title": "Lettrix – Resignation Letter Generator",
        "description": "Create professional resignation letters quickly and easily with Lettrix.",
        "og_image": "/static/images/result1.png"
    },
    "job_application": {
        "title": "Lettrix – Job Application Letter Generator",
        "description": "Generate professional job application letters with Lettrix. Save time, impress recruiters, and increase your chances of success.",
        "og_image": "/static/images/result2.png"
    },
    "project_internship": {
        "title": "Lettrix – Internship Request Letter Generator",
        "description": "Easily create polished internship request letters using Lettrix. Stand out to your future mentors and companies.",
        "og_image": "/static/images/result3.png"
    },
    "work_certificate": {
        "title": "Lettrix – Work Certificate Generator",
        "description": "Automatically generate professional work certificates for employees or clients using Lettrix.",
        "og_image": "/static/images/result1.png"
    },
    "project2": {
        "title": "Lettrix – Leave Request Letter Generator",
        "description": "Create official leave request letters in seconds with Lettrix. Templates are ready to use and professional.",
        "og_image": "/static/images/result2.png"
    }
}

# ---------------- MINI-APP REDIRECT AVEC SEO ----------------
@app.route("/open/<appname>")
def open_app(appname):
    mapping = {
        "work_certificate": "/work_certificate",
        "job_application": "/job_application",
        "project_internship": "/project_internship",
        "project2": "/project2",
        "projects": "/projects"
    }
    log_event(appname, "open")

    if appname not in mapping:
        return "Mini-app non trouvée", 404

    seo = SEO_DATA.get(appname, {})
    page_title = seo.get("title")
    page_description = seo.get("description")
    og_image = seo.get("og_image")
    canonical_url = f"https://lettrix-web.onrender.com/open/{appname}"

    return render_template(
        "open_redirect.html",
        target_url=mapping[appname],
        page_title=page_title,
        page_description=page_description,
        og_image=og_image,
        canonical_url=canonical_url
    )

# ---------------- SITEMAP XML ----------------
@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    pages = []

    # Pages principales
    pages.append({"loc": url_for("home", _external=True), "priority": "1.0"})
    pages.append({"loc": url_for("about", _external=True), "priority": "0.5"})
    pages.append({"loc": url_for("privacy", _external=True), "priority": "0.5"})
    pages.append({"loc": url_for("terms", _external=True), "priority": "0.5"})
    pages.append({"loc": url_for("contact", _external=True), "priority": "0.5"})
    pages.append({"loc": url_for("comments", _external=True), "priority": "0.6"})

    # Mini-apps
    for appname in SEO_DATA.keys():
        pages.append({"loc": url_for("open_app", appname=appname, _external=True), "priority": "0.9"})

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="https://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        sitemap_xml += f"  <url>\n"
        sitemap_xml += f"    <loc>{page['loc']}</loc>\n"
        sitemap_xml += f"    <priority>{page['priority']}</priority>\n"
        sitemap_xml += f"  </url>\n"
    sitemap_xml += '</urlset>'

    return Response(sitemap_xml, mimetype="application/xml")






# ================= DEBUG =================
print("static trouvés :", os.listdir("static"))

# ================= DISPATCHER POUR RENDER =================
application = DispatcherMiddleware(
    app,
    {
        "/work_certificate": work_certificate_app,
        "/job_application": job_application_app,
        "/project_internship": project_internship_app,
        "/project2": project2_app,
        "/projects": projects_app,
    }
)

# ================= DEV LOCAL =================
if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple(
       "0.0.0.0",
        5000,
        application,
        use_reloader=True,
        use_debugger=True
    )
