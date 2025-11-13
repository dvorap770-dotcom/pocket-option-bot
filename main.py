import requests, time, pandas as pd, numpy as np, yfinance as yf
from flask import Flask
import threading

# === Telegram ===
TELEGRAM_TOKEN = "8431349187:AAGSTWKMi__sIKZZ5n4nzNLSUoLn4Y"
CHAT_ID = "5968005832"

# === Flask для keep-alive ===
app = Flask(__name__)
@app.route('/')
def home():
    return "📡 Pocket Option Bot 4.0 is running!"
def run_flask():
    app.run(host='0.0.0.0', port=8080)
threading.Thread(target=run_flask).start()

# === Настройки анализа ===
pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "NZDUSD=X", "NZDUSD=X"]
intervals = ["1m", "5m"]

def get_signals(pair, interval):
    data = yf.download(pair, period="1d", interval=interval)
    data.dropna(inplace=True)

    data['EMA5'] = data['Close'].ewm(span=5).mean()
    data['EMA20'] = data['Close'].ewm(span=20).mean()
    data['RSI'] = 100 - (100 / (1 + data['Close'].pct_change().add(1).rolling(14).apply(lambda x: np.prod(x) ** (1/len(x)))))

    last = data.iloc[-1]
    prev = data.iloc[-2]

    if last['EMA5'] > last['EMA20'] and prev['EMA5'] <= prev['EMA20'] and last['RSI'] < 70:
        return f"🟢 BUY {pair} ({interval})"
    elif last['EMA5'] < last['EMA20'] and prev['EMA5'] >= prev['EMA20'] and last['RSI'] > 30:
        return f"🔴 SELL {pair} ({interval})"
    else:
        return None

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

print("📊 Pocket Option Bot 4.0 started...")

while True:
    for pair in pairs:
        for interval in intervals:
            try:
                signal = get_signals(pair, interval)
                if signal:
                    print(signal)
                    send_telegram(signal)
            except Exception as e:
                print("Ошибка:", e)
    time.sleep(60)
