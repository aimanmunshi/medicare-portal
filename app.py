import os, logging
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
COLOR = os.getenv("APP_COLOR", "blue")
VERSION = os.getenv("APP_VERSION", "1.0")
appointments = []   # dummy in-memory data only

DOCTORS = ["Dr. Rao - Cardiology", "Dr. Mehta - General Medicine",
           "Dr. Iyer - Pediatrics", "Dr. Khan - Dermatology"]
SLOTS = ["09:00", "10:30", "12:00", "14:30", "16:00"]

def ctx():
    return dict(color=COLOR, version=VERSION, appts=appointments,
                doctors=DOCTORS, slots=SLOTS)

@app.route("/")
def home():
    return render_template("index.html", **ctx())

@app.route("/book", methods=["POST"])
def book():
    appointments.append({
        "name": request.form["name"][:50],
        "doctor": request.form["doctor"][:60],
        "slot": request.form.get("slot", "09:00")[:5],
        "reason": request.form.get("reason", "")[:80],
    })
    app.logger.info("AUDIT: appointment booked (total=%d)", len(appointments))
    return redirect(url_for("home"))

@app.route("/health")
def health():
    return jsonify(status="ok", color=COLOR, version=VERSION)
