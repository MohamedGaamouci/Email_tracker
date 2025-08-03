from flask import Flask, request, send_file, redirect, jsonify, make_response
import os
from datetime import datetime
from flask_cors import CORS
from database import MySQLTracker
port = int(os.environ.get("PORT", 5000))  # default to 5000 if PORT is not set


app = Flask(__name__)
CORS(app)


print("Server running...")

CSV_FILE = "events.csv"


tracker = MySQLTracker()  # create the tracker instance


@app.route("/")
def home():
    return "<h1>Email Tracker Running</h1>"


@app.route('/pixel')
def track_pixel():
    campaign = request.args.get('campaign')
    email = request.args.get('email')

    if campaign and email:
        tracker.log_event(campaign, email, "open")

    print(f"📩 Open tracked: {email} - {campaign}")
    return send_file('pixel.png', mimetype='image/png')


@app.route("/cta")
def track_cta():
    campaign = request.args.get("campaign")
    email = request.args.get("email")
    target_url = request.args.get("target", "https://easybooking.com")

    if campaign and email:
        tracker.log_event(campaign, email, "click", target_url)

    return redirect(target_url)


@app.route("/api/stats")
def api_stats():
    return jsonify(tracker.get_stats())


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=port)

# from PIL import Image

# img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))  # Transparent
# img.save("pixel.png")
