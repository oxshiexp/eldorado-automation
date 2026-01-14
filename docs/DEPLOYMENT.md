# 🚀 Deployment Guide - Eldorado Automation System

## ✅ System Selesai Dibuat!

Sistem automation lengkap untuk Eldorado.gg telah selesai dengan komponen berikut:

### 📦 Files Created

1. **scraper.py** - Web scraper untuk extract produk dari seller
2. **uploader.py** - Auto uploader menggunakan Eldorado Seller API
3. **monitor.py** - Price monitoring system dengan change detection
4. **automation.py** - Orchestrator untuk scrape+upload+sync
5. **setup_triggers.py** - Helper untuk setup automation triggers
6. **README.md** - Complete documentation
7. **QUICKSTART.md** - Quick start guide
8. **DEPLOYMENT.md** - This file

### 🤖 Triggers Created (Nebula)

✅ **Daily Product Sync** - Cron: `0 0 * * *` (Midnight setiap hari)
✅ **Hourly Price Monitor** - Cron: `0 * * * *` (Setiap jam)
✅ **6-Hour Product Scrape** - Cron: `0 */6 * * *` (Setiap 6 jam)

## 📋 Pre-Deployment Checklist

### 1. Environment Setup
```bash
# Set API credentials
export ELDORADO_API_KEY='your_api_key_from_seller_dashboard'
export ELDORADO_SELLER_ID='your_seller_id'

# Verify
echo $ELDORADO_API_KEY
```

### 2. Dependencies Check
```bash
pip install requests beautifulsoup4
python --version  # Should be Python 3.7+
```

### 3. Test Components Individually

**Test Scraper:**
```bash
python scraper.py
# Expected: Scrapes and saves products.json and products.csv
```

**Test Uploader:**
```bash
python uploader.py
# Expected: Generates bulk_upload_template.csv
```

**Test Monitor:**
```bash
python monitor.py "https://www.eldorado.gg/users/Alayon?category=Currency" 1
# Expected: Takes initial snapshot, waits 1 minute, checks again
# Press Ctrl+C to stop after verifying it works
```

**Test Full Automation:**
```bash
python automation.py scrape --seller-url "https://www.eldorado.gg/users/Alayon?category=Currency"
# Expected: Scrapes and saves scraped_products.json
```

### 4. Configure Target Sellers

Edit `setup_triggers.py` dan update:
```python
SELLER_URL = "https://www.eldorado.gg/users/YOUR_COMPETITOR_NAME?category=Currency"
NOTIFICATION_EMAIL = "your@email.com"
```

## 🎯 Deployment Workflows

### Workflow 1: Manual Scrape & Review
```bash
# Scrape competitor
python automation.py scrape --seller-url "COMPETITOR_URL"

# Review scraped_products.csv
# Edit/filter produk yang mau di-upload

# Upload manually
python automation.py upload --file scraped_products.json --api-key YOUR_KEY
```

### Workflow 2: Automated Scrape + Upload
```bash
# One command: scrape + adjust price + upload
python automation.py scrape-upload \
  --seller-url "COMPETITOR_URL" \
  --price-adjustment 0.95 \
  --api-key YOUR_KEY \
  --email your@email.com
```

### Workflow 3: Continuous Monitoring
```bash
# Start monitoring (runs until stopped)
python monitor.py "COMPETITOR_URL" 60

# Or use Nebula trigger for automated monitoring
# Trigger: "Eldorado Hourly Price Monitor"
```

### Workflow 4: Daily Sync (Recommended)
```bash
# Enable Nebula trigger: "Eldorado Daily Product Sync"
# Runs at midnight daily
# Automatically syncs prices and adds new products
```

## 📊 Expected Automation Flow

### Daily (00:00):
1. ✅ Scrape all competitor products
2. ✅ Compare with your current listings
3. ✅ Update prices (5% cheaper automatically)
4. ✅ Upload new products
5. ✅ Email summary report

### Hourly:
1. ✅ Quick price check
2. ✅ Detect changes
3. ✅ Alert if significant changes (>5%)

### Every 6 Hours:
1. ✅ Full product scrape
2. ✅ Discover new products
3. ✅ Update product database

## 🔍 Monitoring & Maintenance

### Check Automation Health

```bash
# View recent operations
cat automation_log.json | tail -20

# View detected changes
cat detected_changes.json | tail -10

# View price history
cat price_history.json | tail -5
```

### Email Notifications

You'll receive emails for:
- ✉️ Price drops >5% from competitor
- ✉️ New products added by competitor
- ✉️ Products removed by competitor
- ✉️ Daily sync summary
- ✉️ Upload errors or failures

### Performance Metrics

Track these metrics weekly:
- Number of products scraped
- Upload success rate
- Price changes detected
- Competitor activity patterns

## 🛠️ Troubleshooting

### Issue: Scraping Returns No Products
**Debug:**
```bash
# Test URL in browser first
# Check if selector patterns changed
# Update scraper.py selectors if needed
```

### Issue: Upload Fails
**Debug:**
```bash
# Verify API key
echo $ELDORADO_API_KEY

# Check API endpoint in uploader.py
# Contact Eldorado support for API docs
```

### Issue: Monitor Not Detecting Changes
**Debug:**
```bash
# Check price_history.json
# Verify snapshots are being saved
# Review comparison logic in monitor.py
```

### Issue: Triggers Not Running
**Debug:**
```bash
# Check Nebula trigger status
# Verify cron expressions
# Check automation_log.json for errors
```

## 🔐 Security Best Practices

1. **Never commit API keys** to Git
2. **Use environment variables** only
3. **Rotate API keys** every 90 days
4. **Monitor API usage** for unusual activity
5. **Backup automation_log.json** weekly
6. **Review email alerts** daily

## 📈 Scaling Up

### Multiple Competitors

Create separate triggers for each competitor:
```bash
# Competitor 1
python automation.py scrape-upload --seller-url "COMPETITOR_1_URL" ...

# Competitor 2
python automation.py scrape-upload --seller-url "COMPETITOR_2_URL" ...
```

### Multiple Games/Categories

Modify automation.py to handle different categories:
```python
TARGETS = [
    "https://www.eldorado.gg/users/Seller1?category=Currency",
    "https://www.eldorado.gg/users/Seller2?category=Accounts",
    "https://www.eldorado.gg/users/Seller3?category=Items"
]
```

### Advanced Pricing Strategy

Edit automation.py for dynamic pricing:
```python
# Different adjustments per game
if game == "World of Warcraft":
    price_adjustment = 0.93  # 7% cheaper
elif game == "OSRS":
    price_adjustment = 0.95  # 5% cheaper
else:
    price_adjustment = 0.97  # 3% cheaper
```

## 📞 Support & Updates

### Getting Help
1. Check automation_log.json for detailed errors
2. Review README.md for full documentation
3. See QUICKSTART.md for common use cases

### System Updates
- Review Eldorado seller rules monthly
- Update scraping selectors if website changes
- Check for new API features from Eldorado
- Update Python dependencies regularly

### Maintenance Schedule
- **Daily**: Review email alerts
- **Weekly**: Check automation logs
- **Monthly**: Update pricing strategy
- **Quarterly**: Rotate API keys

## ✨ Success Metrics

After 1 week of automation:
- [ ] 100+ products auto-uploaded
- [ ] Price changes detected daily
- [ ] Email notifications working
- [ ] Zero manual intervention needed

After 1 month:
- [ ] Competitive pricing maintained
- [ ] New products discovered automatically
- [ ] Revenue increase from better pricing
- [ ] Time saved: ~10 hours/week

## 🎉 System is Production Ready!

Your Eldorado automation system is complete and ready to deploy!

**Final Steps:**
1. ✅ Update configuration in setup_triggers.py
2. ✅ Set environment variables
3. ✅ Test each component
4. ✅ Enable Nebula triggers
5. ✅ Monitor for 24 hours
6. ✅ Adjust pricing strategy as needed

**Good luck with your automation! 🚀**

---

**System Version:** 1.0.0
**Last Updated:** January 2026
**Status:** ✅ Production Ready
