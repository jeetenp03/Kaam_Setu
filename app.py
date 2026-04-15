from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        # Auto-load .env so GOOGLE_SHEET_ID / GOOGLE_CREDS_FILE / SECRET_KEY are
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        # available without exporting them by hand on every run.
try : 
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from translations import TRANSLATIONS, LANGUAGES
from sheets import append_registration, fetch_workers

app            = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "village-hire-dev-key-change-in-production")


@app.context_processor
def inject_asset_version():
    """Cache-bust static assets using the style.css mtime."""
    try:
        css_path = os.path.join(app.static_folder, "style.css")
        return {"asset_v": int(os.path.getmtime(css_path))}
    except OSError:
        return {"asset_v": "0"}


@app.context_processor
def inject_analytics():
    """Expose the GA4 Measurement ID to templates so the snippet can render."""
    return {"ga_measurement_id": os.environ.get("GA_MEASUREMENT_ID", "")}

# Use a writable location for the JSON database. On DigitalOcean App Platform
# the working directory is read-only at runtime; mount /tmp or set DB_PATH.
DB_FILE = os.environ.get("DB_PATH", "db.json")
DEFAULT_LANG = "gu"

# Map category keys to PNG files in static/images/
# Categories not in this dict fall back to SVG icons.
CATEGORY_IMAGES = {
    "electrician" : "electrician.png",
    "labor"       : "labor.png",
    "painter"     : "painter.png",
    "carpentry"   : "lumber.png",
    "mason"       : "manson.png",
    "plumber"     : "plumber.png",
    "tailor"      : "tailor.png",
    "driver"      : "driver.png",
    "cook"        : "cook.png",
    "farming"     : "farmer.png",
}


def load_db():
    """Load the JSON database, guaranteeing both top-level lists exist."""
    data = {"workers": [], "hirers": []}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    data.update(loaded)
            except json.JSONDecodeError:
                pass
    data.setdefault("workers", [])
    data.setdefault("hirers", [])
    return data


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
    poster = "Poster (English).jpg" if lang == "en" else "Poster (Gujarati).png"
    return {
        "t": TRANSLATIONS[lang],
        "lang": lang,
        "languages": LANGUAGES,
        "category_images": CATEGORY_IMAGES,
        "banner_poster": poster,
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
    entry = {
        "name": request.form.get("name", ""),
        "phone": request.form.get("phone", ""),
        "village": request.form.get("village", ""),
        "category": request.form.get("category", ""),
        "role": request.form.get("role", ""),
    }

    if entry["role"] != "worker":
        # Hirer-only job details
        entry["workers_needed"] = request.form.get("workers_needed", "")
        entry["start_date"] = request.form.get("start_date", "")
        entry["num_days"] = request.form.get("num_days", "")
        entry["start_time"] = request.form.get("start_time", "")

    # Primary store: Google Sheets (campaign team views registrations there).
    # Falls back to local JSON if Sheets is not configured or the call fails,
    # so the form never breaks for users on the ground.
    print(f"\n[SUBMIT] entry={entry}", flush=True)
    print(f"[SUBMIT] APPS_SCRIPT_URL set: {bool(os.environ.get('APPS_SCRIPT_URL'))}", flush=True)
    sheet_ok = False
    try:
        sheet_ok = append_registration(entry)
        print(f"[SUBMIT] append_registration returned: {sheet_ok}", flush=True)
    except Exception as exc:
        print(f"[SUBMIT] append_registration RAISED: {type(exc).__name__}: {exc}", flush=True)
        app.logger.warning("Google Sheets append failed: %s", exc)

    if not sheet_ok:
        print("[SUBMIT] FALLING BACK to local db.json", flush=True)
        db = load_db()
        if entry["role"] == "worker":
            db["workers"].append(entry)
        else:
            db["hirers"].append(entry)
        save_db(db)
    else:
        print("[SUBMIT] OK — wrote to Google Sheet", flush=True)

    return render_template(
        "success.html",
        role=entry["role"],
        name=entry["name"],
        category=entry["category"],
    )


@app.route("/privacy")
def privacy():
    """Full privacy notice — linked from the footer of every page."""
    return render_template("privacy.html")


@app.route("/directory")
def directory():
    """View registered workers (for hirers to browse)."""
    workers = None
    try:
        workers = fetch_workers()
    except Exception as exc:
        app.logger.warning("Google Sheets fetch failed: %s", exc)

    if workers is None:
        workers = load_db()["workers"]

    category = request.args.get("category", "all")
    if category != "all":
        workers = [w for w in workers if w["category"] == category]
    return render_template("directory.html", workers=workers, category=category)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
