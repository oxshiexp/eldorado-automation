# 🚀 Quick Start Guide - Eldorado Automation

Panduan cepat untuk mulai menggunakan Eldorado automation system.

## ⚡ 5 Menit Setup

### Step 1: Install Dependencies
```bash
pip install requests beautifulsoup4
```

### Step 2: Test Scraping
```bash
# Test scrape seller (no API key needed)
python automation.py scrape --seller-url "https://www.eldorado.gg/users/Alayon?category=Currency"
```

Output: `scraped_products.json` dan `scraped_products.csv`

### Step 3: Get Eldorado API Key
1. Daftar di https://www.eldorado.gg/become-seller
2. Verify akun (beberapa menit)
3. Go to Seller Dashboard → API/Developer section
4. Generate API Key
5. Copy dan simpan

### Step 4: Set Environment Variables
```bash
# Linux/Mac
export ELDORADO_API_KEY='your_api_key_here'

# Windows
set ELDORADO_API_KEY=your_api_key_here
```

### Step 5: Test Upload
```bash
# Generate template
python uploader.py

# Edit bulk_upload_template.csv with your products

# Upload (akan error jika API key belum valid)
python automation.py upload --file bulk_upload_template.csv --api-key YOUR_API_KEY
```

## 🎯 Use Cases

### Use Case 1: Copy Competitor Pricing
```bash
# Scrape competitor dan upload ke akun Anda (5% lebih murah)
python automation.py scrape-upload \
  --seller-url "https://www.eldorado.gg/users/COMPETITOR_NAME?category=Currency" \
  --price-adjustment 0.95 \
  --api-key YOUR_API_KEY \
  --email your@email.com
```

**Result:** Semua produk competitor di-copy dengan harga 5% lebih murah.

### Use Case 2: Monitor Price Changes
```bash
# Monitor competitor setiap 30 menit
python monitor.py "https://www.eldorado.gg/users/COMPETITOR_NAME?category=Currency" 30
```

**Result:** Notifikasi setiap ada perubahan harga, produk baru, atau produk dihapus.

### Use Case 3: Daily Auto Sync
```bash
# Sync produk setiap hari
python automation.py sync \
  --seller-url "https://www.eldorado.gg/users/COMPETITOR_NAME?category=Currency" \
  --api-key YOUR_API_KEY
```

**Result:** Update harga otomatis + upload produk baru.

## 🤖 Setup Automation (dengan Nebula)

### Option A: Manual Setup
1. Edit `setup_triggers.py`:
   - Update `SELLER_URL`
   - Update `NOTIFICATION_EMAIL`
   - Update `API_KEY`

2. Run setup:
```bash
python setup_triggers.py
```

3. Create Nebula triggers menggunakan config yang dihasilkan

### Option B: Quick Commands

**Daily Sync (00:00 setiap hari):**
```bash
python automation.py sync --seller-url "SELLER_URL" --api-key YOUR_KEY
```
Cron: `0 0 * * *`

**Hourly Monitor:**
```bash
python monitor.py "SELLER_URL" 60
```
Cron: `0 * * * *`

**6-Hour Scrape:**
```bash
python automation.py scrape --seller-url "SELLER_URL" --email your@email.com
```
Cron: `0 */6 * * *`

## 📊 Expected Results

### After First Scrape:
- ✅ `scraped_products.json` (detailed product data)
- ✅ `scraped_products.csv` (spreadsheet format)
- ✅ Console output dengan summary

### After Upload:
- ✅ Products listed di Eldorado seller dashboard
- ✅ `automation_log.json` (operation history)
- ✅ Email notification (jika configured)

### After Monitoring (1 hour):
- ✅ `price_history.json` (2 snapshots)
- ✅ `detected_changes.json` (if any changes)
- ✅ Console output dengan change summary

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `automation_config.json` | Monitoring configuration |
| `trigger_configs.json` | Trigger schedules |
| `automation_log.json` | Operation history |
| `price_history.json` | Price snapshots |
| `detected_changes.json` | Change events |

## 🐛 Common Issues

### Issue 1: "No products found"
**Cause:** Incorrect seller URL atau website structure changed
**Fix:** 
- Verify URL di browser
- Check apakah seller memiliki produk
- Update scraping selectors di `scraper.py`

### Issue 2: "API key not configured"
**Cause:** Environment variable tidak di-set
**Fix:**
```bash
export ELDORADO_API_KEY='your_actual_key'
```

### Issue 3: "Upload failed"
**Cause:** API endpoint atau schema incorrect
**Fix:**
- Verify API key valid
- Check Eldorado API documentation
- Contact Eldorado support untuk API access

## 📞 Getting Help

1. Check `automation_log.json` untuk error details
2. Review console output untuk warnings
3. Test each component individually:
   - Scraper: ✅
   - Uploader: (needs API key)
   - Monitor: ✅

## 🎓 Next Steps

1. ✅ Test scraping beberapa sellers
2. ✅ Review scraped data quality
3. ⏳ Get valid API key from Eldorado
4. ⏳ Test upload dengan 1-2 products
5. ⏳ Setup monitoring untuk 1 competitor
6. ⏳ Enable automation triggers
7. ⏳ Monitor results daily

## 💡 Pro Tips

### Tip 1: Start Small
Test dengan 1 seller dan few products sebelum scale up.

### Tip 2: Monitor First
Setup monitoring dulu untuk understand price patterns sebelum auto-upload.

### Tip 3: Smart Pricing
- High demand products: 3-5% cheaper
- Low competition: 2-3% cheaper
- Niche products: sama atau 1% cheaper

### Tip 4: Scheduled Optimization
- Scrape saat traffic rendah (midnight-6am)
- Monitor saat peak hours (untuk react cepat)
- Sync sebelum prime time (evening)

---

**Time to first automation:** ~10 minutes
**Time to full setup:** ~30 minutes (including API key)

Happy automating! 🚀
