# 📋 Commands Cheat Sheet

Quick reference untuk semua commands yang sering digunakan.

---

## 🚀 Quick Setup

### One-Command Setup
```bash
cd /root/eldorado-automation && python3 scripts/deploy_seller_monitoring.py
```

---

## 🎮 Service Control

### Check Status
```bash
sudo systemctl status eldorado-seller-monitor
```
Output: Shows active/inactive, uptime, last messages

### Start Service
```bash
sudo systemctl start eldorado-seller-monitor
```

### Stop Service
```bash
sudo systemctl stop eldorado-seller-monitor
```

### Restart Service
```bash
sudo systemctl restart eldorado-seller-monitor
```
Use after config changes

### Enable Auto-Start (Boot)
```bash
sudo systemctl enable eldorado-seller-monitor
```

### Disable Auto-Start
```bash
sudo systemctl disable eldorado-seller-monitor
```

---

## 📊 Monitoring & Logs

### View Live Logs
```bash
sudo journalctl -u eldorado-seller-monitor -f
```
Press `Ctrl+C` to exit

### View Last 50 Lines
```bash
sudo journalctl -u eldorado-seller-monitor -n 50
```

### View Logs Since Today
```bash
sudo journalctl -u eldorado-seller-monitor --since today
```

### View Logs Last Hour
```bash
sudo journalctl -u eldorado-seller-monitor --since "1 hour ago"
```

### Search Logs
```bash
sudo journalctl -u eldorado-seller-monitor | grep "ERROR"
```

---

## ⚙️ Configuration

### Edit Telegram Credentials
```bash
nano .env
```
Then restart:
```bash
sudo systemctl restart eldorado-seller-monitor
```

### Edit Seller List
```bash
nano seller_monitoring/seller_config.json
```
Then restart:
```bash
sudo systemctl restart eldorado-seller-monitor
```

### Reload Service After Changes
```bash
sudo systemctl daemon-reload
sudo systemctl restart eldorado-seller-monitor
```

---

## 🧪 Testing

### Manual Test Run
```bash
cd /root/eldorado-automation
python3 seller_monitoring/seller_monitor.py
```
Press `Ctrl+C` to stop

### Test Telegram Notification
```bash
python3 -c "
import os
from dotenv import load_dotenv
from shared.telegram_notifier import TelegramNotifier

load_dotenv()
notifier = TelegramNotifier()
notifier.send_message('🔔 Test notification from seller monitor')
"
```

### Test Scraping Single Seller
```bash
python3 -c "
from shared.scraper import fetch_seller_listings

products = fetch_seller_listings('SELLER_USERNAME')
print(f'Found {len(products)} products')
for p in products[:3]:
    print(f'- {p[\"title\"]}: {p[\"price\"]}')
"
```

---

## 📁 File Management

### View Configuration
```bash
cat seller_monitoring/seller_config.json
```

### View Environment Variables
```bash
cat .env
```

### Backup Database
```bash
cp seller_monitoring/monitor.db seller_monitoring/monitor.db.backup.$(date +%Y%m%d)
```

### View Database Size
```bash
du -h seller_monitoring/monitor.db
```

### List All Monitoring Files
```bash
ls -lh seller_monitoring/
```

---

## 🗄️ Database Queries

### Access Database
```bash
cd /root/eldorado-automation
sqlite3 seller_monitoring/monitor.db
```

### View All Sellers
```sql
SELECT * FROM sellers;
```

### View Latest Products
```sql
SELECT seller_username, title, price, stock 
FROM products 
ORDER BY last_seen DESC 
LIMIT 20;
```

### View Price Changes Today
```sql
SELECT * FROM price_history 
WHERE DATE(changed_at) = DATE('now') 
ORDER BY changed_at DESC;
```

### View All Changes Today
```sql
SELECT * FROM change_log 
WHERE DATE(detected_at) = DATE('now') 
ORDER BY detected_at DESC;
```

### Count Products Per Seller
```sql
SELECT seller_username, COUNT(*) as total_products 
FROM products 
GROUP BY seller_username;
```

### Exit Database
```sql
.quit
```

---

## 🔧 Maintenance

### Update Repository
```bash
cd /root/eldorado-automation
git pull origin main
```
Then restart:
```bash
sudo systemctl restart eldorado-seller-monitor
```

### Install/Update Dependencies
```bash
pip3 install -r requirements.txt --upgrade
```

### Check Python Version
```bash
python3 --version
```
Required: Python 3.8+

### Check Disk Space
```bash
df -h
```

### Check Memory Usage
```bash
free -h
```

### Check CPU Usage
```bash
top -bn1 | grep "eldorado"
```

---

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check detailed status
sudo systemctl status eldorado-seller-monitor -l

# Check logs
sudo journalctl -u eldorado-seller-monitor -n 100

# Verify service file
cat /etc/systemd/system/eldorado-seller-monitor.service

# Test manual run
python3 seller_monitoring/seller_monitor.py
```

### No Notifications
```bash
# Check Telegram bot
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage" \
  -d "chat_id=<YOUR_CHAT_ID>" \
  -d "text=Test message"

# Check environment variables
cat .env | grep TELEGRAM

# Test notification
python3 -c "
from shared.telegram_notifier import TelegramNotifier
notifier = TelegramNotifier()
notifier.send_message('Test')
"
```

### Scraping Errors
```bash
# Test connection
ping eldorado.gg

# Test scraping
python3 -c "
from shared.scraper import fetch_seller_listings
products = fetch_seller_listings('SELLER_USERNAME')
print(f'Found {len(products)} products')
"

# Check service logs
sudo journalctl -u eldorado-seller-monitor -f | grep ERROR
```

### Database Locked
```bash
# Stop service
sudo systemctl stop eldorado-seller-monitor

# Check processes
ps aux | grep seller_monitor

# Kill if needed
sudo killall python3

# Restart service
sudo systemctl start eldorado-seller-monitor
```

### Permission Errors
```bash
# Fix ownership
sudo chown -R $USER:$USER /root/eldorado-automation

# Fix permissions
chmod +x seller_monitoring/seller_monitor.py
chmod 644 seller_monitoring/seller_config.json
chmod 600 .env
```

---

## 🔄 Reset & Reinstall

### Reset Database (Fresh Start)
```bash
# Stop service
sudo systemctl stop eldorado-seller-monitor

# Backup old database
mv seller_monitoring/monitor.db seller_monitoring/monitor.db.old

# Restart (will create new database)
sudo systemctl start eldorado-seller-monitor
```

### Reinstall Service
```bash
# Stop and disable
sudo systemctl stop eldorado-seller-monitor
sudo systemctl disable eldorado-seller-monitor

# Remove service file
sudo rm /etc/systemd/system/eldorado-seller-monitor.service

# Reload daemon
sudo systemctl daemon-reload

# Re-run deployment
python3 scripts/deploy_seller_monitoring.py
```

### Clean Uninstall
```bash
# Stop service
sudo systemctl stop eldorado-seller-monitor

# Disable auto-start
sudo systemctl disable eldorado-seller-monitor

# Remove service
sudo rm /etc/systemd/system/eldorado-seller-monitor.service

# Reload daemon
sudo systemctl daemon-reload

# Remove database (optional)
rm seller_monitoring/monitor.db

# Remove config (optional)
rm seller_monitoring/seller_config.json
rm .env
```

---

## 📊 Statistics

### Service Uptime
```bash
sudo systemctl status eldorado-seller-monitor | grep "Active:"
```

### Log Size
```bash
sudo journalctl -u eldorado-seller-monitor --disk-usage
```

### Database Statistics
```bash
sqlite3 seller_monitoring/monitor.db << EOF
SELECT 'Total Sellers:', COUNT(*) FROM sellers;
SELECT 'Total Products:', COUNT(*) FROM products;
SELECT 'Total Price Changes:', COUNT(*) FROM price_history;
SELECT 'Total Changes Logged:', COUNT(*) FROM change_log;
EOF
```

### Memory Usage
```bash
ps aux | grep seller_monitor | grep -v grep | awk '{print $4}'
```

---

## 🚨 Emergency Commands

### Force Stop Everything
```bash
sudo systemctl stop eldorado-seller-monitor
sudo killall -9 python3
```

### Quick Status Check
```bash
sudo systemctl is-active eldorado-seller-monitor
```
Output: `active` or `inactive`

### Restart After Crash
```bash
sudo systemctl restart eldorado-seller-monitor
sudo journalctl -u eldorado-seller-monitor -f
```

---

## 💡 Useful Aliases

Add to `~/.bashrc` for shortcuts:

```bash
# Seller monitor aliases
alias sm-status='sudo systemctl status eldorado-seller-monitor'
alias sm-start='sudo systemctl start eldorado-seller-monitor'
alias sm-stop='sudo systemctl stop eldorado-seller-monitor'
alias sm-restart='sudo systemctl restart eldorado-seller-monitor'
alias sm-logs='sudo journalctl -u eldorado-seller-monitor -f'
alias sm-config='nano seller_monitoring/seller_config.json'
alias sm-db='sqlite3 seller_monitoring/monitor.db'
```

Reload:
```bash
source ~/.bashrc
```

Usage:
```bash
sm-status    # Check status
sm-logs      # View logs
sm-restart   # Restart service
```

---

## 📚 Quick Links

- **Setup Guide:** [QUICK_START.md](QUICK_START.md)
- **Full Documentation:** [SELLER_MONITORING_SETUP.md](SELLER_MONITORING_SETUP.md)
- **Scripts README:** [../scripts/README.md](../scripts/README.md)

---

**Print this for quick reference!** 📋✨