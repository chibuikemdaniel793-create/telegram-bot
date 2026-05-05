import requests
import time

# ========= CONFIG =========
BOT_TOKEN = "8729302934:AAGTTdfV8lPAR2hg4_zVVqT2ipLG1-lAV4s"
CHAT_ID = "-1003953725914"
API_KEY = "99d377849d7549b6bee6e997e1fd9456"

# ========= TELEGRAM =========
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=5)
    except:
        pass

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        return requests.get(url, params={"timeout": 100, "offset": offset}).json()
    except:
        return {"result": []}

# ========= DATA =========
def get_data(symbol):
    base = "https://api.twelvedata.com"

    try:
        rsi = requests.get(f"{base}/rsi?symbol={symbol}&interval=1min&apikey={API_KEY}", timeout=5).json()
        ema50 = requests.get(f"{base}/ema?symbol={symbol}&interval=1min&time_period=50&apikey={API_KEY}", timeout=5).json()
        ema200 = requests.get(f"{base}/ema?symbol={symbol}&interval=1min&time_period=200&apikey={API_KEY}", timeout=5).json()

        rsi_val = float(rsi["values"][0]["rsi"])
        ema50_val = float(ema50["values"][0]["ema"])
        ema200_val = float(ema200["values"][0]["ema"])

        return rsi_val, ema50_val, ema200_val

    except:
        return None, None, None

# ========= STRATEGY =========
def get_signal(symbol):
    rsi, ema50, ema200 = get_data(symbol)

    if rsi is None:
        return "ERROR", None

    if ema50 > ema200 and 40 <= rsi <= 55:
        return "CALL", rsi

    if ema50 < ema200 and 45 <= rsi <= 60:
        return "PUT", rsi

    return "NO TRADE", rsi

# ========= BOT LOOP =========
def run_bot():
    last_update_id = None

    send_message("🤖 Bot is now ACTIVE!\nUse /signal EURUSD")

    while True:
        updates = get_updates(last_update_id)

        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1

            if "message" in update:
                text = update["message"]["text"]

                if text == "/start":
                    send_message("✅ Bot working!\nUse /signal EURUSD")

                elif text.startswith("/signal"):
                    parts = text.split()

                    if len(parts) < 2:
                        send_message("⚠️ Use: /signal EURUSD")
                        continue

                    pair = parts[1].upper()

                    send_message(f"🔍 Checking {pair}...")

                    result, rsi = get_signal(pair)

                    if result == "ERROR":
                        send_message("⚠️ Data error. Try again.")
                        continue

                    if result == "NO TRADE":
                        send_message(f"⚠️ {pair}\nNo good setup now\nRSI: {rsi:.2f}")
                        continue

                    send_message(
                        f"📊 {pair}\n"
                        f"📢 SIGNAL: {result}\n"
                        f"⏱ Duration: 1 Minute\n"
                        f"📈 RSI: {rsi:.2f}"
                    )

        time.sleep(1)

# ========= RUN =========
if __name__ == "__main__":
    run_bot()
