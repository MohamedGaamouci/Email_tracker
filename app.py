from flask import Flask, request, send_file, redirect, jsonify, make_response
import csv
import os
from datetime import datetime
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


print("Server running...")

CSV_FILE = "events.csv"

# Ensure CSV file exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["campaign", "email", "type", "timestamp"])  # header


@app.route("/")
def home():
    return "<h1>Email Tracker Running</h1>"


@app.route('/pixel')
def track_pixel():
    campaign = request.args.get('campaign')
    email = request.args.get('email')

    if campaign and email:
        log_event(campaign, email, "open")

    print(f"📩 Open tracked: {email} - {campaign}")

    return send_file(r'C:\Users\n\Desktop\EasyBooking Logo.png', mimetype='image/png')


@app.route("/cta")
def track_cta():
    campaign = request.args.get("campaign")
    email = request.args.get("email")
    redirect_url = request.args.get("target", "https://easybooking.com")
    if campaign and email:
        log_event(campaign, email, "click")
    return redirect(redirect_url)


def log_event(campaign, email, event_type):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([campaign, email, event_type,
                        datetime.utcnow().isoformat()])


@app.route("/api/stats")
def api_stats():
    import collections

    opens = 0
    clicks = 0
    campaigns = set()
    recent_data = collections.defaultdict(
        lambda: {"sent": 0, "open": 0, "click": 0})

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            campaigns.add(row["campaign"])
            recent_data[row["campaign"]]["sent"] += 1
            if row["type"] == "open":
                opens += 1
                recent_data[row["campaign"]]["open"] += 1
            elif row["type"] == "click":
                clicks += 1
                recent_data[row["campaign"]]["click"] += 1

    # Sort and keep only 5 recent campaigns (based on volume, for simplicity)
    sorted_campaigns = sorted(
        recent_data.items(), key=lambda x: x[1]["sent"], reverse=True)[:5]

    return jsonify({
        "emails_opened": opens,
        "emails_clicked": clicks,
        "total_campaigns": len(campaigns),
        "recent_campaigns": [
            {
                "subject": name,
                "sent": stats["sent"],
                "opened": stats["open"],
                "clicked": stats["click"]
            }
            for name, stats in sorted_campaigns
        ]
    })


if __name__ == "__main__":
    app.run(debug=True)


# from PIL import Image

# img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))  # Transparent
# img.save("pixel.png")
