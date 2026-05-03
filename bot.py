from flask import Flask, request
import requests

app = Flask(__name__)

# 🔴 REPLACE THESE WITH YOUR REAL VALUES
BOT_TOKEN = "8636133899:AAH2M4Onguq-3Gx2yInJ-EYvYoYOu5fmKy4"
CHAT_ID = "-1003981695392"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

# ✅ Test route (optional)
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

# ✅ Webhook route (TradingView will send data here)
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    message = str(data)

    send_telegram(message)

    return {"status": "success"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
