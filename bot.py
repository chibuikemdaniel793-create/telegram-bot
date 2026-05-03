from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = "8636133899:AAH2M4Onguq-3Gx2yInJ-EYvYoYOu5fmKy4"
CHAT_ID = "-1003981695392"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, data=data)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    # If message comes from Telegram
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        send_message(chat_id, text)

    # If alert comes from TradingView
    elif "text" in data:
        send_message(CHAT_ID, data["text"])

    return "ok"

@app.route('/')
def home():
    return "Bot is running!"

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
