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
    return render_template("map.html")  # Updated to map.html

@app.route("/get-data")
def get_data():
    """Fetches the latest fill level for Dustbin No. 32."""
    ref = db.reference("data")  # Reference to "data" node
    data = ref.get()

    if not data:
        return jsonify({"error": "No data found"}), 404  # Handle empty database

    latest_percentage = "No data"  # Default if no data is found

    # ✅ Extract the latest percentage for Dustbin No. 32
    for key in sorted(data.keys(), reverse=True):  # Sort keys to get latest first
        entry = data[key]
        if entry.get("dustbin_no") == 32:  # Check if it's for Dustbin 32
            latest_percentage = entry.get("percentage", "No data")
            break  # Stop after finding the latest entry

    return jsonify({"percentage": latest_percentage})  # Return only one value

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
