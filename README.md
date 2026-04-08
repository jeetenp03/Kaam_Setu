# Village Hire — ગામ મજૂર

A tile-based Flask web app that connects villagers needing work with people who want to hire them. Designed for **rural Gujarat** with large visual tiles, hand-drawn SVG illustrations, and **trilingual support** (English, Hindi, Gujarati) so even non-readers can use it.

## Features

- **Two-tile landing page** — `HIRE` or `WORKER` (full-screen, can't miss it)
- **10 trade categories** — Electrician, Labor, Painter, Carpentry, Plumber, Mason, Tailor, Driver, Cook, Farming
- **Hand-drawn SVG icons** for every trade — visual recognition for non-readers
- **Trilingual** — switch between English / हिन्दी / ગુજરાતી from the navbar
- **Mobile-first** — large tap targets, dynamic viewport height, safe-area insets, no iOS zoom on focus
- **Gujarat-themed navbar** — saffron/cream/green palette, Bandhani-inspired border, sun-over-village logo
- **Simple JSON storage** — no database setup needed

## Tech stack

- Python 3 + Flask
- Vanilla HTML / CSS (no frontend framework)
- Inline SVGs for all illustrations
- JSON file for storage

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5050` in your browser.

To test on your phone, find your PC's local IP (`ipconfig` on Windows) and open `http://<your-ip>:5050` from any device on the same Wi-Fi.

## Project structure

```
VillageHire/
├── app.py                  # Flask routes and language handling
├── translations.py         # English / Hindi / Gujarati strings
├── requirements.txt
├── templates/
│   ├── base.html           # Layout + Gujarat-themed navbar
│   ├── icons.html          # Reusable SVG illustrations
│   ├── index.html          # Landing — HIRE / WORKER tiles
│   ├── worker_categories.html
│   ├── hire_categories.html
│   ├── register.html       # Name / phone / village form
│   ├── success.html
│   └── directory.html      # Browse registered workers
└── static/
    └── style.css
```

## Adding category-tile photos

Drop `hire.jpg` and `worker.jpg` into `static/` to use real photographs as backgrounds for the two main landing tiles. The CSS overlays a dark gradient so the text stays readable.
