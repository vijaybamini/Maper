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
    """Fetches the latest fill level for all dustbins."""
    ref = db.reference("data")  # Reference to "data" node
    data = ref.get()  # Fetch all dustbin data

    if not data:
        return jsonify({})  # Return empty object if no data found

    result = {}

    for dustbin_no, records in data.items():
        if isinstance(records, dict):  # ✅ Proper indentation
            latest_key = max(records.keys(), default=None)  # Find latest key
            if latest_key and isinstance(records[latest_key], dict):  # Ensure valid data
                latest_percentage = records[latest_key].get("percentage", 0)

                if isinstance(latest_percentage, (int, float)):  # Check if it's a number
                    if latest_percentage > 100 or latest_percentage < 0:
                        latest_percentage = 100  # If out of range, set to 100
                else:
                    latest_percentage = "No data"  # If data is invalid

                result[dustbin_no] = latest_percentage  # Store only percentage

    return jsonify(result)  # ✅ Ensure this is outside the loop

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
