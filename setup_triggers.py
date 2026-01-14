"""
Setup Nebula Triggers untuk Eldorado Automation
Script ini membantu setup automated triggers untuk scraping dan monitoring
"""

import os
import sys

# Configuration
SELLER_URL = "https://www.eldorado.gg/users/Alayon?category=Currency"  # Ganti dengan seller target
NOTIFICATION_EMAIL = "your@email.com"  # Ganti dengan email Anda
API_KEY = os.getenv('ELDORADO_API_KEY', 'your_api_key_here')

def print_trigger_instructions():
    """Print instruksi untuk setup triggers di Nebula"""
    
    print("\n" + "="*70)
    print("🤖 ELDORADO AUTOMATION - TRIGGER SETUP INSTRUCTIONS")
    print("="*70)
    
    print("\n📋 OVERVIEW:")
    print("   Anda akan setup 3 automated triggers:")
    print("   1. Daily Product Sync (00:00 setiap hari)")
    print("   2. Hourly Price Monitor (setiap jam)")
    print("   3. 6-Hour Product Scrape (setiap 6 jam)")
    
    print("\n" + "="*70)
    print("🔧 TRIGGER 1: DAILY PRODUCT SYNC")
    print("="*70)
    print("Name: Eldorado Daily Sync")
    print("Description: Sync produk dengan competitor setiap hari")
    print("Schedule (Cron): 0 0 * * *")
    print("Command to run:")
    print(f"   python automation.py sync \\")
    print(f"     --seller-url '{SELLER_URL}' \\")
    print(f"     --api-key '{API_KEY}' \\")
    print(f"     --email '{NOTIFICATION_EMAIL}'")
    
    print("\n" + "="*70)
    print("🔧 TRIGGER 2: HOURLY PRICE MONITORING")
    print("="*70)
    print("Name: Eldorado Price Monitor")
    print("Description: Monitor perubahan harga setiap jam")
    print("Schedule (Cron): 0 * * * *")
    print("Command to run:")
    print(f"   python monitor.py '{SELLER_URL}' 60")
    
    print("\n" + "="*70)
    print("🔧 TRIGGER 3: 6-HOUR PRODUCT SCRAPE")
    print("="*70)
    print("Name: Eldorado Product Scraper")
    print("Description: Scrape produk setiap 6 jam")
    print("Schedule (Cron): 0 */6 * * *")
    print("Command to run:")
    print(f"   python automation.py scrape \\")
    print(f"     --seller-url '{SELLER_URL}' \\")
    print(f"     --email '{NOTIFICATION_EMAIL}'")
    
    print("\n" + "="*70)
    print("📅 CRON SCHEDULE EXPLANATION")
    print("="*70)
    print("Format: minute hour day month day_of_week")
    print("")
    print("0 0 * * *     = Daily at midnight (00:00)")
    print("0 * * * *     = Every hour at minute 0")
    print("0 */6 * * *   = Every 6 hours (00:00, 06:00, 12:00, 18:00)")
    print("*/30 * * * *  = Every 30 minutes")
    print("0 9 * * 1     = Every Monday at 9:00 AM")
    
    print("\n" + "="*70)
    print("⚙️ ENVIRONMENT VARIABLES SETUP")
    print("="*70)
    print("Sebelum menjalankan automation, set environment variables:")
    print("")
    print("# Linux/Mac:")
    print(f"export ELDORADO_API_KEY='{API_KEY}'")
    print(f"export ELDORADO_SELLER_ID='your_seller_id'")
    print("")
    print("# Windows:")
    print(f"set ELDORADO_API_KEY={API_KEY}")
    print(f"set ELDORADO_SELLER_ID=your_seller_id")
    
    print("\n" + "="*70)
    print("📧 EMAIL NOTIFICATIONS")
    print("="*70)
    print("Email notifikasi akan dikirim untuk:")
    print("✅ Perubahan harga > 5%")
    print("✅ Produk baru dari competitor")
    print("✅ Produk yang dihapus competitor")
    print("✅ Daily sync summary")
    print("✅ Error atau failed operations")
    
    print("\n" + "="*70)
    print("🚀 NEXT STEPS")
    print("="*70)
    print("1. Update SELLER_URL, NOTIFICATION_EMAIL, dan API_KEY di file ini")
    print("2. Run: python setup_triggers.py")
    print("3. Gunakan Nebula untuk create triggers dengan config di atas")
    print("4. Test manual dulu sebelum enable automation:")
    print(f"   python automation.py scrape --seller-url '{SELLER_URL}'")
    print("5. Enable triggers dan monitor automation_log.json")
    
    print("\n" + "="*70)
    print("✨ AUTOMATION IS READY!")
    print("="*70 + "\n")


def generate_trigger_configs():
    """Generate trigger configuration files"""
    
    triggers = [
        {
            "name": "Eldorado Daily Sync",
            "description": "Sync produk dengan competitor setiap hari midnight",
            "cron": "0 0 * * *",
            "command": f"python automation.py sync --seller-url '{SELLER_URL}' --api-key '{API_KEY}' --email '{NOTIFICATION_EMAIL}'",
            "enabled": True
        },
        {
            "name": "Eldorado Price Monitor",
            "description": "Monitor perubahan harga setiap jam",
            "cron": "0 * * * *",
            "command": f"python monitor.py '{SELLER_URL}' 60",
            "enabled": True
        },
        {
            "name": "Eldorado Product Scraper",
            "description": "Scrape produk baru setiap 6 jam",
            "cron": "0 */6 * * *",
            "command": f"python automation.py scrape --seller-url '{SELLER_URL}' --email '{NOTIFICATION_EMAIL}'",
            "enabled": True
        }
    ]
    
    import json
    with open('trigger_configs.json', 'w', encoding='utf-8') as f:
        json.dump(triggers, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Trigger configs saved to: trigger_configs.json")
    print("   Use this file as reference when creating Nebula triggers\n")


def test_automation():
    """Test automation scripts before enabling triggers"""
    
    print("\n" + "="*70)
    print("🧪 TESTING AUTOMATION SCRIPTS")
    print("="*70)
    
    print("\n1. Testing scraper...")
    print(f"   Command: python automation.py scrape --seller-url '{SELLER_URL}'")
    print("   Expected: scraped_products.json and .csv files created")
    
    print("\n2. Testing uploader (requires API key)...")
    print(f"   Command: python uploader.py")
    print("   Expected: bulk_upload_template.csv created")
    
    print("\n3. Testing monitor...")
    print(f"   Command: python monitor.py '{SELLER_URL}' 1")
    print("   Expected: Initial snapshot saved, monitoring started")
    
    print("\n💡 TIP: Run each test manually to verify everything works")
    print("   before enabling automated triggers")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Check if config variables are updated
    if SELLER_URL == "https://www.eldorado.gg/users/Alayon?category=Currency":
        print("\n⚠️ WARNING: Using default SELLER_URL!")
        print("   Please update SELLER_URL, NOTIFICATION_EMAIL, and API_KEY")
        print("   in setup_triggers.py before proceeding.\n")
    
    # Print instructions
    print_trigger_instructions()
    
    # Generate config files
    generate_trigger_configs()
    
    # Test instructions
    test_automation()
    
    print("\n📚 For more information, see README.md\n")
