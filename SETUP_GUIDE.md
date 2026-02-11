# 🚀 Complete Setup Guide - ORB Automation with Telegram

## ✅ All 6 Critical Fixes Applied

### 🔧 What Was Fixed:

| Problem | Status | Fix |
|---------|--------|-----|
| ❌ Too many print() logs | ✅ FIXED | Removed all console prints |
| ❌ No safe JSON write | ✅ FIXED | Atomic write with .tmp file |
| ❌ No guarantee file created | ✅ FIXED | Fallback JSON on error |
| ❌ Local time assumptions | ✅ FIXED | IST timezone (pytz) |
| ❌ Yahoo API failure breaks everything | ✅ FIXED | Try-except wrapper |
| ❌ Telegram integration | ✅ ADDED | Beautiful formatted messages |

---

## 📁 File Structure

```
your-repo/
├── orb_analysis_fixed.py          # Main ORB engine (UPDATED)
├── telegram_notifier.py            # Telegram bot (NEW)
├── .github/
│   └── workflows/
│       └── orb_automation.yml     # GitHub Actions (NEW)
├── orb_analysis_multi_trade.json  # Output (auto-generated)
└── .sent_signals.json             # Tracking sent signals (auto-generated)
```

---

## 🔐 Step 1: Create Telegram Bot

### 1.1 Talk to BotFather

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name: `My ORB Signals Bot`
4. Choose a username: `my_orb_signals_bot` (must end with `_bot`)
5. **Copy the TOKEN** - looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 1.2 Create Your Channel/Group

**Option A: Private Channel (Recommended)**
1. Create new channel in Telegram
2. Name it: `ORB Trading Signals`
3. Make it **Private**
4. Add your bot as **Administrator**

**Option B: Private Group**
1. Create new group
2. Add your bot to the group
3. Make bot admin

### 1.3 Get Chat ID

**Method 1: Using IDBot**
1. Add `@userinfobot` to your channel/group
2. It will send the chat ID
3. Remove the bot after

**Method 2: Manual**
1. Send a message to your channel/group
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for `"chat":{"id":-1001234567890}`
4. Copy the ID (including the minus sign!)

---

## 🔐 Step 2: Add Secrets to GitHub

1. Go to your GitHub repo
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these two secrets:

**Secret 1:**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` (your bot token)

**Secret 2:**
- Name: `TELEGRAM_CHAT_ID`
- Value: `-1001234567890` (your channel/group ID)

---

## 📂 Step 3: Upload Files to GitHub

### 3.1 Create the workflow directory

```bash
mkdir -p .github/workflows
```

### 3.2 Copy files to correct locations

```bash
# Main Python scripts
cp orb_analysis_fixed.py ./
cp telegram_notifier.py ./

# GitHub workflow
cp github_workflow.yml .github/workflows/orb_automation.yml
```

### 3.3 Commit and push

```bash
git add .
git commit -m "Add ORB automation with Telegram notifications"
git push
```

---

## ⚙️ Step 4: Configure GitHub Actions

### 4.1 Enable Actions

1. Go to your repo on GitHub
2. Click **Actions** tab
3. Enable workflows if disabled

### 4.2 Adjust Schedule (Optional)

Edit `.github/workflows/orb_automation.yml`:

```yaml
schedule:
  # Current: Every 5 minutes from 9:15 AM - 3:30 PM IST
  - cron: '*/5 3-10 * * 1-5'
  
  # For testing (every minute):
  - cron: '* * * * *'
  
  # Every 10 minutes instead:
  - cron: '*/10 3-10 * * 1-5'
```

**CRON timezone is UTC!**
- IST 9:15 AM = UTC 3:45 AM
- IST 3:30 PM = UTC 10:00 AM

---

## 🧪 Step 5: Test Locally (Optional)

### 5.1 Install dependencies

```bash
pip install yfinance pandas numpy pytz requests
```

### 5.2 Test ORB engine

```bash
python orb_analysis_fixed.py
```

**Expected output:**
- File created: `orb_analysis_multi_trade.json`
- No console spam
- Even if it errors, JSON is created

### 5.3 Test Telegram bot

```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
python telegram_notifier.py
```

**Expected output:**
- Message sent to your Telegram channel
- `.sent_signals.json` created

---

## 📱 Step 6: What Messages Look Like

### New Signal Message:

```
🔔 ORB BREAKOUT SIGNAL 🔔
━━━━━━━━━━━━━━━━━━━━━

🟢📈 NIFTY - CALL

📊 Option: NIFTY 12FEB26 26000 CE
💰 Strike: 26000
🕐 Time: 10:05 IST
📅 Expiry: 2026-02-12

💵 PREMIUM LEVELS:
  • Entry: ₹142.00
  • 🎯 Target: ₹185.00
  • 🛑 Stoploss: ₹92.00

📊 RISK/REWARD:
  • Potential Profit: ₹43.00 (30%)
  • Potential Loss: ₹50.00 (35%)
  • R:R Ratio: 1:0.86

📈 MARKET DATA:
  • Spot Price: ₹25992
  • OI: 150,000
  • Volume: 5,000

✅ QUALITY CHECKS:
  • Candle Body: 75.5%
  • Volume Surge: 2.3x
  • ATR: Expanding

🌍 MARKET CONTEXT:
  • VIX: 15.2
  • ORB Range: ₹85.50
  • Bias: CALL

━━━━━━━━━━━━━━━━━━━━━
⚠️ Educational only. Not financial advice.
```

### Summary Message (No Signals):

```
📊 ORB ENGINE UPDATE 📊
━━━━━━━━━━━━━━━━━━━━━

Status: NO_SIGNALS
Updated: 2026-02-12 10:00:00 IST

✅ No signals yet

Waiting for high-quality breakout...

NIFTY: ₹25992
BANKNIFTY: ₹54123

━━━━━━━━━━━━━━━━━━━━━
Next update in 5 minutes
```

---

## 🔍 Step 7: Monitoring & Debugging

### 7.1 Check GitHub Actions Logs

1. Go to **Actions** tab
2. Click on latest workflow run
3. Check each step:
   - ✅ Run ORB Analysis
   - ✅ Verify JSON created
   - ✅ Send Telegram Notifications

### 7.2 Common Issues

**Issue 1: Telegram messages not sending**
- Check bot token is correct
- Check chat ID (include minus sign if group/channel)
- Make sure bot is admin in channel

**Issue 2: Workflow not running**
- Check cron schedule
- Enable Actions in Settings
- Check it's weekday (Mon-Fri)

**Issue 3: JSON not created**
- Check Python errors in logs
- Should never happen with new error handling

**Issue 4: Duplicate messages**
- `.sent_signals.json` tracks sent signals
- Delete it to reset and resend all

---

## 🎯 Advanced: Target Reached Notifications

To add "Target Reached" notifications, you'll need to:

1. **Track entry prices** in a database or file
2. **Fetch current option prices** every 5 minutes
3. **Compare with targets** and send alerts

Example addition to `telegram_notifier.py`:

```python
def check_targets(data, active_trades):
    """
    Check if any active trades hit target/stoploss
    active_trades = {
        "NIFTY 12FEB26 26000 CE": {
            "entry": 142,
            "target": 185,
            "stoploss": 92
        }
    }
    """
    # Fetch current option prices using yfinance
    # Compare with targets
    # Send 🔥 TARGET REACHED or 🛑 STOPLOSS HIT message
    pass
```

This requires more complex state management and is Phase 2.

---

## 📊 Step 8: Customization

### Change Target/Stoploss Percentages

Edit `orb_analysis_fixed.py`:

```python
CONFIG = {
    "premium_target": 30,      # 30% → Change to 40 for +40%
    "premium_stoploss": 35,    # 35% → Change to 30 for -30%
    ...
}
```

### Change Signal Filters

```python
CONFIG = {
    "candle_body_min_pct": 60,        # Lower for more signals
    "volume_surge_multiplier": 1.8,   # Lower for more signals
    "fresh_move_window_minutes": 90,  # Increase for late signals
    ...
}
```

### Customize Telegram Messages

Edit `telegram_notifier.py`:

```python
EMOJI = {
    "CALL": "🚀💚",    # Change to whatever you like
    "PUT": "⚡❤️",
    ...
}
```

---

## 🎉 You're Done!

Your automation is now:

✅ Running every 5 minutes during market hours  
✅ Analyzing NIFTY & BANKNIFTY for ORB breakouts  
✅ Selecting ITM option strikes automatically  
✅ Fetching live option premiums  
✅ Calculating targets & stoploss  
✅ Sending beautiful Telegram notifications  
✅ Never crashing (bulletproof error handling)  
✅ Avoiding duplicate messages  
✅ Working in IST timezone correctly  

---

## 📞 Support

**If something breaks:**

1. Check GitHub Actions logs
2. Verify Telegram bot token & chat ID
3. Test locally first
4. Check `.sent_signals.json` exists
5. Ensure `pytz` is installed

**Quick test command:**

```bash
# Test end-to-end
python orb_analysis_fixed.py && \
TELEGRAM_BOT_TOKEN="xxx" TELEGRAM_CHAT_ID="yyy" \
python telegram_notifier.py
```

---

## 🔄 Daily Workflow

**Morning (9:15 AM IST):**
- Automation starts
- First run establishes ORB levels
- No signals yet (waiting for breakout)

**10:00 AM - 12:30 PM:**
- Every 5 minutes, checks for breakouts
- If signal found → Telegram notification
- JSON file updated
- Cooldown prevents spam

**After 12:30 PM:**
- No new signals (CONFIG cutoff)
- Existing trades monitored (Phase 2)

**Market Close (3:30 PM):**
- Automation stops
- Final JSON saved
- Ready for next day

---

## 🚀 Next Steps (Optional)

1. **Phase 2: Live Position Tracking**
   - Store active positions in database
   - Track P&L in real-time
   - Send target/SL hit notifications

2. **Phase 3: Web Dashboard**
   - Show signals on webpage
   - Real-time updates
   - Historical performance

3. **Phase 4: Broker Integration**
   - Auto-place orders via broker API
   - Fully automated trading
   - Position management

For now, you have a **professional signal generation system** that works 24/7! 🎯
