# Eldorado Seller Activity Monitoring System

## 📋 Overview

Sistem monitoring 24/7 untuk memantau aktivitas seller di Eldorado.gg dan mengirim notifikasi Telegram real-time ketika terjadi:
- 📦 **Produk Baru** - Seller list produk baru
- 💰 **Perubahan Harga** - Naik/turun dengan persentase
- ✏️ **Edit Produk** - Perubahan title, deskripsi, gambar, kategori
- 🗑️ **Hapus Produk** - Produk yang dihapus/unlisted

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│           Seller Monitoring System              │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. Fetch seller products (every 10 min)       │
│  2. Compare with database snapshot              │
│  3. Detect changes (new/price/edit/delete)      │
│  4. Send Telegram notification                  │
│  5. Update database                             │
│                                                 │
└─────────────────────────────────────────────────┘
         ↓                              ↓
   [SQLite DB]                  [Telegram Bot]
```

**Key Features:**
- ✅ Monitor 1-5 sellers simultaneously
- ✅ Configurable notifications per seller
- ✅ Detailed change history in database
- ✅ Low resource usage (~50 MB RAM)
- ✅ Independent from automation bot

---

## 🚀 Quick Start

### **Prerequisites**
- VPS Ubuntu 20.04+ dengan Python 3.8+
- Telegram account
- Repository sudah di-clone di VPS

---

## 📱 Step 1: Setup Telegram Bot (5 menit)

### **1.1 Create Bot**
```
1. Buka Telegram, search: @BotFather
2. Send command: /newbot
3. Follow instructions:
   - Bot name: Eldorado Monitor
   - Username: eldorado_monitor_bot (atau nama lain)
4. Simpan TOKEN yang diberikan
```

**Example Token:**
```
7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
```

### **1.2 Get Chat ID**

**Option A: Using userinfobot (recommended)**
```
1. Search: @userinfobot di Telegram
2. Start chat dan send /start
3. Bot akan reply dengan User ID Anda
4. Simpan ID tersebut sebagai CHAT_ID
```

**Option B: Manual method**
```bash
# Kirim message ke bot Anda terlebih dahulu
# Lalu run command ini (ganti YOUR_BOT_TOKEN):
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates

# Response akan berisi chat id:
# "chat":{"id":123456789,...
```

**Example Chat ID:**
```
123456789
```

---

## ⚙️ Step 2: Configure Environment

### **2.1 Update .env File**
```bash
cd /root/eldorado-automation
nano .env
```

**Add Telegram credentials:**
```bash
# Telegram Notifications
TELEGRAM_BOT_TOKEN=7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
TELEGRAM_CHAT_ID=123456789
```

**Full .env example:**
```bash
# Eldorado API Credentials
ELDORADO_API_KEY=your_api_key_here
ELDORADO_API_SECRET=your_api_secret_here

# Telegram Notifications
TELEGRAM_BOT_TOKEN=7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
TELEGRAM_CHAT_ID=123456789

# Bot Configuration
BOT_NAME=YourBotName
CHECK_INTERVAL_HOURS=6
```

### **2.2 Configure Sellers to Monitor**
```bash
nano seller_monitoring/seller_config.json
```

**Configuration format:**
```json
{
  "sellers": [
    {
      "username": "competitor_shop_1",
      "display_name": "Competitor A",
      "notify_new_product": true,
      "notify_price_change": true,
      "notify_edit": true,
      "notify_delete": true
    },
    {
      "username": "competitor_shop_2",
      "display_name": "Competitor B",
      "notify_new_product": true,
      "notify_price_change": true,
      "notify_edit": false,
      "notify_delete": false
    }
  ],
  "monitoring_interval_minutes": 10,
  "telegram_enabled": true,
  "rate_limit_delay_seconds": 2
}
```

**Configuration options:**
- `username`: Seller username di Eldorado.gg (required)
- `display_name`: Nama untuk display di notifikasi (optional)
- `notify_new_product`: Notifikasi produk baru (true/false)
- `notify_price_change`: Notifikasi perubahan harga (true/false)
- `notify_edit`: Notifikasi edit produk (true/false)
- `notify_delete`: Notifikasi produk dihapus (true/false)
- `monitoring_interval_minutes`: Interval checking (5-60 menit)

**Tips:**
- Minimal interval: 5 menit (hindari rate limiting)
- Optimal: 10-15 menit untuk 3-5 sellers
- Max 5 sellers untuk performa optimal

---

## 📦 Step 3: Install Dependencies

```bash
cd /root/eldorado-automation
git pull
pip3 install -r requirements.txt
```

**Verify installation:**
```bash
python3 -c "import telegram; print('Telegram bot library OK')"
```

---

## 🎯 Step 4: Test Monitoring System

### **4.1 Test Manual**
```bash
cd /root/eldorado-automation
python3 seller_monitoring/seller_monitor.py
```

**Expected output:**
```
[2024-01-15 10:00:00] Seller Monitor initialized
Monitoring 2 sellers
Interval: 10 minutes

============================================================
[2024-01-15 10:00:01] Starting monitoring cycle
============================================================

[2024-01-15 10:00:02] Checking seller: competitor_shop_1
Fetched 15 products
  [NEW] Valorant 100 VP - Rp 15,000
  [PRICE] PUBG UC 600: Rp 85,000 → Rp 79,000 (-7.1%)

✓ Notification sent for competitor_shop_1

[2024-01-15 10:00:05] Checking seller: competitor_shop_2
Fetched 22 products

============================================================
Cycle complete:
  Total products: 37
  Active products: 37
  Changes today: 2
============================================================

Waiting 10 minutes until next check...
```

**Press Ctrl+C to stop test**

### **4.2 Verify Telegram Notification**

Check your Telegram - you should receive:
```
🔔 SELLER ACTIVITY DETECTED

👤 Seller: Competitor A
━━━━━━━━━━━━━━━━━━━━

📦 NEW PRODUCTS (1)

• Valorant 100 VP
  💰 Rp 15,000
  📊 Stock: 999
  🔗 https://eldorado.gg/listings/abc123

💰 PRICE CHANGES (1)

• PUBG UC 600
  Old: Rp 85,000
  New: Rp 79,000
  Change: -7.1% 📉
  🔗 https://eldorado.gg/listings/def456

⏰ 2024-01-15 10:00:05
```

---

## 🔧 Step 5: Install Systemd Service (24/7 Running)

### **5.1 Copy Service File**
```bash
sudo cp eldorado-seller-monitor.service /etc/systemd/system/
```

### **5.2 Reload Systemd**
```bash
sudo systemctl daemon-reload
```

### **5.3 Enable & Start Service**
```bash
# Enable auto-start on boot
sudo systemctl enable eldorado-seller-monitor

# Start service now
sudo systemctl start eldorado-seller-monitor
```

### **5.4 Verify Service Status**
```bash
sudo systemctl status eldorado-seller-monitor
```

**Expected output:**
```
● eldorado-seller-monitor.service - Eldorado Seller Activity Monitor
   Loaded: loaded (/etc/systemd/system/eldorado-seller-monitor.service; enabled)
   Active: active (running) since Wed 2024-01-15 10:00:00 UTC; 1min ago
 Main PID: 12345 (python3)
   Status: "Monitoring 2 sellers..."
    Tasks: 1 (limit: 4915)
   Memory: 45.2M
```

✅ Service running successfully!

---

## 🎛️ Service Control Commands

### **Start/Stop/Restart**
```bash
# Start monitoring
sudo systemctl start eldorado-seller-monitor

# Stop monitoring
sudo systemctl stop eldorado-seller-monitor

# Restart monitoring
sudo systemctl restart eldorado-seller-monitor

# Check status
sudo systemctl status eldorado-seller-monitor
```

### **Enable/Disable Auto-Start**
```bash
# Enable auto-start on boot
sudo systemctl enable eldorado-seller-monitor

# Disable auto-start
sudo systemctl disable eldorado-seller-monitor
```

### **View Logs**
```bash
# View live logs (follow)
sudo journalctl -u eldorado-seller-monitor -f

# View recent logs
sudo journalctl -u eldorado-seller-monitor -n 100

# View logs from today
sudo journalctl -u eldorado-seller-monitor --since today

# View logs with timestamp
sudo journalctl -u eldorado-seller-monitor -o short-iso
```

---

## 🔀 Running Multiple Systems

### **Scenario 1: Monitor Only (Recommended for pure monitoring)**
```bash
# Start seller monitor
sudo systemctl start eldorado-seller-monitor

# Stop automation bot
sudo systemctl stop eldorado-automation
sudo systemctl disable eldorado-automation
```

### **Scenario 2: Both Systems Running**
```bash
# Start both services
sudo systemctl start eldorado-seller-monitor
sudo systemctl start eldorado-automation

# Check both statuses
sudo systemctl status eldorado-seller-monitor
sudo systemctl status eldorado-automation
```

### **Scenario 3: Automation Only**
```bash
# Stop monitor
sudo systemctl stop eldorado-seller-monitor

# Start automation
sudo systemctl start eldorado-automation
```

---

## 🗄️ Database Management

### **Database Location**
```
/root/eldorado-automation/seller_monitoring/monitor.db
```

### **View Database Content**
```bash
cd /root/eldorado-automation
sqlite3 seller_monitoring/monitor.db

# List tables
.tables

# View products
SELECT * FROM products LIMIT 10;

# View recent changes
SELECT * FROM change_log ORDER BY timestamp DESC LIMIT 20;

# View price history
SELECT * FROM price_history ORDER BY changed_at DESC LIMIT 20;

# Exit
.quit
```

### **Backup Database**
```bash
# Manual backup
cp seller_monitoring/monitor.db seller_monitoring/monitor_backup_$(date +%Y%m%d).db

# Scheduled backup (add to crontab)
crontab -e

# Add line: Backup daily at 3 AM
0 3 * * * cp /root/eldorado-automation/seller_monitoring/monitor.db /root/eldorado-automation/seller_monitoring/monitor_backup_$(date +\%Y\%m\%d).db
```

---

## 📊 Monitoring Statistics

### **Get Stats from Database**
```bash
cd /root/eldorado-automation
python3 -c "
from seller_monitoring.database import MonitoringDatabase
db = MonitoringDatabase()
stats = db.get_stats()
print(f'Total products: {stats[\"total_products\"]}')
print(f'Active products: {stats[\"active_products\"]}')
print(f'Sellers monitored: {stats[\"sellers\"]}')
print(f'Changes today: {stats[\"changes_today\"]}')
"
```

---

## 🐛 Troubleshooting

### **Problem: Service tidak start**
```bash
# Check service status
sudo systemctl status eldorado-seller-monitor

# View error logs
sudo journalctl -u eldorado-seller-monitor -n 50

# Common issues:
# 1. Missing .env file
# 2. Wrong TELEGRAM_BOT_TOKEN
# 3. Wrong working directory in .service file
```

**Solution:**
```bash
# Verify .env exists
ls -la /root/eldorado-automation/.env

# Test Python script manually
cd /root/eldorado-automation
python3 seller_monitoring/seller_monitor.py
```

### **Problem: Tidak terima notifikasi Telegram**
```bash
# Test Telegram bot manually
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
from shared.telegram_notifier import TelegramNotifier
notifier = TelegramNotifier()
notifier.send_message('🧪 Test notification from seller monitor')
"
```

**Common issues:**
1. ❌ Wrong TELEGRAM_BOT_TOKEN
2. ❌ Wrong TELEGRAM_CHAT_ID
3. ❌ Bot not started (send /start to your bot first)
4. ❌ `telegram_enabled: false` in config

**Solution:**
```bash
# Verify credentials
cat .env | grep TELEGRAM

# Test bot token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# Start chat with bot
# Go to Telegram and send /start to your bot
```

### **Problem: Seller tidak terdeteksi**
```bash
# Check seller username
# Visit: https://eldorado.gg/user/<seller_username>
# Make sure username is correct

# Test fetch manually
python3 -c "
from seller_monitoring.seller_monitor import SellerMonitor
monitor = SellerMonitor()
products = monitor.fetch_seller_products('seller_username')
print(f'Fetched {len(products)} products')
"
```

### **Problem: High CPU/Memory usage**
```bash
# Check resource usage
top -p $(pgrep -f seller_monitor)

# Solution: Increase interval in config
nano seller_monitoring/seller_config.json
# Set: "monitoring_interval_minutes": 15  (instead of 5)

# Restart service
sudo systemctl restart eldorado-seller-monitor
```

### **Problem: Database locked**
```bash
# This happens if multiple processes access DB
# Solution: Stop service, delete lock, restart

sudo systemctl stop eldorado-seller-monitor
rm -f seller_monitoring/monitor.db-journal
sudo systemctl start eldorado-seller-monitor
```

---

## 🔄 Update Monitoring System

```bash
# Pull latest code
cd /root/eldorado-automation
git pull

# Install new dependencies (if any)
pip3 install -r requirements.txt

# Restart service
sudo systemctl restart eldorado-seller-monitor

# Verify
sudo systemctl status eldorado-seller-monitor
```

---

## 📈 Performance Tips

### **Optimize for Multiple Sellers**
```json
{
  "monitoring_interval_minutes": 15,
  "rate_limit_delay_seconds": 3
}
```

### **Reduce Notification Spam**
```json
{
  "notify_new_product": true,
  "notify_price_change": true,
  "notify_edit": false,        // Disable minor edits
  "notify_delete": false       // Disable delete notifications
}
```

### **Resource Usage**
- **CPU:** <5% average
- **RAM:** 40-80 MB
- **Disk:** 10-50 MB (database grows over time)
- **Network:** Minimal (~1 MB/day for 5 sellers)

---

## 🔐 Security Best Practices

1. **Protect .env file**
```bash
chmod 600 /root/eldorado-automation/.env
```

2. **Regular backups**
```bash
# Backup database weekly
0 0 * * 0 cp /root/eldorado-automation/seller_monitoring/monitor.db /root/backups/monitor_$(date +\%Y\%m\%d).db
```

3. **Monitor logs**
```bash
# Setup log rotation
sudo nano /etc/logrotate.d/eldorado-monitor
```

---

## 📝 Configuration Examples

### **Example 1: Monitor Top 3 Competitors**
```json
{
  "sellers": [
    {
      "username": "top_seller_1",
      "display_name": "Market Leader",
      "notify_new_product": true,
      "notify_price_change": true,
      "notify_edit": true,
      "notify_delete": true
    },
    {
      "username": "top_seller_2",
      "display_name": "Close Competitor",
      "notify_new_product": true,
      "notify_price_change": true,
      "notify_edit": false,
      "notify_delete": false
    },
    {
      "username": "top_seller_3",
      "display_name": "Rising Star",
      "notify_new_product": true,
      "notify_price_change": false,
      "notify_edit": false,
      "notify_delete": false
    }
  ],
  "monitoring_interval_minutes": 15
}
```

### **Example 2: Price War Monitor (Focus on Price Changes)**
```json
{
  "sellers": [
    {
      "username": "competitor_1",
      "display_name": "Competitor A",
      "notify_new_product": false,
      "notify_price_change": true,
      "notify_edit": false,
      "notify_delete": false
    }
  ],
  "monitoring_interval_minutes": 5
}
```

---

## 🎓 Advanced Usage

### **Custom Notification Format**

Edit `seller_monitoring/seller_monitor.py` method `send_notifications()` to customize message format.

### **Add Webhook Integration**

Modify `seller_monitor.py` to send changes to webhook:
```python
def send_webhook(self, changes):
    webhook_url = os.getenv('WEBHOOK_URL')
    requests.post(webhook_url, json=changes)
```

### **Export Changes to CSV**
```bash
sqlite3 -header -csv seller_monitoring/monitor.db \
  "SELECT * FROM change_log WHERE date(timestamp) = date('now')" \
  > changes_today.csv
```

---

## 📞 Support

**Issues or Questions?**
- Check logs: `sudo journalctl -u eldorado-seller-monitor -f`
- Test manually: `python3 seller_monitoring/seller_monitor.py`
- Review config: `nano seller_monitoring/seller_config.json`

---

## ✅ Quick Checklist

- [ ] Telegram bot created
- [ ] Bot token added to .env
- [ ] Chat ID added to .env
- [ ] Sellers configured in seller_config.json
- [ ] Dependencies installed
- [ ] Manual test successful
- [ ] Systemd service installed
- [ ] Service running and active
- [ ] Telegram notifications working
- [ ] Database creating properly

**All checked? You're ready to monitor! 🚀**