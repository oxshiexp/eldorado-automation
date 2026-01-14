"""
Eldorado.gg Price Monitor
Monitor perubahan harga dan detail produk dari seller tertentu
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from scraper import EldoradoScraper
import difflib

from telegram_notifier import get_notifier

class EldoradoMonitor:
    def __init__(self, notification_email: str = None):
        """
        Initialize monitor
        
        Args:
            notification_email: Email untuk notifikasi (optional)
        """
        self.scraper = EldoradoScraper()
        self.notification_email = notification_email
        self.history_file = 'price_history.json'
        self.changes_file = 'detected_changes.json'
        
    def monitor_seller(self, seller_url: str, check_interval: int = 3600) -> None:
        """
        Monitor seller continuously
        
        Args:
            seller_url: URL seller profile
            check_interval: Check interval in seconds (default: 1 hour)
        """
        print(f"🔍 Starting monitoring for: {seller_url}")
        print(f"⏱️ Check interval: {check_interval} seconds ({check_interval/60} minutes)")
        
        # Initial scrape
        previous_products = self.scraper.scrape_seller_products(seller_url)
        self._save_snapshot(previous_products, 'initial')
        
        print(f"\n✅ Initial snapshot saved: {len(previous_products)} products")
        print(f"⏳ Next check in {check_interval/60} minutes...\n")
        
        check_count = 1
        
        while True:
            try:
                time.sleep(check_interval)
                
                check_count += 1
                print(f"\n{'='*60}")
                print(f"🔄 Check #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*60}")
                
                # Scrape current products
                current_products = self.scraper.scrape_seller_products(seller_url)
                
                # Compare and detect changes
                changes = self.compare_products(previous_products, current_products)
                
                if changes['has_changes']:
                    print(f"\n🔔 CHANGES DETECTED!")
                    self._handle_changes(changes, seller_url)
                else:
                    print(f"\n✓ No changes detected")
                
                # Save current snapshot
                self._save_snapshot(current_products, f'check_{check_count}')
                
                # Update previous products
                previous_products = current_products
                
                print(f"\n⏳ Next check in {check_interval/60} minutes...")
                
            except KeyboardInterrupt:
                print(f"\n\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Error during monitoring: {e}")
                print(f"⏳ Retrying in {check_interval/60} minutes...")
                time.sleep(check_interval)
    
    def compare_products(self, previous: List[Dict], current: List[Dict]) -> Dict:
        """
        Compare two product snapshots and detect changes
        
        Returns:
            Dictionary with change details
        """
        changes = {
            'has_changes': False,
            'timestamp': datetime.now().isoformat(),
            'price_changes': [],
            'stock_changes': [],
            'new_products': [],
            'removed_products': [],
            'description_changes': []
        }
        
        # Create lookup dictionaries
        prev_dict = {p['offer_id']: p for p in previous if p.get('offer_id')}
        curr_dict = {p['offer_id']: p for p in current if p.get('offer_id')}
        
        # Check for new products
        new_ids = set(curr_dict.keys()) - set(prev_dict.keys())
        for offer_id in new_ids:
            product = curr_dict[offer_id]
            changes['new_products'].append({
                'offer_id': offer_id,
                'game': product.get('game_name'),
                'type': product.get('product_type'),
                'price': product.get('price'),
                'stock': product.get('stock')
            })
            changes['has_changes'] = True
        
        # Check for removed products
        removed_ids = set(prev_dict.keys()) - set(curr_dict.keys())
        for offer_id in removed_ids:
            product = prev_dict[offer_id]
            changes['removed_products'].append({
                'offer_id': offer_id,
                'game': product.get('game_name'),
                'type': product.get('product_type'),
                'was_price': product.get('price')
            })
            changes['has_changes'] = True
        
        # Check for changes in existing products
        common_ids = set(prev_dict.keys()) & set(curr_dict.keys())
        for offer_id in common_ids:
            prev_prod = prev_dict[offer_id]
            curr_prod = curr_dict[offer_id]
            
            # Price changes
            if prev_prod.get('price_numeric') != curr_prod.get('price_numeric'):
                price_change = {
                    'offer_id': offer_id,
                    'game': curr_prod.get('game_name'),
                    'type': curr_prod.get('product_type'),
                    'old_price': prev_prod.get('price'),
                    'new_price': curr_prod.get('price'),
                    'old_numeric': prev_prod.get('price_numeric'),
                    'new_numeric': curr_prod.get('price_numeric'),
                    'change_percent': self._calculate_change_percent(
                        prev_prod.get('price_numeric', 0),
                        curr_prod.get('price_numeric', 0)
                    )
                }
                changes['price_changes'].append(price_change)
                changes['has_changes'] = True
            
            # Stock changes
            if prev_prod.get('stock_numeric') != curr_prod.get('stock_numeric'):
                stock_change = {
                    'offer_id': offer_id,
                    'game': curr_prod.get('game_name'),
                    'old_stock': prev_prod.get('stock'),
                    'new_stock': curr_prod.get('stock'),
                    'old_numeric': prev_prod.get('stock_numeric'),
                    'new_numeric': curr_prod.get('stock_numeric')
                }
                changes['stock_changes'].append(stock_change)
                changes['has_changes'] = True
            
            # Description changes
            if prev_prod.get('description') != curr_prod.get('description'):
                desc_change = {
                    'offer_id': offer_id,
                    'game': curr_prod.get('game_name'),
                    'old_description': prev_prod.get('description', ''),
                    'new_description': curr_prod.get('description', '')
                }
                changes['description_changes'].append(desc_change)
                changes['has_changes'] = True
        
        return changes
    
    def _calculate_change_percent(self, old_value: float, new_value: float) -> float:
        """Calculate percentage change"""
        if old_value == 0:
            return 0
        return round(((new_value - old_value) / old_value) * 100, 2)
    
    def _handle_changes(self, changes: Dict, seller_url: str) -> None:
        """Handle detected changes"""
        # Print changes summary
        print(f"\n📊 Changes Summary:")
        print(f"   💰 Price changes: {len(changes['price_changes'])}")
        print(f"   📦 Stock changes: {len(changes['stock_changes'])}")
        print(f"   ✨ New products: {len(changes['new_products'])}")
        print(f"   🗑️ Removed products: {len(changes['removed_products'])}")
        print(f"   📝 Description changes: {len(changes['description_changes'])}")
        
        # Print detailed price changes
        if changes['price_changes']:
            print(f"\n💰 PRICE CHANGES:")
            for change in changes['price_changes']:
                direction = "📈" if change['change_percent'] > 0 else "📉"
                print(f"   {direction} {change['game']} - {change['type']}")
                print(f"      {change['old_price']} → {change['new_price']}")
                print(f"      Change: {change['change_percent']:+.2f}%")
        
        # Print new products
        if changes['new_products']:
            print(f"\n✨ NEW PRODUCTS:")
            for product in changes['new_products']:
                print(f"   + {product['game']} - {product['type']}")
                print(f"     Price: {product['price']}, Stock: {product['stock']}")
        
        # Print removed products
        if changes['removed_products']:
            print(f"\n🗑️ REMOVED PRODUCTS:")
            for product in changes['removed_products']:
                print(f"   - {product['game']} - {product['type']}")
                print(f"     Was: {product['was_price']}")
        
        # Save changes to file
        self._save_changes(changes)
        
        # Send notification
        self._send_notification(changes, seller_url)
    
    def _save_snapshot(self, products: List[Dict], label: str) -> None:
        """Save product snapshot to history"""
        try:
            # Load existing history
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except FileNotFoundError:
                history = []
            
            # Add new snapshot
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'label': label,
                'product_count': len(products),
                'products': products
            }
            history.append(snapshot)
            
            # Keep only last 50 snapshots
            history = history[-50:]
            
            # Save
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Warning: Could not save snapshot: {e}")
    
    def _save_changes(self, changes: Dict) -> None:
        """Save detected changes"""
        try:
            # Load existing changes
            try:
                with open(self.changes_file, 'r', encoding='utf-8') as f:
                    all_changes = json.load(f)
            except FileNotFoundError:
                all_changes = []
            
            # Add new changes
            all_changes.append(changes)
            
            # Keep only last 100 change events
            all_changes = all_changes[-100:]
            
            # Save
            with open(self.changes_file, 'w', encoding='utf-8') as f:
                json.dump(all_changes, f, indent=2, ensure_ascii=False)
                
            print(f"\n💾 Changes saved to {self.changes_file}")
                
        except Exception as e:
            print(f"⚠️ Warning: Could not save changes: {e}")
    
    def _send_notification(self, changes: Dict, seller_url: str) -> None:
        """Send notification about changes"""
        if not self.notification_email:
            return
        
        # Prepare email content
        subject = f"🔔 Eldorado Price Alert - Changes Detected"
        
        body = f"""
Price monitoring alert for: {seller_url}
Time: {changes['timestamp']}

SUMMARY:
- Price changes: {len(changes['price_changes'])}
- Stock changes: {len(changes['stock_changes'])}
- New products: {len(changes['new_products'])}
- Removed products: {len(changes['removed_products'])}

PRICE CHANGES:
"""
        
        for change in changes['price_changes']:
            body += f"\n{change['game']} - {change['type']}\n"
            body += f"  {change['old_price']} → {change['new_price']} ({change['change_percent']:+.2f}%)\n"
        
        # Send via Nebula email
        try:
            # This will be called via the send_email tool when integrated
            print(f"\n📧 Notification prepared for: {self.notification_email}")
            print(f"   (Email integration requires Nebula send_email tool)")
        except Exception as e:
            print(f"⚠️ Could not send notification: {e}")


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python monitor.py <seller_url> [check_interval_minutes]")
        print("\nExample:")
        print("  python monitor.py 'https://www.eldorado.gg/users/Alayon?category=Currency' 60")
        return
    
    seller_url = sys.argv[1]
    check_interval = int(sys.argv[2]) * 60 if len(sys.argv) > 2 else 3600
    
    # Initialize monitor
    monitor = EldoradoMonitor(notification_email="your@email.com")
    
    # Start monitoring
    monitor.monitor_seller(seller_url, check_interval)


if __name__ == "__main__":
    notifier = get_notifier()
    notifier.notify_start("Price Monitor")
    
    main()
