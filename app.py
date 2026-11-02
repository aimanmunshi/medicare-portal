import os, logging
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
COLOR = os.getenv("APP_COLOR", "blue")
VERSION = os.getenv("APP_VERSION", "1.0")
appointments = []   # dummy in-memory data only

@app.route("/")
def home():
    return render_template("index.html", color=COLOR, version=VERSION, appts=appointments)

@app.route("/book", methods=["POST"])
def book():
    appointments.append({"name": request.form["name"][:50], "doctor": request.form["doctor"][:50]})
    app.logger.info("AUDIT: appointment booked (total=%d)", len(appointments))
    return render_template("index.html", color=COLOR, version=VERSION, appts=appointments)

@app.route("/health")
def health():
    return jsonify(status="ok", color=COLOR, version=VERSION)
