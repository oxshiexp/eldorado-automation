# Eldorado.gg Automation System

Sistem automasi lengkap untuk scraping, upload, dan monitoring produk di Eldorado.gg marketplace.

## 🎯 Fitur Utama

### 1. **Product Scraper** (`scraper.py`)
- Scrape semua produk dari seller profile
- Extract detail lengkap: harga, stock, server, faction, delivery time
- Support pagination otomatis
- Export ke JSON dan CSV
- Rate limiting untuk menghindari ban

### 2. **Auto Uploader** (`uploader.py`)
- Upload produk ke Eldorado menggunakan Seller API
- Bulk upload dengan batch processing
- Update produk yang sudah ada
- Delete produk
- Template CSV untuk bulk upload

### 3. **Price Monitor** (`monitor.py`)
- Monitor perubahan harga secara real-time
- Deteksi produk baru dan yang dihapus
- Track perubahan stock dan description
- Notifikasi via email
- History tracking (50 snapshots terakhir)

### 4. **Complete Automation** (`automation.py`)
- Scrape dan upload dalam satu command
- Auto-adjust harga (lebih murah dari competitor)
- Sync produk dengan competitor
- Scheduled monitoring
- Operation logging

## 📦 Instalasi

### Requirements
```bash
pip install requests beautifulsoup4
```

### Setup
1. Clone atau download folder ini
2. Daftar sebagai seller di [Eldorado.gg](https://www.eldorado.gg/become-seller)
3. Dapatkan API key dari seller dashboard
4. Set environment variables:
```bash
export ELDORADO_API_KEY='your_api_key_here'
export ELDORADO_SELLER_ID='your_seller_id_here'
```

## 🚀 Cara Penggunaan

### 1. Scrape Produk Seller

```bash
# Scrape semua produk dari seller
python scraper.py

# Atau langsung dengan URL
python automation.py scrape --seller-url "https://www.eldorado.gg/users/Alayon?category=Currency"
```

Output: `scraped_products.json` dan `scraped_products.csv`

### 2. Upload Produk

```bash
# Upload dari file JSON
python automation.py upload --file scraped_products.json --api-key YOUR_API_KEY

# Generate template CSV terlebih dahulu
python uploader.py  # Akan generate bulk_upload_template.csv
```

### 3. Scrape + Upload Otomatis

```bash
# Scrape dari competitor dan upload ke akun Anda (5% lebih murah)
python automation.py scrape-upload \
  --seller-url "https://www.eldorado.gg/users/Alayon?category=Currency" \
  --price-adjustment 0.95 \
  --api-key YOUR_API_KEY
```

**Penjelasan:**
- `--price-adjustment 0.95` = harga Anda 5% lebih murah dari competitor
- `--price-adjustment 0.90` = harga Anda 10% lebih murah
- `--price-adjustment 1.00` = harga sama dengan competitor

### 4. Monitor Perubahan Harga

```bash
# Monitor seller setiap 60 menit
python automation.py monitor \
  --seller-url "https://www.eldorado.gg/users/Alayon?category=Currency" \
  --interval 60 \
  --email your@email.com

# Atau langsung dengan monitor.py
python monitor.py "https://www.eldorado.gg/users/Alayon?category=Currency" 30
```

Monitor akan:
- ✅ Deteksi perubahan harga
- ✅ Deteksi produk baru
- ✅ Deteksi produk yang dihapus
- ✅ Track perubahan stock
- ✅ Kirim notifikasi via email

### 5. Sync Produk

```bash
# Sync produk Anda dengan competitor
python automation.py sync \
  --seller-url "https://www.eldorado.gg/users/Alayon?category=Currency" \
  --api-key YOUR_API_KEY
```

Sync akan:
1. Scrape produk competitor
2. Compare dengan produk Anda
3. Update harga yang berubah (otomatis 5% lebih murah)
4. Upload produk baru yang belum ada

## 🤖 Setup Automation dengan Nebula Triggers

### Scheduled Scraping (Setiap 6 jam)

```bash
# Akan di-setup via Nebula trigger system
# Cron: 0 */6 * * * (setiap 6 jam)
```

### Price Monitoring (Setiap 1 jam)

```bash
# Cron: 0 * * * * (setiap jam)
```

### Daily Sync (Setiap hari jam 00:00)

```bash
# Cron: 0 0 * * * (midnight setiap hari)
```

## 📊 Output Files

| File | Deskripsi |
|------|-----------|
| `scraped_products.json` | Hasil scraping dalam format JSON |
| `scraped_products.csv` | Hasil scraping dalam format CSV |
| `price_history.json` | History monitoring (50 snapshots terakhir) |
| `detected_changes.json` | Log perubahan yang terdeteksi |
| `automation_log.json` | Log operasi automation |
| `automation_config.json` | Config monitoring |

## 🔧 Konfigurasi Lanjutan

### Custom Scraping Logic

Edit `scraper.py` untuk customize extraction logic:

```python
def _extract_product_details(self, element, seller_info):
    # Add custom extraction logic here
    pass
```

### Custom Price Adjustment

Edit `automation.py`:

```python
# Contoh: harga dinamis berdasarkan rating seller
if seller_info['rating'] > 99.5:
    price_adjustment = 0.93  # 7% lebih murah untuk top seller
else:
    price_adjustment = 0.95  # 5% lebih murah untuk seller biasa
```

## ⚠️ Penting: API Setup

Eldorado.gg menyediakan **Seller API** untuk automation. Untuk menggunakannya:

1. **Daftar sebagai seller** di https://www.eldorado.gg/become-seller
2. **Verify akun** Anda (biasanya beberapa menit)
3. **Akses Seller Dashboard** dan cari menu "API" atau "Developer"
4. **Generate API Key**
5. **Copy API key** dan simpan sebagai environment variable

```bash
# Linux/Mac
export ELDORADO_API_KEY='your_api_key_here'
export ELDORADO_SELLER_ID='your_seller_id_here'

# Windows
set ELDORADO_API_KEY=your_api_key_here
set ELDORADO_SELLER_ID=your_seller_id_here
```

**Note:** Jika Eldorado belum menyediakan public API documentation, Anda perlu:
- Contact support untuk API access
- Request API documentation
- Adjust endpoint URLs di `uploader.py`

## 🔐 Security Best Practices

1. **Never commit API keys** ke Git
2. **Use environment variables** untuk credentials
3. **Rate limit** scraping (sudah built-in)
4. **Respect robots.txt** dan terms of service
5. **Monitor API usage** untuk avoid limits

## 📈 Workflow Rekomendasi

### Daily Automation:
1. **00:00** - Full sync dengan competitor (scrape + update semua produk)
2. **Setiap 1 jam** - Monitor perubahan harga
3. **Setiap 6 jam** - Scrape produk baru

### Manual Tasks:
- Review detected changes
- Adjust pricing strategy
- Add/remove products manually
- Check automation logs

## 🐛 Troubleshooting

### Scraping Issues
```bash
# Jika scraping gagal, cek:
1. URL seller benar
2. Koneksi internet stabil
3. Website tidak down
4. Rate limiting (tunggu beberapa menit)
```

### Upload Issues
```bash
# Jika upload gagal:
1. Cek API key valid
2. Cek format data sesuai schema
3. Cek quota/limits API
4. Review error message di console
```

### Monitoring Issues
```bash
# Jika monitoring tidak jalan:
1. Cek interval tidak terlalu pendek
2. Cek disk space untuk history files
3. Review automation_log.json untuk errors
```

## 📞 Support

Untuk pertanyaan atau issue:
1. Check automation_log.json untuk error details
2. Review detected_changes.json untuk change history
3. Contact Eldorado support untuk API issues

## 📝 License

This automation system is for personal/educational use. Please comply with Eldorado.gg Terms of Service.

## 🎓 Tips & Tricks

### Optimal Pricing Strategy
- Start dengan 5% lebih murah (0.95)
- Monitor conversion rate
- Adjust berdasarkan demand
- Jangan terlalu murah (profit margin!)

### Best Monitoring Interval
- High competition products: 30-60 menit
- Low competition: 2-4 jam
- Niche products: 6-12 jam

### Scaling Up
- Monitor multiple sellers sekaligus
- Use different price adjustments per game
- Setup alerts untuk price drops > 10%
- Auto-pause listings jika competitor habis stock

## 🔄 Updates & Maintenance

Check for updates:
- Review Eldorado.gg Seller Rules regularly
- Update scraping selectors if website changes
- Adjust API endpoints if documentation updates
- Monitor for new features (Bulk Upload tools, etc)

---

**Last Updated:** January 2026
**Version:** 1.0.0
