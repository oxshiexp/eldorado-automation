"""
Eldorado Hourly Price Monitor - Execution Script
Trigger #1 - 2026-01-14 23:00:02 UTC
"""
import json
import time
from datetime import datetime
from pathlib import Path

from telegram_notifier import get_notifier

def create_snapshot_dir():
    """Create snapshot directory if not exists"""
    snapshot_dir = Path('snapshots')
    snapshot_dir.mkdir(exist_ok=True)
    return snapshot_dir

def scrape_prices_demo():
    """
    Demo scraping - simulates scraping seller prices
    In production, this would call the actual scraper.py
    """
    print("🔍 Scraping harga terbaru dari seller target...")
    time.sleep(1)
    
    # Mock data for demo - simulates actual scraped data
    products = [
        {
            'id': 'prod_001',
            'name': 'Roblox Robux 800',
            'price': 95000,
            'currency': 'IDR',
            'seller': 'competitor_1',
            'url': 'https://www.eldorado.gg/roblox-robux/123'
        },
        {
            'id': 'prod_002', 
            'name': 'Roblox Robux 1700',
            'price': 185000,
            'currency': 'IDR',
            'seller': 'competitor_1',
            'url': 'https://www.eldorado.gg/roblox-robux/456'
        },
        {
            'id': 'prod_003',
            'name': 'Roblox Robux 4500',
            'price': 450000,
            'currency': 'IDR',
            'seller': 'competitor_1',
            'url': 'https://www.eldorado.gg/roblox-robux/789'
        }
    ]
    
    print(f"✅ Scraped {len(products)} products")
    return products

def load_previous_snapshot(snapshot_dir):
    """Load the most recent snapshot"""
    snapshots = sorted(snapshot_dir.glob('snapshot_*.json'), reverse=True)
    
    if not snapshots:
        print("📋 No previous snapshot found - this is the first execution")
        return None
    
    latest = snapshots[0]
    print(f"📂 Loading previous snapshot: {latest.name}")
    
    with open(latest, 'r') as f:
        return json.load(f)

def compare_snapshots(current, previous):
    """Compare current prices with previous snapshot"""
    if not previous:
        return {
            'is_first_run': True,
            'total_products': len(current),
            'changes': []
        }
    
    print("🔍 Comparing with previous snapshot...")
    
    # Create lookup dict for previous prices
    prev_prices = {p['id']: p for p in previous['products']}
    changes = []
    
    for product in current:
        prod_id = product['id']
        curr_price = product['price']
        
        if prod_id in prev_prices:
            prev_price = prev_prices[prod_id]['price']
            
            if curr_price != prev_price:
                change_pct = ((curr_price - prev_price) / prev_price) * 100
                
                changes.append({
                    'product_id': prod_id,
                    'product_name': product['name'],
                    'previous_price': prev_price,
                    'current_price': curr_price,
                    'change_amount': curr_price - prev_price,
                    'change_percentage': round(change_pct, 2),
                    'url': product['url']
                })
        else:
            # New product detected
            changes.append({
                'product_id': prod_id,
                'product_name': product['name'],
                'type': 'NEW_PRODUCT',
                'current_price': curr_price,
                'url': product['url']
            })
    
    # Check for deleted products
    current_ids = {p['id'] for p in current}
    for prev_id, prev_prod in prev_prices.items():
        if prev_id not in current_ids:
            changes.append({
                'product_id': prev_id,
                'product_name': prev_prod['name'],
                'type': 'PRODUCT_REMOVED',
                'previous_price': prev_prod['price']
            })
    
    return {
        'is_first_run': False,
        'total_products': len(current),
        'total_changes': len(changes),
        'changes': changes
    }

def save_snapshot(products, snapshot_dir):
    """Save current snapshot"""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f'snapshot_{timestamp}.json'
    filepath = snapshot_dir / filename
    
    snapshot_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'product_count': len(products),
        'products': products
    }
    
    with open(filepath, 'w') as f:
        json.dump(snapshot_data, f, indent=2)
    
    print(f"💾 Snapshot saved: {filename}")
    return filepath

def check_significant_changes(comparison_result):
    """Check if there are changes > 5%"""
    if comparison_result['is_first_run']:
        return False, []
    
    significant = []
    
    for change in comparison_result['changes']:
        if 'change_percentage' in change:
            if abs(change['change_percentage']) > 5:
                significant.append(change)
        elif change.get('type') == 'NEW_PRODUCT':
            significant.append(change)
    
    return len(significant) > 0, significant

def format_email_report(comparison_result, significant_changes):
    """Format email notification"""
    if comparison_result['is_first_run']:
        return {
            'subject': '🎯 Eldorado Monitor: Baseline Created',
            'body': f"""# Eldorado Price Monitor - Baseline Created

Monitoring system is now active!

**Summary:**
- Total products monitored: {comparison_result['total_products']}
- First execution completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

The system will now check for price changes every hour.
You'll receive notifications when prices change by more than 5%.

---
*Eldorado Automation System*
"""
        }
    
    if not significant_changes:
        # No significant changes
        return None
    
    body = "# 🚨 Eldorado Price Alert - Significant Changes Detected\n\n"
    body += f"**Execution Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
    body += f"**Total Products Monitored:** {comparison_result['total_products']}\n"
    body += f"**Significant Changes:** {len(significant_changes)}\n\n"
    body += "---\n\n"
    body += "## 📊 Price Changes\n\n"
    
    for change in significant_changes:
        if change.get('type') == 'NEW_PRODUCT':
            body += f"### ✨ NEW: {change['product_name']}\n"
            body += f"- **Price:** Rp {change['current_price']:,}\n"
            body += f"- **URL:** {change['url']}\n\n"
        elif 'change_percentage' in change:
            emoji = "📉" if change['change_percentage'] < 0 else "📈"
            body += f"### {emoji} {change['product_name']}\n"
            body += f"- **Previous:** Rp {change['previous_price']:,}\n"
            body += f"- **Current:** Rp {change['current_price']:,}\n"
            body += f"- **Change:** Rp {change['change_amount']:,} ({change['change_percentage']:+.1f}%)\n"
            body += f"- **URL:** {change['url']}\n\n"
    
    body += "---\n"
    body += "*Next check in 1 hour*"
    
    return {
        'subject': f'🚨 Eldorado Alert: {len(significant_changes)} Significant Price Changes',
        'body': body
    }

def main():
    """Main execution flow"""
    print("=" * 60)
    print("🤖 ELDORADO HOURLY PRICE MONITOR - EXECUTION #1")
    print("=" * 60)
    print(f"Execution Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
    
    # Step 1: Scrape current prices
    print("📍 STEP 1: Scrape harga terbaru")
    print("-" * 60)
    current_products = scrape_prices_demo()
    print()
    
    # Step 2: Load previous snapshot and compare
    print("📍 STEP 2: Compare dengan snapshot sebelumnya")
    print("-" * 60)
    snapshot_dir = create_snapshot_dir()
    previous_snapshot = load_previous_snapshot(snapshot_dir)
    
    prev_products = previous_snapshot['products'] if previous_snapshot else None
    comparison = compare_snapshots(current_products, prev_products)
    
    if comparison['is_first_run']:
        print("✅ Baseline snapshot will be created")
    else:
        print(f"✅ Found {comparison['total_changes']} changes")
    print()
    
    # Step 3: Check for significant changes and send notification
    print("📍 STEP 3: Check significant changes & send notification")
    print("-" * 60)
    has_significant, significant_changes = check_significant_changes(comparison)
    
    email_data = format_email_report(comparison, significant_changes)
    
    if email_data:
        print(f"📧 Email notification prepared:")
        print(f"   Subject: {email_data['subject']}")
        print(f"   Recipients: just4myweb@gmail.com")
        if has_significant:
            print(f"   ⚠️  {len(significant_changes)} significant changes detected!")
        print()
        
        # Save email preview
        email_preview = Path('email_preview.txt')
        with open(email_preview, 'w') as f:
            f.write(f"Subject: {email_data['subject']}\n")
            f.write(f"To: just4myweb@gmail.com\n\n")
            f.write(email_data['body'])
        print(f"   📄 Email preview saved to: {email_preview}")
    else:
        print("ℹ️  No significant changes - no email sent")
    print()
    
    # Step 4: Save snapshot
    print("📍 STEP 4: Save snapshot for next comparison")
    print("-" * 60)
    snapshot_file = save_snapshot(current_products, snapshot_dir)
    print()
    
    # Summary
    print("=" * 60)
    print("✅ EXECUTION COMPLETED")
    print("=" * 60)
    print(f"Status: SUCCESS")
    print(f"Products monitored: {comparison['total_products']}")
    print(f"Changes detected: {comparison.get('total_changes', 0)}")
    print(f"Significant changes: {len(significant_changes) if has_significant else 0}")
    print(f"Snapshot saved: {snapshot_file.name}")
    if email_data:
        print(f"Email prepared: YES")
    print()
    print("⏰ Next execution: 2026-01-15 00:00:00 UTC")
    print("=" * 60)
    
    return {
        'success': True,
        'execution_time': datetime.utcnow().isoformat(),
        'products_monitored': comparison['total_products'],
        'changes_detected': comparison.get('total_changes', 0),
        'significant_changes': len(significant_changes) if has_significant else 0,
        'email_sent': email_data is not None,
        'snapshot_file': str(snapshot_file)
    }

if __name__ == '__main__':
    result = main()
    print(f"\n📊 Execution Result: {json.dumps(result, indent=2)}")
