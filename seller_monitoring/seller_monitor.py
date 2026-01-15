"""
Eldorado Seller Monitoring System
Monitors seller activities and sends Telegram notifications for changes
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from seller_monitoring.database import MonitoringDatabase
from shared.telegram_notifier import TelegramNotifier

class SellerMonitor:
    def __init__(self, config_path: str = "seller_monitoring/seller_config.json"):
        """Initialize seller monitoring system"""
        self.config_path = config_path
        self.config = self.load_config()
        self.db = MonitoringDatabase()
        self.telegram = TelegramNotifier()
        
        print(f"[{self.get_timestamp()}] Seller Monitor initialized")
        print(f"Monitoring {len(self.config['sellers'])} sellers")
        print(f"Interval: {self.config['monitoring_interval_minutes']} minutes")
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            print("Creating default config...")
            default_config = {
                "sellers": [],
                "monitoring_interval_minutes": 10,
                "telegram_enabled": True,
                "rate_limit_delay_seconds": 2
            }
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def get_timestamp(self) -> str:
        """Get formatted timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def fetch_seller_products(self, seller_username: str) -> List[Dict]:
        """Fetch all products from a seller's shop"""
        try:
            # Eldorado.gg API endpoint for seller listings
            url = f"https://api.eldorado.gg/v1/users/{seller_username}/listings"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                products = []
                
                # Parse product data
                for item in data.get('listings', []):
                    product = {
                        'product_id': item.get('id', ''),
                        'title': item.get('title', ''),
                        'price': float(item.get('price', 0)),
                        'stock': int(item.get('quantity', 0)),
                        'description': item.get('description', ''),
                        'category': item.get('game', {}).get('name', ''),
                        'image_url': item.get('image_url', ''),
                        'url': f"https://eldorado.gg/listings/{item.get('id', '')}"
                    }
                    products.append(product)
                
                return products
            
            elif response.status_code == 404:
                print(f"Seller not found: {seller_username}")
                return []
            
            else:
                print(f"Error fetching products: HTTP {response.status_code}")
                return []
        
        except Exception as e:
            print(f"Exception fetching products for {seller_username}: {e}")
            return []
    
    def detect_changes(self, seller_config: Dict) -> Dict[str, List]:
        """Detect changes for a seller and return categorized changes"""
        seller_username = seller_config['username']
        
        print(f"\n[{self.get_timestamp()}] Checking seller: {seller_username}")
        
        # Fetch current products from eldorado
        current_products = self.fetch_seller_products(seller_username)
        
        if not current_products:
            print(f"No products fetched for {seller_username}")
            return {'new': [], 'price_changes': [], 'edits': [], 'deleted': []}
        
        print(f"Fetched {len(current_products)} products")
        
        # Get existing products from database
        db_products = self.db.get_seller_products(seller_username, active_only=True)
        db_product_ids = {p['product_id'] for p in db_products}
        current_product_ids = {p['product_id'] for p in current_products}
        
        changes = {
            'new': [],
            'price_changes': [],
            'edits': [],
            'deleted': []
        }
        
        # Detect new products
        new_product_ids = current_product_ids - db_product_ids
        for product in current_products:
            if product['product_id'] in new_product_ids:
                if seller_config.get('notify_new_product', True):
                    changes['new'].append(product)
                    self.db.log_change(
                        seller_username,
                        product['product_id'],
                        'new',
                        product,
                        notified=False
                    )
                # Add to database
                self.db.add_product(seller_username, product)
                print(f"  [NEW] {product['title']} - Rp {product['price']:,.0f}")
        
        # Detect deleted products
        deleted_product_ids = db_product_ids - current_product_ids
        for product_id in deleted_product_ids:
            product = self.db.get_product(product_id)
            if product and seller_config.get('notify_delete', True):
                changes['deleted'].append(product)
                self.db.log_change(
                    seller_username,
                    product_id,
                    'deleted',
                    product,
                    notified=False
                )
            self.db.mark_product_deleted(product_id)
            print(f"  [DELETED] {product['title']}")
        
        # Detect changes in existing products
        for product in current_products:
            if product['product_id'] in db_product_ids:
                result = self.db.update_product(product['product_id'], product)
                
                if result['changed']:
                    for change in result['changes']:
                        if change['type'] == 'price':
                            if seller_config.get('notify_price_change', True):
                                change_data = {
                                    'product': result['product'],
                                    'old_price': change['old'],
                                    'new_price': change['new'],
                                    'percent': change['percent']
                                }
                                changes['price_changes'].append(change_data)
                                self.db.log_change(
                                    seller_username,
                                    product['product_id'],
                                    'price',
                                    change_data,
                                    notified=False
                                )
                                print(f"  [PRICE] {result['product']['title']}: "
                                      f"Rp {change['old']:,.0f} → Rp {change['new']:,.0f} "
                                      f"({change['percent']:+.1f}%)")
                        
                        elif change['type'] == 'edit':
                            if seller_config.get('notify_edit', True):
                                edit_data = {
                                    'product': result['product'],
                                    'field': change['field'],
                                    'old': change['old'],
                                    'new': change['new']
                                }
                                changes['edits'].append(edit_data)
                                self.db.log_change(
                                    seller_username,
                                    product['product_id'],
                                    'edit',
                                    edit_data,
                                    notified=False
                                )
                                print(f"  [EDIT] {result['product']['title']}: "
                                      f"{change['field']} changed")
        
        return changes
    
    def send_notifications(self, seller_config: Dict, changes: Dict[str, List]):
        """Send Telegram notifications for detected changes"""
        if not self.config.get('telegram_enabled', True):
            return
        
        seller_username = seller_config['username']
        display_name = seller_config.get('display_name', seller_username)
        
        # Prepare notification message
        if not any(changes.values()):
            return
        
        message = f"🔔 SELLER ACTIVITY DETECTED\n\n"
        message += f"👤 Seller: {display_name}\n"
        message += f"━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # New products
        if changes['new']:
            message += f"📦 NEW PRODUCTS ({len(changes['new'])})\n"
            for product in changes['new'][:5]:  # Limit to 5
                message += f"\n• {product['title']}\n"
                message += f"  💰 Rp {product['price']:,.0f}\n"
                message += f"  📊 Stock: {product['stock']}\n"
                message += f"  🔗 {product['url']}\n"
            if len(changes['new']) > 5:
                message += f"\n... and {len(changes['new']) - 5} more\n"
            message += "\n"
        
        # Price changes
        if changes['price_changes']:
            message += f"💰 PRICE CHANGES ({len(changes['price_changes'])})\n"
            for change in changes['price_changes'][:5]:
                product = change['product']
                emoji = "📉" if change['percent'] < 0 else "📈"
                message += f"\n• {product['title']}\n"
                message += f"  Old: Rp {change['old_price']:,.0f}\n"
                message += f"  New: Rp {change['new_price']:,.0f}\n"
                message += f"  Change: {change['percent']:+.1f}% {emoji}\n"
                message += f"  🔗 {product['url']}\n"
            if len(changes['price_changes']) > 5:
                message += f"\n... and {len(changes['price_changes']) - 5} more\n"
            message += "\n"
        
        # Edits
        if changes['edits']:
            message += f"✏️ PRODUCT EDITS ({len(changes['edits'])})\n"
            for edit in changes['edits'][:3]:
                product = edit['product']
                message += f"\n• {product['title']}\n"
                message += f"  Changed: {edit['field']}\n"
                message += f"  🔗 {product['url']}\n"
            if len(changes['edits']) > 3:
                message += f"\n... and {len(changes['edits']) - 3} more\n"
            message += "\n"
        
        # Deleted products
        if changes['deleted']:
            message += f"🗑️ DELETED PRODUCTS ({len(changes['deleted'])})\n"
            for product in changes['deleted'][:3]:
                message += f"\n• {product['title']}\n"
                message += f"  Last price: Rp {product['price']:,.0f}\n"
            if len(changes['deleted']) > 3:
                message += f"\n... and {len(changes['deleted']) - 3} more\n"
            message += "\n"
        
        message += f"⏰ {self.get_timestamp()}\n"
        
        # Send notification
        try:
            self.telegram.send_message(message)
            print(f"✓ Notification sent for {seller_username}")
        except Exception as e:
            print(f"✗ Failed to send notification: {e}")
    
    def monitor_once(self):
        """Run one monitoring cycle for all sellers"""
        print(f"\n{'='*60}")
        print(f"[{self.get_timestamp()}] Starting monitoring cycle")
        print(f"{'='*60}")
        
        for seller_config in self.config['sellers']:
            try:
                # Detect changes
                changes = self.detect_changes(seller_config)
                
                # Send notifications
                self.send_notifications(seller_config, changes)
                
                # Rate limiting
                time.sleep(self.config.get('rate_limit_delay_seconds', 2))
            
            except Exception as e:
                print(f"Error monitoring seller {seller_config['username']}: {e}")
        
        # Print stats
        stats = self.db.get_stats()
        print(f"\n{'='*60}")
        print(f"Cycle complete:")
        print(f"  Total products: {stats['total_products']}")
        print(f"  Active products: {stats['active_products']}")
        print(f"  Changes today: {stats['changes_today']}")
        print(f"{'='*60}\n")
    
    def run_continuous(self):
        """Run monitoring continuously with specified interval"""
        print(f"\n🚀 Seller Monitor started - Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.monitor_once()
                
                # Wait for next cycle
                interval_seconds = self.config['monitoring_interval_minutes'] * 60
                print(f"Waiting {self.config['monitoring_interval_minutes']} minutes until next check...")
                time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n\n❌ Fatal error: {e}")
        finally:
            self.db.close()

def main():
    """Main entry point"""
    monitor = SellerMonitor()
    monitor.run_continuous()

if __name__ == "__main__":
    main()
