from flask import Flask, request, send_file, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
print("The server is running")

# Ensure database exists


def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign TEXT,
        email TEXT,
        type TEXT,            -- 'open' or 'click'
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()


init_db()

# Track email opens


@app.route('/pixel')
def track_pixel():
    campaign = request.args.get('campaign')
    email = request.args.get('email')

    if campaign and email:
        log_event(campaign, email, 'open')

    return send_file('pixel.png', mimetype='image/png')

# Track CTA clicks


@app.route('/cta')
def track_cta():
    campaign = request.args.get('campaign')
    email = request.args.get('email')
    redirect_url = request.args.get(
        'target', 'https://easybooking.com')  # fallback URL

    if campaign and email:
        log_event(campaign, email, 'click')

    return redirect(redirect_url)

# Store events


def log_event(campaign, email, event_type):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO events (campaign, email, type, timestamp) VALUES (?, ?, ?, ?)",
              (campaign, email, event_type, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

# Optional: view tracking log


@app.route('/report')
def report():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        "SELECT campaign, email, type, timestamp FROM events ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()

    html = "<h2>Tracking Report</h2><table border='1'><tr><th>Campaign</th><th>Email</th><th>Type</th><th>Time (UTC)</th></tr>"
    for row in rows:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
    html += "</table>"
    return html


# ✅ Main entry point
if __name__ == "__main__":
    app.run(debug=True)
