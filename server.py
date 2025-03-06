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
    data = ref.order_by_key().limit_to_last(1).get()  # Fetch only the latest entry

    if not data:
        return jsonify({"percentage": 0})  # Return 0 if no data found

    latest_entry = list(data.values())[0]  # Extract the latest data

    # Check if the latest entry belongs to Dustbin 32
    if latest_entry.get("dustbin_no") == 32:
        latest_percentage = latest_entry.get("percentage", 0)
    else:
        latest_percentage = 0  # Return 0 if Dustbin 32 data is missing

    return jsonify({"percentage": latest_percentage})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
