import telebot
import yfinance as yf
import pandas as pd
import ta

# === CONFIG ===
BOT_TOKEN = "8208622897:AAH23ayuurLtjjUWBiF"   # your bot token
bot = telebot.TeleBot(BOT_TOKEN)

# Forex pairs
pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "XAUUSD=X"]

# Timeframes
timeframes = {"1m": "1m", "5m": "5m", "15m": "15m"}

def get_signal(pair, interval):
    try:
        data = yf.download(pair, period="1d", interval=interval)
        if data.empty:
            return f"⚠️ No data for {pair} {interval}"

        close = data["Close"]

        # Indicators
        rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
        macd = ta.trend.MACD(close)
        macd_val = macd.macd().iloc[-1]
        signal_val = macd.macd_signal().iloc[-1]

        # Convert to floats
        rsi = float(rsi)
        macd_val = float(macd_val)
        signal_val = float(signal_val)

        # Signal logic
        if rsi < 30 and macd_val > signal_val:
            return f"📈 BUY {pair} ({interval}) | RSI={rsi:.2f}"
        elif rsi > 70 and macd_val < signal_val:
            return f"📉 SELL {pair} ({interval}) | RSI={rsi:.2f}"
        else:
            return f"⏸ NO TRADE {pair} ({interval}) | RSI={rsi:.2f}"

    except Exception as e:
        return f"⚠️ Error for {pair} {interval}: {str(e)}"

@bot.message_handler(commands=["signal"])
def send_signals(message):
    bot.reply_to(message, "📡 Fetching signals...")
    for pair in pairs:
        for tf in timeframes.values():
            signal = get_signal(pair, tf)
            bot.send_message(message.chat.id, signal)

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print("Bot crashed, restarting...", e)

if __name__ == "__main__":
    run_bot()
