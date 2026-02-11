#!/usr/bin/env python3
"""
Telegram ORB Signal Notifier
Reads orb_analysis_multi_trade.json and posts beautiful formatted messages
"""

import json
import os
import sys
import requests
from datetime import datetime

# ===================== CONFIGURATION =====================

TELEGRAM_BOT_TOKEN = os.environ.get("8480675236:AAEWnz2d1pdxvsbAPabLEM4CSYoCdgmT62s")
TELEGRAM_CHAT_ID = os.environ.get("1003713165195")

# Emoji mappings
EMOJI = {
    "CALL": "🟢📈",  # Green up arrow for calls
    "PUT": "🔴📉",   # Red down arrow for puts
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
        print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
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
            print(f"✅ Message sent successfully")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False


def format_premium(value):
    """Format premium nicely"""
    if value is None:
        return "N/A"
    return f"₹{value:,.2f}"


def format_number(value):
    """Format large numbers with commas"""
    if value is None:
        return "N/A"
    return f"{value:,}"


def calculate_potential_profit(entry, target, stoploss):
    """Calculate potential profit and risk"""
    if entry is None or target is None or stoploss is None:
        return None, None
    
    profit = target - entry
    risk = entry - stoploss
    
    return profit, risk


def format_signal_message(signal, index_name):
    """Format a single signal into beautiful Telegram message"""
    
    signal_type = signal.get('type', 'UNKNOWN')
    emoji_signal = EMOJI.get(signal_type, "📊")
    
    # Header
    msg = f"{EMOJI['bell']} <b>ORB BREAKOUT SIGNAL</b> {EMOJI['bell']}\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Index and signal type
    msg += f"{emoji_signal} <b>{index_name} - {signal_type}</b>\n\n"
    
    # Option details
    msg += f"{EMOJI['chart']} <b>Option:</b> <code>{signal.get('option_symbol', 'N/A')}</code>\n"
    msg += f"{EMOJI['money']} <b>Strike:</b> {signal.get('strike', 'N/A')}\n"
    msg += f"{EMOJI['clock']} <b>Time:</b> {signal.get('time', 'N/A')} IST\n"
    msg += f"{EMOJI['calendar']} <b>Expiry:</b> {signal.get('expiry', 'N/A')}\n\n"
    
    # Entry and targets
    entry = signal.get('premium_entry')
    target = signal.get('target_premium')
    stoploss = signal.get('stoploss_premium')
    
    msg += f"<b>💵 PREMIUM LEVELS:</b>\n"
    msg += f"  • Entry: {format_premium(entry)}\n"
    msg += f"  • {EMOJI['target']} Target: {format_premium(target)}\n"
    msg += f"  • {EMOJI['stop']} Stoploss: {format_premium(stoploss)}\n\n"
    
    # Profit/Risk calculation
    if entry and target and stoploss:
        profit, risk = calculate_potential_profit(entry, target, stoploss)
        if profit and risk:
            reward_ratio = profit / risk if risk > 0 else 0
            msg += f"<b>📊 RISK/REWARD:</b>\n"
            msg += f"  • Potential Profit: {format_premium(profit)} ({signal.get('target_pct', 30)}%)\n"
            msg += f"  • Potential Loss: {format_premium(risk)} ({signal.get('stoploss_pct', 35)}%)\n"
            msg += f"  • R:R Ratio: 1:{reward_ratio:.2f}\n\n"
    
    # Market data
    msg += f"<b>📈 MARKET DATA:</b>\n"
    msg += f"  • Spot Price: ₹{signal.get('spot_price', 'N/A')}\n"
    msg += f"  • OI: {format_number(signal.get('oi'))}\n"
    msg += f"  • Volume: {format_number(signal.get('volume'))}\n\n"
    
    # Quality indicators
    quality = signal.get('breakout_quality', {})
    if quality:
        msg += f"<b>✅ QUALITY CHECKS:</b>\n"
        msg += f"  • Candle Body: {quality.get('candle_body_pct', 'N/A')}%\n"
        msg += f"  • Volume Surge: {quality.get('volume_surge', 'N/A')}x\n"
        msg += f"  • ATR: {'Expanding' if quality.get('atr_expanding') else 'N/A'}\n\n"
    
    # Context
    context = signal.get('market_context', {})
    if context:
        msg += f"<b>🌍 MARKET CONTEXT:</b>\n"
        msg += f"  • VIX: {context.get('vix', 'N/A')}\n"
        msg += f"  • ORB Range: ₹{context.get('orb_range', 'N/A')}\n"
        if context.get('open_bias'):
            msg += f"  • Bias: {context.get('open_bias')}\n"
    
    msg += f"\n━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"{EMOJI['warning']} <i>Educational only. Not financial advice.</i>"
    
    return msg


def format_summary_message(data):
    """Format summary message when no new signals"""
    
    msg = f"{EMOJI['chart']} <b>ORB ENGINE UPDATE</b> {EMOJI['chart']}\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Status
    status = data.get('status', 'UNKNOWN')
    msg += f"<b>Status:</b> {status}\n"
    
    # Timestamp
    generated_at = data.get('generated_at', 'Unknown')
    msg += f"<b>Updated:</b> {generated_at}\n\n"
    
    # Check both indices
    nifty = data.get('live_signals', {}).get('nifty', {})
    banknifty = data.get('live_signals', {}).get('banknifty', {})
    
    nifty_signals = len(nifty.get('signals', []))
    banknifty_signals = len(banknifty.get('signals', []))
    
    total_signals = nifty_signals + banknifty_signals
    
    if total_signals == 0:
        msg += f"{EMOJI['check']} <b>No signals yet</b>\n\n"
        msg += f"<i>Waiting for high-quality breakout...</i>\n\n"
        
        # Show current prices
        if 'current_price' in nifty:
            msg += f"NIFTY: ₹{nifty['current_price']}\n"
        if 'current_price' in banknifty:
            msg += f"BANKNIFTY: ₹{banknifty['current_price']}\n"
    else:
        msg += f"{EMOJI['rocket']} <b>Active Signals: {total_signals}</b>\n\n"
        msg += f"  • NIFTY: {nifty_signals} signal(s)\n"
        msg += f"  • BANKNIFTY: {banknifty_signals} signal(s)\n"
    
    msg += f"\n━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"<i>Next update in 5 minutes</i>"
    
    return msg


def load_previous_signals():
    """Load previously sent signals to avoid duplicates"""
    sent_file = ".sent_signals.json"
    if os.path.exists(sent_file):
        try:
            with open(sent_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"nifty": [], "banknifty": []}


def save_sent_signals(sent_signals):
    """Save sent signals to avoid duplicates"""
    sent_file = ".sent_signals.json"
    with open(sent_file, 'w') as f:
        json.dump(sent_signals, f, indent=2)


def signal_hash(signal):
    """Create unique hash for signal to detect duplicates"""
    return f"{signal.get('time')}_{signal.get('type')}_{signal.get('strike')}"


# ===================== MAIN =====================

def main():
    # Load JSON file
    json_file = "orb_analysis_multi_trade.json"
    
    if not os.path.exists(json_file):
        print(f"ERROR: {json_file} not found")
        sys.exit(1)
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to read JSON: {e}")
        sys.exit(1)
    
    # Load previously sent signals
    sent_signals = load_previous_signals()
    
    # Check for new signals
    new_signals_found = False
    
    # Process NIFTY signals
    nifty = data.get('live_signals', {}).get('nifty', {})
    nifty_signals = nifty.get('signals', [])
    
    for signal in nifty_signals:
        sig_hash = signal_hash(signal)
        if sig_hash not in sent_signals['nifty']:
            # New signal! Send it
            msg = format_signal_message(signal, "NIFTY")
            if send_telegram_message(msg):
                sent_signals['nifty'].append(sig_hash)
                new_signals_found = True
    
    # Process BANKNIFTY signals
    banknifty = data.get('live_signals', {}).get('banknifty', {})
    banknifty_signals = banknifty.get('signals', [])
    
    for signal in banknifty_signals:
        sig_hash = signal_hash(signal)
        if sig_hash not in sent_signals['banknifty']:
            # New signal! Send it
            msg = format_signal_message(signal, "BANKNIFTY")
            if send_telegram_message(msg):
                sent_signals['banknifty'].append(sig_hash)
                new_signals_found = True
    
    # Save sent signals
    save_sent_signals(sent_signals)
    
    # If no new signals and this is first run of the day, send summary
    # (Optional: can be configured to send every hour or at specific times)
    if not new_signals_found:
        # Check if we should send summary (e.g., at 9:45 AM IST)
        current_hour = datetime.now().hour
        current_minute = datetime.now().minute
        
        # Send summary at market open (9:45 AM) if no signals yet
        if current_hour == 9 and current_minute >= 45 and current_minute < 50:
            summary_msg = format_summary_message(data)
            send_telegram_message(summary_msg)
    
    print(f"✅ Telegram notification check complete")
    print(f"   New signals sent: {new_signals_found}")


if __name__ == "__main__":
    main()
