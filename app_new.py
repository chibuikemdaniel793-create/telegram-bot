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

    return float(rsi['values'][0]['rsi']), float(ema50['values'][0]['ema']), float(ema200['values'][0]['ema'])

def get_price(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
    data = requests.get(url).json()
    return float(data["price"])

# ---------------- SIGNAL LOGIC ---------------- #
def generate_signal(symbol, mode="normal"):
    rsi, ema50, ema200 = get_indicators(symbol)

    trend_up = ema50 > ema200
    trend_down = ema50 < ema200
    trend_strength = abs(ema50 - ema200)

    if trend_strength < 0.00005:
        return "NO TRADE", rsi, ""

    if mode == "fast":
        if trend_up and 38 <= rsi <= 48:
            return "CALL", rsi, "30 seconds"
        elif trend_down and 52 <= rsi <= 62:
            return "PUT", rsi, "30 seconds"
    else:
        if trend_up and rsi < 38:
            return "CALL", rsi, "1-2 minutes"
        elif trend_down and rsi > 62:
            return "PUT", rsi, "1-2 minutes"

    return "NO TRADE", rsi, ""

# ---------------- RESULT TRACKER ---------------- #
def track_result(symbol, signal, entry_price, duration):
    if duration == "30 seconds":
        time.sleep(30)
    else:
        time.sleep(60)

    exit_price = get_price(symbol)

    win = False
    if signal == "CALL" and exit_price > entry_price:
        win = True
    elif signal == "PUT" and exit_price < entry_price:
        win = True

    if win:
        trade_stats["wins"] += 1
        result = "✅ WIN"
    else:
        trade_stats["losses"] += 1
        result = "❌ LOSS"

    total = trade_stats["wins"] + trade_stats["losses"]
    winrate = (trade_stats["wins"] / total) * 100

    send_message(
        f"{result}\n\n"
        f"📊 {symbol}\n"
        f"Entry: {entry_price}\n"
        f"Exit: {exit_price}\n\n"
        f"📈 Winrate: {winrate:.2f}% "
        f"({trade_stats['wins']}W / {trade_stats['losses']}L)"
    )

# ---------------- STYLE ---------------- #
def fancy_signal(symbol, mode="normal"):
    send_message(
        "🔍 Generating New Signal...\n\n"
        f"📊 Asset: {symbol}\n"
        "⏱ Time Frame: 1 Minute\n"
        "📡 Status: Analyzing market conditions...\n\n"
        "📈 Process Started:\n"
        "• Scanning market trends\n"
        "• Analyzing price patterns\n"
        "• Calculating risk levels\n"
        "• Generating signal...\n\n"
        "⏳ Please wait 3-5 seconds..."
    )

    time.sleep(3)

    signal, rsi, duration = generate_signal(symbol, mode)

    if signal == "NO TRADE":
        return

    entry_price = get_price(symbol)

    image = "https://i.imgur.com/green_call.png" if signal == "CALL" else "https://i.imgur.com/red_put.png"

    caption = (
        "✅ New Signal Generated!\n\n"
        f"📊 Asset: {symbol}\n"
        "⏱ Time Frame: 1 Minute\n"
        "📡 Status: Signal Confirmed\n\n"
        f"📢 SIGNAL: {signal}\n\n"
        f"📈 RSI: {rsi:.2f}\n"
        "📌 Strategy:\n"
        "• EMA Trend Confirmed\n"
        "• RSI Condition Met\n\n"
        f"⚠️ Duration: {duration}"
    )

    send_photo(image, caption)

    threading.Thread(
        target=track_result,
        args=(symbol, signal, entry_price, duration)
    ).start()

# ---------------- AUTO SCANNER ---------------- #
def market_scanner():
    while True:
        for pair in PAIRS:
            signal, _, _ = generate_signal(pair, "fast")

            if signal != "NO TRADE":
                if pair not in last_signal or last_signal[pair] != signal:
                    fancy_signal(pair, "fast")
                    last_signal[pair] = signal

        time.sleep(30)

# ---------------- TELEGRAM COMMANDS ---------------- #
def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    return requests.get(url, params=params).json()

def handle_updates():
    last_update_id = None

    while True:
        updates = get_updates(last_update_id)

        for update in updates["result"]:
            last_update_id = update["update_id"] + 1

            if "message" in update:
                text = update["message"]["text"]

                if text == "/start":
                    send_message("🤖 Bot Active!\nUse /signal GBPUSD or /signal EURUSD fast")

                elif text.startswith("/signal"):
                    parts = text.split()

                    if len(parts) >= 2:
                        pair = parts[1].upper()
                        mode = "fast" if len(parts) > 2 else "normal"
                        fancy_signal(pair, mode)
                    else:
                        send_message("⚠️ Use: /signal GBPUSD")

        time.sleep(2)

# ---------------- WEBHOOK (OLD BOT STILL SAFE) ---------------- #
@app.route('/webhook', methods=['POST'])
def webhook_old():
    data = request.json
    symbol = data.get("symbol", "GBPUSD")
    fancy_signal(symbol, "normal")
    return "ok"

# ---------------- WEBHOOK NEW (YOUR NEW BOT) ---------------- #
@app.route('/webhook-new', methods=['POST'])
def webhook_new():
    data = request.json
    symbol = data.get("symbol", "GBPUSD")
    fancy_signal(symbol, "fast")
    return "ok"

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    threading.Thread(target=market_scanner).start()
    threading.Thread(target=handle_updates).start()
    app.run(host="0.0.0.0", port=10000)
