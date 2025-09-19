import telebot
import yfinance as yf
import ta

# 🔑 Your bot token
BOT_TOKEN = "8208622897:AAH23ayuurLtjjUWBiFIb8HpzsppERpAWzk"
bot = telebot.TeleBot(BOT_TOKEN)

# 🔍 Function to get signals
def get_signal(symbol, interval):
    try:
        data = yf.download(symbol, period="1d", interval=interval)
        close = data["Close"].dropna()

        # 🔥 FIX: make sure it's 1D
        close = close.squeeze()

        # RSI
        rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]

        # MACD
        macd = ta.trend.MACD(close)
        macd_val = macd.macd().iloc[-1]
        signal_val = macd.macd_signal().iloc[-1]

        # Trading logic (always BUY or SELL)
        if rsi < 50 and macd_val > signal_val:
            return f"{symbol} ({interval}) → BUY 📈\nRSI: {rsi:.2f}\nMACD: Bullish crossover ✅"
        else:
            return f"{symbol} ({interval}) → SELL 📉\nRSI: {rsi:.2f}\nMACD: Bearish crossover ❌"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📊 Welcome to MANBOY Forex Bot!\n\nUse /signal to request live signals.")

# /signal command
@bot.message_handler(commands=['signal'])
def signal(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("EURUSD 1m", "GBPUSD 1m", "AUDUSD 1m", "USDJPY 1m", "XAUUSD 1m")
    bot.send_message(message.chat.id, "💹 Choose a pair:", reply_markup=markup)

# Handle chosen pair
@bot.message_handler(func=lambda msg: True)
def handle_signal_request(message):
    try:
        text = message.text.split()
        if len(text) == 2:
            symbol, interval = text
            # Map symbols to Yahoo Finance format
            mapping = {
                "EURUSD": "EURUSD=X",
                "GBPUSD": "GBPUSD=X",
                "AUDUSD": "AUDUSD=X",
                "USDJPY": "JPY=X",
                "XAUUSD": "GC=F"  # Gold
            }
            if symbol in mapping:
                ticker = mapping[symbol]
                result = get_signal(ticker, interval)
                bot.reply_to(message, result)
            else:
                bot.reply_to(message, "⚠️ Invalid pair.")
        else:
            bot.reply_to(message, "⚠️ Please choose a valid option.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

print("🤖 Bot is running...")
bot.infinity_polling()
