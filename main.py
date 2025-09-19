import telebot
import yfinance as yf
import pandas as pd
import ta

# ======================
# CONFIG
# ======================
API_TOKEN = "8208622897:AAH23ayuurLtjjUWBiFIb8HpzsppERpAWzk"  # your bot token
bot = telebot.TeleBot(API_TOKEN)

# Pairs we dey watch
PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "XAUUSD=X"]

# Function to check signals
def get_signal(pair):
    try:
        df = yf.download(pair, period="1d", interval="1m")

        if df.empty:
            return f"⚠️ No data for {pair}"

        df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
        df["MACD"] = ta.trend.MACD(df["Close"]).macd()

        rsi = df["RSI"].iloc[-1]
        macd = df["MACD"].iloc[-1]

        if rsi < 30 and macd > 0:
            return f"✅ {pair} → BUY signal"
        elif rsi > 70 and macd < 0:
            return f"❌ {pair} → SELL signal"
        else:
            # Instead of "No Trade", just stay silent
            return None

    except Exception as e:
        return f"⚠️ Error for {pair}: {e}"

# ======================
# COMMANDS
# ======================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Bot dey online!\nUse /signal to check trades.")

@bot.message_handler(commands=['signal'])
def signal(message):
    results = []
    for pair in PAIRS:
        sig = get_signal(pair)
        if sig:  # Only add if it's BUY or SELL
            results.append(sig)

    if results:
        bot.reply_to(message, "\n".join(results))
    else:
        bot.reply_to(message, "📉 No BUY/SELL signals right now.")

# ======================
# RUN BOT
# ======================
print("🤖 Bot dey run...")
bot.polling(none_stop=True)
