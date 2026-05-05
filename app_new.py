from flask import Flask
import requests
import time
import threading

app = Flask(__name__)

# ================= CONFIG =================
BOT_TOKEN = "8729302934:AAGTTdfV8lPAR2hg4_zVVqT2ipLG1-lAV4s"
CHAT_ID = "-1003953725914"
API_KEY = "99d377849d7549b6bee6e997e1fd9456"

PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY",
    "AUD/USD", "USD/CAD", "USD/CHF",
    "EUR/JPY", "GBP/JPY", "EUR/GBP", "AUD/JPY"
]

last_signal = {}

# ================= TELEGRAM =================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass

# ================= DATA =================
def get_indicators(symbol):
    base = "https://api.twelvedata.com"

    try:
        rsi = requests.get(f"{base}/rsi?symbol={symbol}&interval=1min&apikey={API_KEY}").json()
        ema50 = requests.get(f"{base}/ema?symbol={symbol}&interval=1min&time_period=50&apikey={API_KEY}").json()
        ema200 = requests.get(f"{base}/ema?symbol={symbol}&interval=1min&time_period=200&apikey={API_KEY}").json()

        return (
            float(rsi["values"][0]["rsi"]),
            float(ema50["values"][0]["ema"]),
            float(ema200["values"][0]["ema"])
        )
    except:
        return None, None, None

# ================= SIGNAL LOGIC =================
def generate_signal(symbol):
    rsi, ema50, ema200 = get_indicators(symbol)

    if rsi is None:
        return "NO DATA"

    # TREND
    if ema50 > ema200 and rsi < 40:
        return "CALL"
    elif ema50 < ema200 and rsi > 60:
        return "PUT"

    return "WAIT"

# ================= MANUAL SIGNAL =================
def send_signal(pair):
    send_message(f"🔍 Generating signal for {pair}...")

    signal = generate_signal(pair)

    if signal == "CALL":
        send_message(f"📈 {pair} → BUY (CALL)\n⏱ Time: 1 Minute")
    elif signal == "PUT":
        send_message(f"📉 {pair} → SELL (PUT)\n⏱ Time: 1 Minute")
    else:
        send_message(f"⚠️ No clear signal for {pair}")

# ================= AUTO SCANNER =================
def auto_scan():
    while True:
        for pair in PAIRS:
            signal = generate_signal(pair)

            if signal in ["CALL", "PUT"]:
                if last_signal.get(pair) != signal:
                    send_message(f"🔥 AUTO SIGNAL\n{pair} → {signal} (1M)")
                    last_signal[pair] = signal

        time.sleep(15)  # FAST SCAN (no long delay)

# ================= TELEGRAM COMMAND =================
def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    return requests.get(url, params={"timeout": 100, "offset": offset}).json()

def handle_updates():
    last_id = None

    while True:
        updates = get_updates(last_id)

        for update in updates.get("result", []):
            last_id = update["update_id"] + 1

            if "message" in update:
                text = update["message"]["text"].lower()

                if text == "/start":
                    send_message("🤖 Bot Active!\nUse /signal eurusd")

                elif text.startswith("/signal"):
                    parts = text.split()

                    if len(parts) < 2:
                        send_message("⚠️ Use: /signal eurusd")
                        continue

                    pair = parts[1].upper()

                    # FIX FORMAT (EURUSD → EUR/USD)
                    if "/" not in pair:
                        pair = pair[:3] + "/" + pair[3:]

                    send_signal(pair)

        time.sleep(2)

# ================= RUN =================
if __name__ == "__main__":
    threading.Thread(target=auto_scan).start()
    threading.Thread(target=handle_updates).start()

    app.run(host="0.0.0.0", port=10000)
