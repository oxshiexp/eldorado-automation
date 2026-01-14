# 🚀 VPS Deployment Guide with Telegram Notifications

Complete guide to deploy Eldorado Automation on VPS with 24/7 running, auto-start on reboot, and Telegram notifications.

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Step 1: VPS Setup](#step-1-vps-setup)
- [Step 2: Install Dependencies](#step-2-install-dependencies)
- [Step 3: Clone Repository](#step-3-clone-repository)
- [Step 4: Setup Telegram Bot](#step-4-setup-telegram-bot)
- [Step 5: Configure Environment](#step-5-configure-environment)
- [Step 6: Setup Systemd Service (Auto-Start)](#step-6-setup-systemd-service-auto-start)
- [Step 7: Start and Monitor Service](#step-7-start-and-monitor-service)
- [Troubleshooting](#troubleshooting)
- [Maintenance Commands](#maintenance-commands)

---

## 📋 Prerequisites

### Minimum VPS Requirements
- **CPU**: 1 vCore
- **RAM**: 1 GB (2 GB recommended)
- **Storage**: 10 GB SSD
- **OS**: Ubuntu 20.04/22.04 LTS
- **Network**: Stable internet connection

### Recommended VPS Providers
| Provider | Price | Location | Link |
|----------|-------|----------|------|
| **DigitalOcean** | $6/mo | Singapore | digitalocean.com |
| **Vultr** | $6/mo | Singapore | vultr.com |
| **Linode** | $5/mo | Singapore | linode.com |
| **Contabo** | €4/mo | Germany | contabo.com |

---

## 🔧 Step 1: VPS Setup

### 1.1 Connect to VPS via SSH
```bash
# Replace with your VPS IP and username
ssh root@your-vps-ip

# Or if using non-root user
ssh username@your-vps-ip
```

### 1.2 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 Create Non-Root User (Recommended)
```bash
# Create new user
sudo adduser automation

# Add to sudo group
sudo usermod -aG sudo automation

# Switch to new user
su - automation
```

---

## 📦 Step 2: Install Dependencies

### 2.1 Install Python & Essential Tools
```bash
sudo apt install -y python3 python3-pip python3-venv git curl wget unzip
```

### 2.2 Install Chrome & ChromeDriver (for Selenium)
```bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install -y

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE -O /tmp/chrome_version
DRIVER_VERSION=$(cat /tmp/chrome_version)
wget https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Verify installation
google-chrome --version
chromedriver --version
```

### 2.3 Verify Python Installation
```bash
python3 --version  # Should be 3.8+
pip3 --version
```

---

## 📥 Step 3: Clone Repository

### 3.1 Create Project Directory
```bash
mkdir -p ~/automation
cd ~/automation
```

### 3.2 Clone GitHub Repository
```bash
git clone https://github.com/oxshiexp/eldorado-automation.git
cd eldorado-automation
```

### 3.3 Setup Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3.4 Verify Installation
```bash
# Check installed packages
pip list | grep -E "(telegram|selenium|requests)"

# Should show:
# python-telegram-bot  20.7
# selenium             4.15.0
# requests             2.31.0
```

---

## 📱 Step 4: Setup Telegram Bot

### 4.1 Create Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Start conversation** with `/start`
3. **Create new bot** with `/newbot`
4. **Choose bot name** (e.g., "Eldorado Monitor")
5. **Choose username** (e.g., "eldorado_monitor_bot")
6. **Copy the Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Screenshot Example:**
```
@BotFather: Congratulations! Your bot is created.
Token: 7891234567:AAHxxx-yyyyyyyyyyyyyyyyyyyyyyyyy
Keep your token secure and store it safely!
```

### 4.2 Get Your Chat ID

1. **Search for** `@userinfobot` on Telegram
2. **Start conversation** with `/start`
3. **Copy your Chat ID** (looks like: `123456789` or `-123456789`)

**Alternative Method:**
```bash
# Send a message to your bot first, then:
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates

# Look for "chat":{"id":123456789}
```

### 4.3 Test Bot Connection
```bash
# Replace with your actual token and chat_id
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
  -d "chat_id=<YOUR_CHAT_ID>" \
  -d "text=Test from VPS! 🚀"
```

If successful, you'll receive the test message on Telegram! ✅

---

## ⚙️ Step 5: Configure Environment

### 5.1 Copy Environment Template
```bash
cd ~/automation/eldorado-automation
cp env.example.txt .env
```

### 5.2 Edit Configuration
```bash
nano .env
```

### 5.3 Configure Settings
```env
# Eldorado API Key
ELDORADO_API_KEY=your_actual_api_key_here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=7891234567:AAHxxx-yyyyyyyyyyyyyyyyyyyyyyyyy
TELEGRAM_CHAT_ID=123456789
ENABLE_TELEGRAM_NOTIFICATIONS=true

# Monitoring Settings
CHECK_INTERVAL_MINUTES=30
PRICE_ADJUSTMENT_FACTOR=0.95

# Target Sellers
TARGET_SELLERS=https://www.eldorado.gg/users/YourCompetitor?category=Currency
```

**Press `Ctrl+X`, then `Y`, then `Enter` to save.**

### 5.4 Secure .env File
```bash
chmod 600 .env
```

### 5.5 Test Telegram Notifier
```bash
# Activate virtual environment
source ~/automation/eldorado-automation/venv/bin/activate

# Test notifier
python3 telegram_notifier.py
```

**Expected Output:**
```
✅ Telegram notifier initialized successfully!
📱 Bot Token: 789123456...
💬 Chat ID: 123456789
🧪 Sending test notification...
✅ Test notification sent successfully!
```

You should receive a test message on Telegram! 🎉

---

## 🔄 Step 6: Setup Systemd Service (Auto-Start)

Systemd service ensures the bot runs 24/7 and auto-starts on reboot.

### 6.1 Create Log Directory
```bash
sudo mkdir -p /var/log/eldorado-automation
sudo chown $USER:$USER /var/log/eldorado-automation
```

### 6.2 Edit Service File
```bash
nano ~/automation/eldorado-automation/eldorado-automation.service
```

**Replace placeholders:**
- `your_username` → Your actual username (e.g., `automation`)
- `/home/your_username` → Your home directory path

**Example:**
```ini
[Unit]
Description=Eldorado Automation - 24/7 Price Monitoring Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=automation
Group=automation
WorkingDirectory=/home/automation/automation/eldorado-automation
Environment="PATH=/home/automation/automation/eldorado-automation/venv/bin"
ExecStart=/home/automation/automation/eldorado-automation/venv/bin/python hourly_monitor_execution.py

# Restart policy
Restart=always
RestartSec=60

# Logging
StandardOutput=append:/var/log/eldorado-automation/service.log
StandardError=append:/var/log/eldorado-automation/error.log

[Install]
WantedBy=multi-user.target
```

### 6.3 Install Service
```bash
# Copy service file to systemd directory
sudo cp ~/automation/eldorado-automation/eldorado-automation.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable eldorado-automation.service

# Verify service is enabled
sudo systemctl is-enabled eldorado-automation.service
# Should output: enabled
```

---

## ▶️ Step 7: Start and Monitor Service

### 7.1 Start Service
```bash
sudo systemctl start eldorado-automation.service
```

You should receive a Telegram notification: **"🚀 Eldorado Automation Started"**

### 7.2 Check Service Status
```bash
sudo systemctl status eldorado-automation.service
```

**Expected Output:**
```
● eldorado-automation.service - Eldorado Automation - 24/7 Price Monitoring
   Loaded: loaded (/etc/systemd/system/eldorado-automation.service; enabled)
   Active: active (running) since Wed 2024-01-15 10:00:00 UTC; 5s ago
   Main PID: 12345 (python)
```

**Status Indicators:**
- 🟢 `Active: active (running)` → Service is running
- 🔵 `Loaded: ... enabled` → Auto-start enabled
- 🟢 `Main PID: 12345` → Process ID

### 7.3 View Logs
```bash
# View service logs (last 50 lines)
sudo journalctl -u eldorado-automation.service -n 50

# Follow logs in real-time
sudo journalctl -u eldorado-automation.service -f

# View custom log files
tail -f /var/log/eldorado-automation/service.log
tail -f /var/log/eldorado-automation/error.log
```

### 7.4 Test Auto-Restart on Failure
```bash
# Kill process (service should auto-restart)
sudo pkill -f "hourly_monitor_execution.py"

# Check if restarted
sudo systemctl status eldorado-automation.service
# Should show "Active: active (running)" again
```

### 7.5 Test Auto-Start on Reboot
```bash
# Reboot VPS
sudo reboot

# After reboot, reconnect and check
ssh username@your-vps-ip
sudo systemctl status eldorado-automation.service
# Should be "Active: active (running)"
```

---

## 🔧 Troubleshooting

### Service Won't Start

**Check logs:**
```bash
sudo journalctl -u eldorado-automation.service -n 100 --no-pager
```

**Common Issues:**

1. **Python not found:**
   ```bash
   # Verify path in service file
   which python3
   # Update ExecStart path in service file
   ```

2. **Module not found:**
   ```bash
   # Activate venv and reinstall
   source ~/automation/eldorado-automation/venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Permission denied:**
   ```bash
   # Fix log directory permissions
   sudo chown -R $USER:$USER /var/log/eldorado-automation
   ```

4. **ChromeDriver issues:**
   ```bash
   # Check Chrome & ChromeDriver versions match
   google-chrome --version
   chromedriver --version
   
   # Reinstall if needed
   sudo apt remove google-chrome-stable
   # Then repeat Step 2.2
   ```

### Telegram Notifications Not Working

**Test bot manually:**
```bash
source ~/automation/eldorado-automation/venv/bin/activate
python3 telegram_notifier.py
```

**Check credentials:**
```bash
# View .env file
cat ~/automation/eldorado-automation/.env | grep TELEGRAM

# Verify bot token format: 123456789:ABCdef...
# Verify chat_id is numeric
```

**Test with curl:**
```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>" \
  -d "text=Manual test"
```

### High Memory Usage

**Check memory:**
```bash
free -h
top -o %MEM
```

**Add swap space:**
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 🛠️ Maintenance Commands

### Service Management
```bash
# Start service
sudo systemctl start eldorado-automation.service

# Stop service
sudo systemctl stop eldorado-automation.service

# Restart service
sudo systemctl restart eldorado-automation.service

# View status
sudo systemctl status eldorado-automation.service

# Enable auto-start
sudo systemctl enable eldorado-automation.service

# Disable auto-start
sudo systemctl disable eldorado-automation.service
```

### Update Code from GitHub
```bash
# Stop service
sudo systemctl stop eldorado-automation.service

# Pull latest changes
cd ~/automation/eldorado-automation
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl start eldorado-automation.service
```

### View Logs
```bash
# Systemd logs (last 100 lines)
sudo journalctl -u eldorado-automation.service -n 100

# Follow logs in real-time
sudo journalctl -u eldorado-automation.service -f

# Custom log files
tail -f /var/log/eldorado-automation/service.log
tail -f /var/log/eldorado-automation/error.log

# View errors only
grep ERROR /var/log/eldorado-automation/error.log
```

### Backup Configuration
```bash
# Backup .env file
cp ~/automation/eldorado-automation/.env ~/automation/.env.backup

# Backup service file
sudo cp /etc/systemd/system/eldorado-automation.service ~/automation/
```

### Monitor System Resources
```bash
# CPU & Memory usage
htop

# Disk space
df -h

# Process info
ps aux | grep python
```

### Clean Old Logs
```bash
# Delete logs older than 7 days
find /var/log/eldorado-automation -name "*.log" -mtime +7 -delete

# Rotate logs manually
sudo journalctl --vacuum-time=7d
```

---

## ✅ Deployment Checklist

After following all steps, verify:

- [ ] VPS is accessible via SSH
- [ ] Python 3.8+ installed
- [ ] Chrome & ChromeDriver installed and working
- [ ] Repository cloned to `~/automation/eldorado-automation`
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list` shows all packages)
- [ ] Telegram bot created and tested
- [ ] Chat ID obtained
- [ ] `.env` file configured with correct credentials
- [ ] Telegram test notification received successfully
- [ ] Systemd service file edited with correct paths
- [ ] Service installed to `/etc/systemd/system/`
- [ ] Service enabled for auto-start
- [ ] Service started successfully
- [ ] Service status shows "active (running)"
- [ ] Logs show no errors
- [ ] Telegram notification received on service start
- [ ] Auto-restart works (tested by killing process)
- [ ] Auto-start works (tested by rebooting VPS)

---

## 🎉 Success!

Your Eldorado Automation is now running 24/7 on VPS with:

✅ **Auto-start on boot** (systemd service)  
✅ **Auto-restart on failure** (60 second delay)  
✅ **Telegram notifications** (real-time alerts)  
✅ **Persistent logging** (service.log & error.log)  
✅ **Resource monitoring** (memory & CPU limits)

**You will receive Telegram notifications for:**
- 🚀 Service start/restart
- 🕷️ Scraping completion
- 📤 Upload results
- 📊 Price changes detected
- ❌ Errors and failures
- 🔍 Monitoring summaries

**Repository:** https://github.com/oxshiexp/eldorado-automation

---

## 📞 Support

Need help? Check the documentation:
- [README.md](README.md) - Overview and features
- [QUICKSTART.md](docs/QUICKSTART.md) - Quick start guide
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues
- [API.md](docs/API.md) - API reference

**Happy automating! 🚀**
