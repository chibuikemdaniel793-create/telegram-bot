from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = "8636133899:AAH2M4Onguq-3Gx2yInJ-EYvYoYOu5fmKy4"
CHAT_ID = "-1003981695392"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    message = f"""
📊 SIGNAL RECEIVED

Pair: {data.get('pair')}
Action: {data.get('action')}
Timeframe: {data.get('timeframe')}
Strategy: {data.get('strategy')}
"""

    send_message(message)

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
