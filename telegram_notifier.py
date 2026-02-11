#!/usr/bin/env python3
"""
Telegram ORB Signal Notifier
Reads orb_analysis_multi_trade.json and posts formatted messages
Only sends new signals/status updates to avoid spam.
"""

import json
import os
import sys
import requests

# ===================== CONFIG =====================

TELEGRAM_BOT_TOKEN = os.environ.get("8480675236:AAEWnz2d1pdxvsbAPabLEM4CSYoCdgmT62s")
TELEGRAM_CHAT_ID = os.environ.get("-1003713165195")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
    sys.exit(1)

EMOJI = {
    "CALL": "🟢📈",
    "PUT": "🔴📉",
    "fire": "🔥",
    "target": "🎯",
    "stop": "🛑",
    "chart": "📊",
    "money": "💰",
    "warning": "⚠️",
    "check": "✅",
    "cross": "❌",
    "rocket": "🚀",
    "bell": "🔔",
    "clock": "🕐",
    "calendar": "📅"
}

SENT_SIGNALS_FILE = ".sent_signals.json"

# ===================== HELPER FUNCTIONS =====================

def send_telegram_message(message, parse_mode="HTML"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            print("✅ Message sent")
            return True
        else:
            print(f"❌ Failed to send: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False


def load_sent_signals():
    if os.path.exists(SENT_SIGNALS_FILE):
        try:
            with open(SENT_SIGNALS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"nifty": [], "banknifty": [], "nifty_status": [], "banknifty_status": []}


def save_sent_signals(sent_signals):
    with open(SENT_SIGNALS_FILE, "w") as f:
        json.dump(sent_signals, f, indent=2)


def signal_hash(signal):
    """Unique hash for a signal to avoid duplicates"""
    return f"{signal.get('time')}_{signal.get('type')}_{signal.get('strike')}"


def format_signal_message(signal, index_name):
    """Format a single ORB signal"""
    signal_type = signal.get("type", "UNKNOWN")
    emoji_signal = EMOJI.get(signal_type, "📊")

    entry = signal.get("premium_entry", "N/A")
    target = signal.get("target_premium", "N/A")
    stoploss = signal.get("stoploss_premium", "N/A")

    msg = f"{EMOJI['bell']} <b>ORB BREAKOUT SIGNAL — {index_name}</b> {EMOJI['bell']}\n"
    msg += f"{emoji_signal} <b>{signal_type}</b>\n"
    msg += f"{EMOJI['money']} <b>Strike:</b> {signal.get('strike', 'N/A')}\n"
    msg += f"{EMOJI['clock']} <b>Time:</b> {signal.get('time', 'N/A')} IST\n"
    msg += f"{EMOJI['calendar']} <b>Expiry:</b> {signal.get('expiry', 'N/A')}\n\n"
    msg += f"<b>💵 PREMIUM LEVELS:</b>\n  • Entry: ₹{entry}\n  • {EMOJI['target']} Target: ₹{target}\n  • {EMOJI['stop']} Stoploss: ₹{stoploss}\n"
    msg += f"\n━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"{EMOJI['warning']} <i>Educational only. Not financial advice.</i>"

    return msg


def format_no_signal_message(index_data):
    """Format status update when no signals"""
    index_name = index_data.get("index", "UNKNOWN")
    status = index_data.get("status", "NO_SIGNALS")
    timestamp = index_data.get("timestamp", {}).get("local", "N/A")
    current_price = index_data.get("current_price", "N/A")

    msg = f"{EMOJI['chart']} <b>ORB STATUS UPDATE — {index_name}</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"{EMOJI['clock']} <b>{timestamp} IST</b>\n"
    msg += f"📍 <b>Spot:</b> ₹{current_price}\n"
    if status == "NO_SIGNALS":
        msg += f"❌ <b>No valid breakout signals yet</b>\n"
    elif status == "WAITING":
        msg += f"⏳ <b>Opening range forming...</b>\n"
    else:
        msg += f"{EMOJI['warning']} <b>Status:</b> {status}\n"
    msg += f"\n━━━━━━━━━━━━━━━━━━━━━\n"
    return msg


# ===================== MAIN =====================

def main():
    json_file = "orb_analysis_multi_trade.json"
    if not os.path.exists(json_file):
        print(f"❌ {json_file} not found")
        sys.exit(1)

    with open(json_file, "r") as f:
        data = json.load(f)

    sent_signals = load_sent_signals()
    messages_sent = 0

    for index_key in ["nifty", "banknifty"]:
        index_data = data.get("live_signals", {}).get(index_key, {})
        if not index_data:
            continue

        signals = index_data.get("signals", [])
        if signals:
            # Send only new signals
            for signal in signals:
                sig_hash = signal_hash(signal)
                if sig_hash not in sent_signals[index_key]:
                    msg = format_signal_message(signal, index_data.get("index", index_key.upper()))
                    if send_telegram_message(msg):
                        sent_signals[index_key].append(sig_hash)
                        messages_sent += 1
        else:
            # Send one status update per day
            status = index_data.get("status", "NO_SIGNALS")
            timestamp = index_data.get("timestamp", {}).get("local", "")[:10]  # date only
            status_hash = f"{status}_{timestamp}"
            status_list_key = f"{index_key}_status"
            if status_hash not in sent_signals.get(status_list_key, []):
                msg = format_no_signal_message(index_data)
                if send_telegram_message(msg):
                    sent_signals.setdefault(status_list_key, []).append(status_hash)
                    messages_sent += 1

    save_sent_signals(sent_signals)
    print(f"✅ Done. Messages sent: {messages_sent}")


if __name__ == "__main__":
    main()
