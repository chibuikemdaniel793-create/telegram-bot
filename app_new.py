from flask import Flask, request
import requests
import time
import threading

app = Flask(__name__)

# ---------------- CONFIG ---------------- #
BOT_TOKEN = "8729302934:AAGTTdfV8lPAR2hg4_zVVqT2ipLG1-lAV4s"
CHAT_ID = "-1003953725914"
API_KEY = "99d377849d7549b6bee6e997e1fd9456"

PAIRS = [
    "GBPUSD", "EURUSD", "USDJPY",
    "AUDUSD", "USDCAD", "USDCHF",
    "EURJPY", "GBPJPY", "EURGBP", "AUDJPY"
]

last_signal = {}

trade_stats = {
    "wins": 0,
    "losses": 0
}

# ---------------- TELEGRAM ---------------- #
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def send_photo(photo_url, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": caption
    })

# ---------------- DATA ---------------- #
def get_indicators(symbol):
    base = "https://api.twelvedata.com"

    rsi = requests.get(f"{base}/rsi?symbol={symbol}&interval=1min&apikey={API_KEY}").json()
    ema50 = requests.get(f"{base}/ema?symbol={symbol}&interval=1min&time_period=50&apikey={API_KEY}").json()
    ema200 = requests.get(f"{base}/ema?symbol={symbol}&interval=1min&time_period=200&apikey={API_KEY}").json()

    return float(rsi['values'][0]['rsi']), float(ema50['values
