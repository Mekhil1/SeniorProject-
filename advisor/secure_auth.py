"""Account and academic record security; local development only."""
import io
import json
import re
import secrets
import sqlite3
import time
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request, session
from flask_login import UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from pypdf import PdfReader
from .degreeworks_parser import parse_degreeworks

auth_bp = Blueprint("secure_auth", __name__)
_attempts = {}  # development-only limiter; replace with shared persistent limiter in production

def connection():
    db = sqlite3.connect(current_app.config["AUTH_DATABASE"])
    db.row_factory = sqlite3.Row
    return db

def init_auth_db(app):
    app.config.setdefault("AUTH_DATABASE", str(Path(app.instance_path) / "accounts.sqlite3"))
    Path(app.config["AUTH_DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(app.config["AUTH_DATABASE"]) as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, major TEXT, classification TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS records (user_id INTEGER PRIMARY KEY, courses_json TEXT NOT NULL, updated_at INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id))")
        db.execute("CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, question TEXT NOT NULL, reply TEXT NOT NULL, created_at INTEGER NOT NULL)")
        columns = {row[1] for row in db.execute("PRAGMA table_info(chats)")}
        if "service" not in columns:
            db.execute("ALTER TABLE chats ADD COLUMN service TEXT NOT NULL DEFAULT 'academic'")
        if "session_id" not in columns:
            db.execute("ALTER TABLE chats ADD COLUMN session_id TEXT")
        db.execute("CREATE INDEX IF NOT EXISTS chats_by_session ON chats(user_id,service,session_id,id)")
        db.execute("CREATE TABLE IF NOT EXISTS advising_sessions "
                   "(id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, revision INTEGER NOT NULL DEFAULT 0)")

class User(UserMixin):
    def __init__(self, row):
        self.id = str(row["id"]); self.name = row["name"]; self.email = row["email"]

def get_user(uid):
    with connection() as db:
        row = db.execute("SELECT id,name,email FROM users WHERE id=?", (uid,)).fetchone()
    return User(row) if row else None

def csrf_token():
    if "csrf" not in session: session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]

@auth_bp.get("/api/auth/csrf")
def csrf():
    return jsonify(csrf=csrf_token())

@auth_bp.before_app_request
def protect_mutations():
    account_chat = current_user.is_authenticated and request.path in (
        "/api/career", "/api/tutoring", "/api/success",
    )
    if (request.path.startswith("/api/auth/") or request.path in ("/api/degreeworks", "/api/adviser") or account_chat) and request.method in ("POST", "PUT", "PATCH", "DELETE"):
        if not secrets.compare_digest(request.headers.get("X-CSRF-Token", ""), session.get("csrf", "")) or not session.get("csrf"):
            return jsonify(error="Invalid CSRF token"), 403

def limited(key):
    now = time.time(); hits = [t for t in _attempts.get(key, []) if now - t < 900]
    if len(hits) >= 10: return True
    hits.append(now); _attempts[key] = hits
    return False

def public_user():
    return {"name": current_user.name, "email": current_user.email}

@auth_bp.post("/api/auth/signup")
def signup():
    data = request.form
    email = data.get("email", "").strip().lower()
    name = data.get("name", "").strip()
    password = data.get("password", "")
    if not re.fullmatch(r"[A-Za-z0-9._%+\-]+@morgan\.edu", email) or not 1 <= len(name) <= 100 or len(password) < 12 or len(password) > 128:
        return jsonify(error="Use a Morgan email, your name, and a password of 12–128 characters."), 400
    pdf = request.files.get("degreeworks")
    try:
        courses = extract_courses(pdf) if pdf and pdf.filename else None
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    try:
        with connection() as db:
            cursor = db.execute("INSERT INTO users (name,email,password_hash,major,classification) VALUES (?,?,?,?,?)", (name,email,generate_password_hash(password),data.get("major", "")[:80],data.get("classification", "")[:40]))
            uid = cursor.lastrowid
            if courses is not None: save_record(db, uid, courses)
    except sqlite3.IntegrityError:
        return jsonify(error="Account already exists."), 409
    session.clear(); login_user(get_user(uid)); csrf_token()
    return jsonify(user=public_user(), csrf=session["csrf"]), 201

@auth_bp.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower(); password = str(data.get("password", ""))
    if limited((request.remote_addr, email)):
        return jsonify(error="Too many attempts. Try again later."), 429
    with connection() as db:
        row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify(error="Invalid email or password."), 401
    session.clear(); login_user(User(row)); csrf_token()
    return jsonify(user=public_user(), csrf=session["csrf"])

@auth_bp.post("/api/auth/logout")
@login_required
def logout():
    logout_user(); session.clear(); return jsonify(ok=True)

@auth_bp.get("/api/auth/me")
def me():
    return jsonify(user=public_user() if current_user.is_authenticated else None)

def extract_courses(upload):
    """Extract only candidate course codes; do not retain the original PDF or raw text."""
    if not upload.filename.lower().endswith(".pdf"):
        raise ValueError("Please upload a PDF file.")
    content = upload.read(5 * 1024 * 1024 + 1)
    if len(content) > 5 * 1024 * 1024 or not content.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF or PDF exceeds 5 MB.")
    try:
        reader = PdfReader(io.BytesIO(content), strict=True)
        if reader.is_encrypted or not 1 <= len(reader.pages) <= 20:
            raise ValueError("Encrypted or oversized reports are not supported.")
        root = reader.trailer["/Root"]
        if any(k in root for k in ("/OpenAction", "/AA")):
            raise ValueError("PDF contains unsupported actions.")
        names = root.get("/Names")
        if names:
            names = names.get_object()
            if any(k in names for k in ("/JavaScript", "/EmbeddedFiles")):
                raise ValueError("PDF contains unsupported embedded content.")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if len(text) > 200000: raise ValueError("PDF contains too much text.")
    except ValueError: raise
    except Exception: raise ValueError("Unable to parse this PDF safely.")
    # Candidates only: a course appearing in a report does not prove completion.
    courses = sorted(set(re.findall(r"\b[A-Z]{2,5}\s?\d{3}[A-Z]?\b", text.upper())))[:250]
    if not courses: raise ValueError("No course codes detected. Please use a text-based Degree Works PDF.")
    report = parse_degreeworks(content)
    report["course_candidates"] = courses
    return report

def save_record(db, uid, courses):
    db.execute("INSERT INTO records (user_id,courses_json,updated_at) VALUES (?,?,?) ON CONFLICT(user_id) DO UPDATE SET courses_json=excluded.courses_json, updated_at=excluded.updated_at", (uid,json.dumps(courses),int(time.time())))

@auth_bp.post("/api/degreeworks")
@login_required
def upload_degreeworks():
    upload = request.files.get("degreeworks")
    if not upload: return jsonify(error="Select a PDF."), 400
    try: courses = extract_courses(upload)
    except ValueError as exc: return jsonify(error=str(exc)), 400
    with connection() as db: save_record(db, int(current_user.id), courses)
    return jsonify(message="Degree Works report analyzed and saved. Review the summary in My Progress; final degree clearance remains with the university.", report=courses)

@auth_bp.get("/api/progress")
@login_required
def progress():
    with connection() as db:
        row = db.execute("SELECT courses_json,updated_at FROM records WHERE user_id=?", (current_user.id,)).fetchone()
    stored=json.loads(row["courses_json"]) if row else None
    report=stored if isinstance(stored,dict) else None
    return jsonify(report=report, courses=report.get("course_candidates",[]) if report else (stored or []), updated_at=row["updated_at"] if row else None, notice="Unofficial Degree Works audit; verify with your academic advisor and registrar.")

@auth_bp.get("/api/history")
@login_required
def history():
    from .chat_history import SERVICES
    service = request.args.get("service", "academic")
    if service not in SERVICES:
        return jsonify(error="Unknown student service."), 400
    with connection() as db:
        rows = db.execute("SELECT id,question,reply,created_at,session_id,service FROM chats "
                          "WHERE user_id=? AND service=? ORDER BY id DESC LIMIT 30",
                          (current_user.id, service)).fetchall()
        requested_session = request.args.get("session_id")
        active_session_valid = None
        if requested_session:
            active_session_valid = db.execute(
                "SELECT 1 FROM chats WHERE user_id=? AND service=? AND session_id=? LIMIT 1",
                (current_user.id, service, requested_session),
            ).fetchone() is not None
    return jsonify(history=[dict(r) for r in rows], active_session_valid=active_session_valid)


@auth_bp.get("/api/history/session")
@login_required
def history_session():
    from .chat_history import SERVICES
    service = request.args.get("service", "academic")
    session_id = request.args.get("session_id", "")
    if service not in SERVICES or not session_id or len(session_id) > 128:
        return jsonify(error="Invalid conversation."), 400
    with connection() as db:
        rows = db.execute(
            "SELECT question,reply,created_at FROM chats WHERE user_id=? AND service=? "
            "AND session_id=? ORDER BY id", (current_user.id, service, session_id),
        ).fetchall()
    if not rows:
        return jsonify(error="Conversation is unavailable."), 404
    return jsonify(history=[dict(row) for row in rows], session_id=session_id)
