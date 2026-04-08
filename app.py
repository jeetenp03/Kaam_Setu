from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

from translations import TRANSLATIONS, LANGUAGES

app = Flask(__name__)
app.secret_key = "village-hire-secret-key"

DB_FILE = "db.json"
DEFAULT_LANG = "en"


def load_db():
    """Load the JSON database."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"workers": [], "hirers": []}


def save_db(data):
    """Save data to JSON database."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ──────────────────────────────────────────────
#  LANGUAGE / TRANSLATION INJECTION
# ──────────────────────────────────────────────

@app.context_processor
def inject_translations():
    """Inject the current language and translation dict into every template."""
    lang = session.get("lang", DEFAULT_LANG)
    if lang not in TRANSLATIONS:
        lang = DEFAULT_LANG
    return {
        "t": TRANSLATIONS[lang],
        "lang": lang,
        "languages": LANGUAGES,
    }


@app.route("/lang/<code>")
def set_language(code):
    """Set language preference and redirect back to referring page."""
    if code in TRANSLATIONS:
        session["lang"] = code
    return redirect(request.referrer or url_for("home"))


# ──────────────────────────────────────────────
#  ROUTES
# ──────────────────────────────────────────────

@app.route("/")
def home():
    """Landing page — Hire or Worker tiles."""
    return render_template("index.html")


@app.route("/worker")
def worker_categories():
    """Show trade category tiles for worker registration."""
    return render_template("worker_categories.html")


@app.route("/hire")
def hire_categories():
    """Show trade category tiles for hiring."""
    return render_template("hire_categories.html")


@app.route("/register/<role>/<category>")
def register(role, category):
    """Registration form for worker or hirer."""
    return render_template("register.html", role=role, category=category)


@app.route("/submit", methods=["POST"])
def submit():
    """Handle registration form submission."""
    db = load_db()

    entry = {
        "name": request.form.get("name", ""),
        "phone": request.form.get("phone", ""),
        "village": request.form.get("village", ""),
        "category": request.form.get("category", ""),
        "role": request.form.get("role", ""),
    }

    if entry["role"] == "worker":
        db["workers"].append(entry)
    else:
        db["hirers"].append(entry)

    save_db(db)
    return render_template("success.html", role=entry["role"], name=entry["name"])


@app.route("/directory")
def directory():
    """View registered workers (for hirers to browse)."""
    db = load_db()
    category = request.args.get("category", "all")
    if category != "all":
        workers = [w for w in db["workers"] if w["category"] == category]
    else:
        workers = db["workers"]
    return render_template("directory.html", workers=workers, category=category)


if __name__ == "__main__":
    app.run(debug=True, port=5050)
