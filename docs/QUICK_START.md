# 🚀 Quick Start Guide - Eldorado Seller Monitoring

Setup monitoring system dalam **5 menit**! Sistem ini akan monitor competitor sellers 24/7 dan kirim notifikasi Telegram.

## ⚡ Super Quick Setup (1 Command)

```bash
cd /root/eldorado-automation
python3 scripts/deploy_seller_monitoring.py
```

Script akan:
- ✅ Setup Telegram bot credentials
- ✅ Configure sellers to monitor
- ✅ Test system
- ✅ Install 24/7 service
- ✅ Start monitoring

**That's it!** Follow the interactive prompts.

---

## 📋 Prerequisites

**Before running, prepare:**

### 1. Telegram Bot Token
1. Chat dengan **@BotFather** di Telegram
2. Ketik `/newbot`
3. Ikuti instruksi (nama bot, username)
4. Copy token yang diberikan
   ```
   Format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 2. Telegram Chat ID
1. Chat dengan **@userinfobot** di Telegram
2. Bot akan reply dengan your user info
3. Copy **Chat ID** (number)
   ```
   Format: 1234567890
   ```

### 3. Seller Usernames
- Buka **eldorado.gg**
- Cari competitor sellers
- Copy **username** dari URL:
  ```
  https://eldorado.gg/sellers/USERNAME
                              ^^^^^^^^
                              Copy this!
  ```
- Siapkan 1-5 usernames

---

## 🎯 Interactive Deployment

Jalankan script dan ikuti prompts:

```bash
python3 scripts/deploy_seller_monitoring.py
```

### Step 1: Telegram Setup
```
Enter Telegram Bot Token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
Enter Telegram Chat ID: 1234567890
```

### Step 2: Configure Sellers
```
Enter seller username: competitor1
  Notify new products? [Y/n]: y
  Notify price changes? [Y/n]: y
  Notify product edits? [Y/n]: y
  Notify deletions? [Y/n]: y

Add another seller? [y/N]: y

Enter seller username: competitor2
  Notify new products? [Y/n]: y
  Notify price changes? [Y/n]: n
  Notify product edits? [Y/n]: n
  Notify deletions? [Y/n]: n
```

### Step 3: Set Interval
```
Check interval in minutes [10]: 15
```
Recommended: 10-15 minutes

### Step 4: Install & Start
```
Install systemd service? [Y/n]: y
Start monitoring service now? [Y/n]: y
```

Done! 🎉

---

## 📱 What to Expect

**First Run (10-15 minutes):**
- System scrapes all current products
- Saves to database
- No notifications (baseline)

**After First Check:**
- System compares new data with baseline
- Sends Telegram notification if changes detected

**Example Notification:**
```
🔔 SELLER ACTIVITY DETECTED

👤 Seller: competitor1
━━━━━━━━━━━━━━━━━━━━

📦 NEW PRODUCTS (2)

• Valorant 475 VP
  💰 Rp 45,000
  📊 Stock: 999
  🔗 https://eldorado.gg/listings/abc123

• PUBG UC 600
  💰 Rp 85,000
  📊 Stock: 999
  🔗 https://eldorado.gg/listings/def456

⏰ 2024-01-15 10:30:15
```

---

## 🎮 Control Commands

### Check Status
```bash
sudo systemctl status eldorado-seller-monitor
```
Shows: active, running time, last messages

### View Live Logs
```bash
sudo journalctl -u eldorado-seller-monitor -f
```
Press `Ctrl+C` to exit

### Stop Monitoring
```bash
sudo systemctl stop eldorado-seller-monitor
```

### Start Monitoring
```bash
sudo systemctl start eldorado-seller-monitor
```

### Restart (after config changes)
```bash
sudo systemctl restart eldorado-seller-monitor
```

### Disable Auto-Start on Boot
```bash
sudo systemctl disable eldorado-seller-monitor
```

### Enable Auto-Start on Boot
```bash
sudo systemctl enable eldorado-seller-monitor
```

---

## ⚙️ Configuration Files

### Telegram Credentials
```bash
nano .env
```
Edit:
```env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### Seller List
```bash
nano seller_monitoring/seller_config.json
```
Edit:
```json
{
  "sellers": [
    {
      "username": "competitor1",
      "notify_new_products": true,
      "notify_price_changes": true,
      "notify_edits": true,
      "notify_deletions": true
    }
  ],
  "check_interval_minutes": 10
}
```

**After editing, restart:**
```bash
sudo systemctl restart eldorado-seller-monitor
```

---

## 🔍 Manual Testing

Test without installing service:

```bash
cd /root/eldorado-automation
python3 seller_monitoring/seller_monitor.py
```

Watch output for errors. Press `Ctrl+C` to stop.

---

## 📊 Database Access

All data stored in SQLite:
```bash
cd /root/eldorado-automation
sqlite3 seller_monitoring/monitor.db
```

Useful queries:
```sql
-- View all monitored sellers
SELECT * FROM sellers;

-- View latest products
SELECT * FROM products ORDER BY last_seen DESC LIMIT 20;

-- View price changes
SELECT * FROM price_history ORDER BY changed_at DESC LIMIT 20;

-- View change log
SELECT * FROM change_log ORDER BY detected_at DESC LIMIT 20;

-- Exit
.quit
```

---

## 🛠️ Troubleshooting

### Service Not Starting
```bash
sudo journalctl -u eldorado-seller-monitor -n 50
```
Check last 50 log lines for errors

### No Notifications Received
1. **Check service is running:**
   ```bash
   sudo systemctl status eldorado-seller-monitor
   ```

2. **Check Telegram bot:**
   - Chat dengan your bot
   - Send any message
   - Bot should respond (if webhook not set)

3. **Test Telegram manually:**
   ```bash
   python3 -c "
   import os
   from dotenv import load_dotenv
   from shared.telegram_notifier import TelegramNotifier
   
   load_dotenv()
   notifier = TelegramNotifier()
   notifier.send_message('Test notification')
   "
   ```

### Scraping Errors
1. **Check internet connection:**
   ```bash
   ping eldorado.gg
   ```

2. **Test scraping manually:**
   ```bash
   python3 seller_monitoring/seller_monitor.py --test
   ```

3. **Check seller username:**
   - Visit: `https://eldorado.gg/sellers/USERNAME`
   - Make sure page loads

### Permission Errors
```bash
# Fix file permissions
sudo chown -R $USER:$USER /root/eldorado-automation
chmod +x seller_monitoring/seller_monitor.py
```

---

## 🎛️ Advanced Configuration

### Change Check Interval
Edit `seller_config.json`:
```json
{
  "check_interval_minutes": 15
}
```
Range: 5-60 minutes
- Lower = More responsive, more API calls
- Higher = Less responsive, fewer API calls

### Selective Notifications
Per-seller configuration:
```json
{
  "username": "competitor1",
  "notify_new_products": true,    // Notify new listings
  "notify_price_changes": true,   // Notify price changes
  "notify_edits": false,          // Ignore edits
  "notify_deletions": false       // Ignore deletions
}
```

### Add More Sellers
Edit `seller_config.json`, add to array:
```json
{
  "sellers": [
    {...},
    {
      "username": "new_seller",
      "notify_new_products": true,
      "notify_price_changes": true,
      "notify_edits": true,
      "notify_deletions": true
    }
  ]
}
```

Restart service after changes:
```bash
sudo systemctl restart eldorado-seller-monitor
```

---

## 🚨 Uninstall

Remove monitoring system:

```bash
# Stop service
sudo systemctl stop eldorado-seller-monitor

# Disable auto-start
sudo systemctl disable eldorado-seller-monitor

# Remove service file
sudo rm /etc/systemd/system/eldorado-seller-monitor.service

# Reload systemd
sudo systemctl daemon-reload

# Remove database (optional)
rm -rf seller_monitoring/monitor.db
```

---

## 💡 Tips & Best Practices

1. **Start with 2-3 sellers** untuk testing
2. **Use 10-15 minute interval** untuk balance
3. **Check logs first day** untuk ensure working
4. **Monitor Telegram** untuk notifications
5. **Backup database** occasionally:
   ```bash
   cp seller_monitoring/monitor.db seller_monitoring/monitor.db.backup
   ```

---

## 📚 Additional Resources

- **Full Documentation:** [SELLER_MONITORING_SETUP.md](SELLER_MONITORING_SETUP.md)
- **VPS Deployment:** [VPS_DEPLOYMENT_TELEGRAM.md](VPS_DEPLOYMENT_TELEGRAM.md)
- **GitHub Repo:** [eldorado-automation](https://github.com/yourusername/eldorado-automation)

---

## 🆘 Support

Issues? Questions?

1. **Check logs:** `sudo journalctl -u eldorado-seller-monitor -f`
2. **Test manually:** `python3 seller_monitoring/seller_monitor.py`
3. **Review docs:** [SELLER_MONITORING_SETUP.md](SELLER_MONITORING_SETUP.md)

---

## ✨ Features Summary

✅ **Monitor unlimited sellers** (recommended 2-5)  
✅ **Real-time Telegram notifications**  
✅ **Track new products, price changes, edits, deletions**  
✅ **SQLite database** for history  
✅ **24/7 operation** via systemd  
✅ **Auto-restart** on failure  
✅ **Low resources** (<50 MB RAM, <5% CPU)  
✅ **No API key required** (web scraping)  
✅ **Easy setup** (5 minutes)  

---

**Ready to monitor? Run the deployment script!** 🚀

```bash
python3 scripts/deploy_seller_monitoring.py
```