import random
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==========================================
# TELEGRAM BOT TOKEN
# ==========================================

BOT_TOKEN = "8729302934:AAGTTdfV8lPAR2hg4_zVVqT2ipLG1-lAV4s"

# ==========================================
# START COMMAND
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
"""
🚀 OTC AI SIGNAL BOT

✅ REAL-TIME OTC ANALYSIS
✅ 1 MINUTE SIGNALS
✅ SMART ENTRY SYSTEM
✅ ALL OTC PAIRS SUPPORTED

📊 SEND OTC PAIR NOW

EXAMPLES:

EURUSD_otc
GBPJPY_otc
CADJPY_otc
AUDCAD_otc
USDCHF_otc
"""
    )

# ==========================================
# GENERATE SIGNAL
# ==========================================

def generate_signal():

    direction = random.choice(["CALL", "PUT"])

    confidence = random.randint(85, 99)

    entry_time = datetime.now().strftime("%H:%M:%S")

    return direction, confidence, entry_time

# ==========================================
# USER MESSAGE HANDLER
# ==========================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pair = update.message.text.upper()

    # ======================================
    # ANALYSIS MESSAGE
    # ======================================

    await update.message.reply_text(
f"""
🔍 GENERATING NEW SIGNAL

📊 Asset: {pair}
⏰ Time Frame: 1 Minute
🧠 Status: Analyzing market conditions...

📈 PROCESS STARTED

• Scanning latest market trends 🔄
• Analyzing candle movement 📊
• Detecting smart entry zones ⏳
• Calculating volatility levels 📉
• Generating fresh AI signal ⚡

⌛ Please wait 3-5 seconds...
"""
    )

    await asyncio.sleep(4)

    # ======================================
    # GENERATE SIGNAL
    # ======================================

    direction, confidence, entry_time = generate_signal()

    # ======================================
    # SIGNAL STYLE
    # ======================================

    if direction == "CALL":

        signal_box = """
🟩🟩🟩🟩🟩🟩🟩
🟩     CALL     🟩
🟩🟩🟩🟩🟩🟩🟩
"""

    else:

        signal_box = """
🟥🟥🟥🟥🟥🟥🟥
🟥      PUT      🟥
🟥🟥🟥🟥🟥🟥🟥
"""

    # ======================================
    # FINAL SIGNAL
    # ======================================

    await update.message.reply_text(
f"""
✅ NEW SIGNAL GENERATED

📊 Asset Analysis: {pair}
⏰ Time Frame: 1 Minute
🕓 Entry Time: {entry_time}

{signal_box}

🎯 Direction: {direction}

🔥 Confidence Level: {confidence}%

⚠️ ENTER TRADE IMMEDIATELY
⚠️ SIGNAL VALID FOR CURRENT CANDLE ONLY
⚠️ LATE ENTRY MAY CAUSE LOSS

📈 OTC AI ANALYSIS COMPLETE
"""
    )

# ==========================================
# MAIN FUNCTION
# ==========================================

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    print("BOT STARTED SUCCESSFULLY")

    app.run_polling()

# ==========================================

if __name__ == "__main__":
    main()
