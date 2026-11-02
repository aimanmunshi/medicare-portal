import os, socket, logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
COLOR = os.getenv("APP_COLOR", "blue")
VERSION = os.getenv("APP_VERSION", "1.0")
STARTED = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
appointments = []   # dummy in-memory data only

DOCTORS = [
    {"name": "Dr. Rao", "dept": "Cardiology", "icon": "&#10084;", "exp": "15 yrs"},
    {"name": "Dr. Mehta", "dept": "General Medicine", "icon": "&#9877;", "exp": "10 yrs"},
    {"name": "Dr. Iyer", "dept": "Pediatrics", "icon": "&#128118;", "exp": "12 yrs"},
    {"name": "Dr. Khan", "dept": "Dermatology", "icon": "&#10024;", "exp": "8 yrs"},
]
SLOTS = ["09:00", "10:30", "12:00", "14:30", "16:00"]

def ctx(**extra):
    d = dict(color=COLOR, version=VERSION, doctors=DOCTORS, slots=SLOTS,
             appts=appointments, pod=socket.gethostname(), started=STARTED)
    d.update(extra)
    return d

@app.route("/")
def home():
    return render_template("index.html", page="home", **ctx())

@app.route("/doctors")
def doctors():
    return render_template("doctors.html", page="doctors", **ctx())

@app.route("/appointments")
def appts():
    return render_template("appointments.html", page="appts", **ctx())

@app.route("/status")
def status():
    return render_template("status.html", page="status", **ctx())

@app.route("/book", methods=["POST"])
def book():
    appointments.append({
        "name": request.form["name"][:50],
        "doctor": request.form["doctor"][:40],
        "slot": request.form.get("slot", "09:00")[:5],
        "reason": request.form.get("reason", "")[:80],
    })
    app.logger.info("AUDIT: appointment booked (total=%d)", len(appointments))
    return redirect(url_for("appts"))

@app.route("/cancel/<int:i>", methods=["POST"])
def cancel(i):
    if 0 <= i < len(appointments):
        appointments.pop(i)
        app.logger.info("AUDIT: appointment cancelled (total=%d)", len(appointments))
    return redirect(url_for("appts"))

@app.route("/health")
def health():
    return jsonify(status="ok", color=COLOR, version=VERSION)
