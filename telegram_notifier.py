#!/usr/bin/env python3
"""
Telegram ORB Signal Notifier
Reads orb_analysis_multi_trade.json and posts formatted messages to Telegram channel
"""

import json
import os
import sys
import requests
from datetime import datetime

# ===================== CONFIGURATION =====================

# ⚡ Use your Bot Token and Channel ID here
TELEGRAM_BOT_TOKEN = "8480675236:AAEWnz2d1pdxvsbAPabLEM4CSYoCdgmT62s"
TELEGRAM_CHAT_ID = "-1003713165195"  # Must be negative for channels

# Emoji mappings
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
    "calendar": "📅",
    "trend_up": "📈",
    "trend_down": "📉"
}

# ===================== HELPER FUNCTIONS =====================

def send_telegram_message(message, parse_mode="HTML"):
    """Send message to Telegram channel/group"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Message sent successfully")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def format_premium(value):
    if value is None:
        return "N/A"
    return f"₹{value:,.2f}"

def format_number(value):
    if value is None:
        return "N/A"
    return f"{value:,}"

def calculate_potential_profit(entry, target, stoploss):
    if entry is None or target is None or stoploss is None:
        return None, None
    profit = target - entry
    risk = entry - stoploss
    return profit, risk

def format_signal_message(signal, index_name):
    """Format a single signal into Telegram message"""
    signal_type = signal.get('type', 'UNKNOWN')
    emoji_signal = EMOJI.get(signal_type, "📊")
    
    msg = f"{EMOJI['bell']} <b>ORB BREAKOUT SIGNAL</b> {EMOJI['bell']}\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"{emoji_signal} <b>{index_name} - {signal_type}</b>\n\n"
    msg += f"{EMOJI['chart']} <b>Option:</b> <code>{signal.get('option_symbol', 'N/A')}</code>\n"
    msg += f"{EMOJI['money']} <b>Strike:</b> {signal.get('strike', 'N/A')}\n"
    msg += f"{EMOJI['clock']} <b>Time:</b> {signal.get('time', 'N/A')} IST\n"
    msg += f"{EMOJI['calendar']} <b>Expiry:</b> {signal.get('expiry', 'N/A')}\n\n"
    
    entry = signal.get('premium_entry')
    target = signal.get('target_premium')
    stoploss = signal.get('stoploss_premium')
    msg += f"<b>💵 PREMIUM LEVELS:</b>\n"
    msg += f"  • Entry: {format_premium(entry)}\n"
    msg += f"  • {EMOJI['target']} Target: {format_premium(target)}\n"
    msg += f"  • {EMOJI['stop']} Stoploss: {format_premium(stoploss)}\n\n"
    
    if entry and target and stoploss:
        profit, risk = calculate_potential_profit(entry, target, stoploss)
        if profit and risk:
            reward_ratio = profit / risk if risk > 0 else 0
            msg += f"<b>📊 RISK/REWARD:</b>\n"
            msg += f"  • Potential Profit: {format_premium(profit)}\n"
            msg += f"  • Potential Loss: {format_premium(risk)}\n"
            msg += f"  • R:R Ratio: 1:{reward_ratio:.2f}\n\n"
    
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"{EMOJI['warning']} <i>Educational only. Not financial advice.</i>"
    
    return msg

def format_no_signal_message(index_data):
    """Format 'no signal yet' status"""
    index_name = index_data.get('index', 'UNKNOWN')
    status = index_data.get('status', 'UNKNOWN')
    msg = f"{EMOJI['chart']} <b>ORB STATUS UPDATE — {index_name}</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    timestamp = index_data.get('timestamp', {})
    time_str = timestamp.get('local', 'N/A')
    msg += f"{EMOJI['clock']} <b>{time_str} IST</b>\n"
    
    current_price = index_data.get('current_price', 'N/A')
    msg += f"📍 <b>Spot:</b> ₹{current_price}\n\n"
    
    if status == "NO_SIGNALS":
        msg += f"❌ <b>No valid breakout signals yet</b>\n\n"
    
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"⏳ <i>Waiting for high-probability setup...</i>"
    return msg

def load_previous_signals():
    sent_file = ".sent_signals.json"
    if os.path.exists(sent_file):
        try:
            with open(sent_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"nifty": [], "banknifty": []}

def save_sent_signals(sent_signals):
    sent_file = ".sent_signals.json"
    with open(sent_file, 'w') as f:
        json.dump(sent_signals, f, indent=2)

def signal_hash(signal):
    return f"{signal.get('time')}_{signal.get('type')}_{signal.get('strike')}"

# ===================== MAIN =====================

def main():
    json_file = "orb_analysis_multi_trade.json"
    if not os.path.exists(json_file):
        print(f"❌ ERROR: {json_file} not found")
        sys.exit(1)
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Failed to read JSON: {e}")
        sys.exit(1)
    
    sent_signals = load_previous_signals()
    messages_sent = 0
    
    for index_key in ["nifty", "banknifty"]:
        index_data = data.get('live_signals', {}).get(index_key, {})
        if not index_data:
            continue
        
        signals = index_data.get('signals', [])
        if signals:
            for signal in signals:
                sig_hash = signal_hash(signal)
                if sig_hash not in sent_signals[index_key]:
                    index_name = index_data.get('index', index_key.upper())
                    msg = format_signal_message(signal, index_name)
                    if send_telegram_message(msg):
                        sent_signals[index_key].append(sig_hash)
                        messages_sent += 1
        else:
            status = index_data.get('status', 'NO_SIGNALS')
            timestamp = index_data.get('timestamp', {}).get('local', '')
            status_hash = f"status_{status}_{timestamp[:10]}"
            
            if status_hash not in sent_signals.get(f'{index_key}_status', []):
                index_name = index_data.get('index', index_key.upper())
                msg = format_no_signal_message(index_data)
                if send_telegram_message(msg):
                    if f'{index_key}_status' not in sent_signals:
                        sent_signals[f'{index_key}_status'] = []
                    sent_signals[f'{index_key}_status'].append(status_hash)
                    messages_sent += 1
    
    save_sent_signals(sent_signals)
    
    print(f"✅ Telegram notification check complete")
    print(f"   Messages sent: {messages_sent}")

if __name__ == "__main__":
    main()
