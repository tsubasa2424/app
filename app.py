import os
import json
import requests
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize Flask app
app = Flask(__name__)

# LINE API credentials
LINE_CHANNEL_ACCESS_TOKEN = "UH9/CGcVZt4bnQKn3DX72uPH1i6AC0uKxSEWa2divzG7kyK3MfkOl1kc2K7bKhbbw0oIWnAk2K+/Mq/GJIq6RcBKBCPK025VD0S7ZPazgxcEI+fbA/ceLzDWorMGUFUPyaAyB/voU2GTKn23KUw8gwdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "43ef859f4196c303b24b94f6052c4fa3"

# Bitbank API endpoint
BITBANK_API_URL = "https://public.bitbank.cc"

# User data storage
user_data = {}

# Send a message through LINE Messaging API
def send_line_message(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=payload)

# Get current price of a cryptocurrency
def get_crypto_price(pair):
    response = requests.get(f"{BITBANK_API_URL}/{pair}/ticker")
    data = response.json()
    return float(data["data"]["last"])

# Monitor prices and send notifications
def monitor_prices():
    for user_id, preferences in user_data.items():
        pair = preferences["pair"]
        target_price = preferences["target_price"]
        current_price = get_crypto_price(pair)
        if current_price >= target_price:
            # Notify the user on LINE
            message = f"🚨 {pair.upper()} has reached your target price of {target_price}! Current price: {current_price}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
            }
            payload = {
                "to": user_id,
                "messages": [{"type": "text", "text": message}]
            }
            requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
            # Remove user preferences after notification
            del user_data[user_id]

# LINE webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json
    events = body["events"]
    for event in events:
        user_id = event["source"]["userId"]
        reply_token = event["replyToken"]
        message = event["message"]["text"]

        if message in ["友達追加", "価格通知"]:
            # Step 1: Show cryptocurrency options
            crypto_list = ["BTC/JPY", "ETH/JPY", "XRP/JPY"]
            buttons = "\n".join([f"- {crypto}" for crypto in crypto_list])
            response_message = f"💱 Select a cryptocurrency:\n{buttons}"
            send_line_message(reply_token, response_message)

        elif message in ["BTC/JPY", "ETH/JPY", "XRP/JPY"]:
            # Step 2: Store selected cryptocurrency and ask for target price
            user_data[user_id] = {"pair": message.lower()}
            send_line_message(reply_token, f"🔢 Enter the target price for {message}:")

        elif message.isdigit():
            # Step 3: Save target price and start monitoring
            if user_id in user_data:
                user_data[user_id]["target_price"] = int(message)
                send_line_message(reply_token, "✅ Target price set! We'll notify you when the price is reached.")
    return "OK"

# Start the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(monitor_prices, "interval", seconds=30)  # Check prices every 30 seconds
scheduler.start()

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)