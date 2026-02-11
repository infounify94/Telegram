import json
import requests
import os

BOT_TOKEN = os.getenv("8480675236:AAEWnz2d1pdxvsbAPabLEM4CSYoCdgmT62s")
CHAT_ID = os.getenv("6275915337")

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

with open("orb_analysis_multi_trade.json") as f:
    data = json.load(f)

def format_index(idx):
    signals = idx.get("signals", [])
    if not signals:
        return f"❌ {idx['index']}: No signals now"

    text = f"🚨 {idx['index']} SIGNALS 🚨\n"
    for s in signals:
        text += (
            f"\n👉 {s['type']} | Strike: {s['strike']} | Premium: ₹{s['premium']}"
            f"\nEntry: {s['entry']}"
            f"\nTarget: +{s['target_pct']}%  Stop: -{s['stop_pct']}%\n"
        )
    return text

nifty_msg = format_index(data["live_signals"]["nifty"])
bank_msg = format_index(data["live_signals"]["banknifty"])

send(nifty_msg)
send(bank_msg)
