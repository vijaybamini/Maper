from flask import Flask, render_template, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
import json

app = Flask(__name__)

# Load Firebase credentials from environment variable
firebase_credentials = os.environ.get("FIREBASE_CREDENTIALS")

if firebase_credentials:
    cred_dict = json.loads(firebase_credentials)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://dustbinmonitor-c5e71-default-rtdb.firebaseio.com/"
    })
else:
    raise ValueError("Firebase credentials not found in environment variables.")

@app.route("/")
def index():
   return render_template("map.html")  # Updated to match your new file name


@app.route("/get-data")
def get_data():
    """Fetches the latest sensor values for the most recent dustbin entry."""
    ref = db.reference("data")  # Reference to "data" node
    data = ref.get()

    if not data:
        return jsonify({"error": "No data found"}), 404  # Handle empty database

    # ✅ Find the latest entry by sorting keys (timestamps)
    latest_key = max(data.keys())  # Get the latest timestamp key
    latest_entry = data[latest_key]

    response_data = {
        "distance": latest_entry.get("sensor1", latest_entry.get("sensor2", {})).get("distance", "No data"),
        "battery": latest_entry.get("sensor1", latest_entry.get("sensor2", {})).get("battery", "No data"),
    }

    return jsonify(response_data)  # Returns only the latest dustbin data

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
