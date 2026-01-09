from flask import Flask, render_template, redirect, url_for, session, request, flash
import sqlite3
from datetime import date, datetime
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# ----- Import des mini-apps -----
from certificate_work.app import app as work_certificate_app
from job_application_app.app import app as job_application_app
from project_intership.app import app as project_internship_app
from project2.app import app as project2_app
from projects.app import app as projects_app

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
    conn.commit()
    conn.close()

init_db()

# ================= VISITORS COUNTER =================
@app.before_request
def count_visits():
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
    cur.execute("SELECT count FROM visits WHERE visit_date = ?", (date.today().isoformat(),))
    row = cur.fetchone()
    visitors_today = row["count"] if row else 0
    conn.close()
    return render_template("home.html", visitors_today=visitors_today)

# ================= MINI APPS via DispatcherMiddleware =================
@app.route("/open/<appname>")
def open_app(appname):
    mapping = {
        "work_certificate": "/work_certificate",
        "job_application": "/job_application",
        "project_internship": "/project_internship",
        "project2": "/project2",
        "projects": "/projects"
    }
    if appname not in mapping:
        return "Mini-app non trouvée", 404
    return redirect(mapping[appname] + "/")

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
