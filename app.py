from flask import Flask, render_template, request, redirect, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load environment variables
PESAPAL_API_URL = os.getenv("PESAPAL_API_URL")
CONSUMER_KEY = os.getenv("PESAPAL_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("PESAPAL_CONSUMER_SECRET")
CALLBACK_URL = os.getenv("CALLBACK_URL")

# Get OAuth Token from Pesapal
def get_token():
    url = f"{PESAPAL_API_URL}/Auth/RequestToken"
    headers = {"Content-Type": "application/json"}
    data = {"consumer_key": CONSUMER_KEY, "consumer_secret": CONSUMER_SECRET}
    response = requests.post(url, json=data)
    print("🟡 [TOKEN RESPONSE]:", response.text)  # Debug log
    response.raise_for_status()
    return response.json().get("token")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/deposit", methods=["POST"])
def deposit():
    phone = request.form["phone"]
    amount = request.form["amount"]

    # Get OAuth token
    token = get_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    # Build request payload
    payload = {
        "id": f"txn-{phone[-4:]}",
        "currency": "KES",
        "amount": amount,
        "description": "Wallet Deposit",
        "callback_url": CALLBACK_URL,
        "notification_id": "",
        "billing_address": {
            "email_address": "user@example.com",
            "phone_number": phone,
            "country_code": "KE",
            "first_name": "User",
            "last_name": "Deposit",
            "line_1": "Nairobi",
        },
    }

    # Submit order to Pesapal
    response = requests.post(
        f"{PESAPAL_API_URL}/Transactions/SubmitOrderRequest",
        json=payload,
        headers=headers,
    )

    print("🟢 [SUBMIT RESPONSE]:", response.text)  # Debug log

    if response.status_code == 200:
        data = response.json()
        redirect_url = data.get("redirect_url")
        order_tracking_id = data.get("order_tracking_id")

        if redirect_url:
            print("✅ Redirecting to:", redirect_url)
            return redirect(redirect_url)
        else:
            print("⚠️ No redirect URL returned!")
            return jsonify({
                "message": "Pesapal response received, but no redirect URL found.",
                "pesapal_response": data
            }), 200
    else:
        print("🔴 [ERROR RESPONSE]:", response.text)
        return jsonify({
            "error": "Failed to initiate payment",
            "details": response.text
        }), 400


@app.route("/callback")
def callback():
    return "✅ Payment completed successfully! Pesapal will notify your system shortly."


if __name__ == "__main__":
    app.run(debug=True)
