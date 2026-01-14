"""
Eldorado.gg Complete Automation System
Orchestrates scraping, uploading, and monitoring
"""

import json
import argparse
from datetime import datetime
from typing import Dict, List
from scraper import EldoradoScraper
from uploader import EldoradoUploader
from monitor import EldoradoMonitor

class EldoradoAutomation:
    def __init__(self, api_key: str = None, notification_email: str = None):
        """
        Initialize automation system
        
        Args:
            api_key: Eldorado Seller API Key
            notification_email: Email for notifications
        """
        self.scraper = EldoradoScraper()
        self.uploader = EldoradoUploader(api_key=api_key)
        self.monitor = EldoradoMonitor(notification_email=notification_email)
        self.config_file = 'automation_config.json'
        
    def scrape_and_upload(self, seller_url: str, auto_adjust_price: bool = True, 
                         price_adjustment: float = 0.95) -> Dict:
        """
        Scrape produk dari seller dan upload ke akun Anda
        
        Args:
            seller_url: URL seller yang akan di-scrape
            auto_adjust_price: Otomatis adjust harga (lebih murah)
            price_adjustment: Multiplier untuk harga (0.95 = 5% lebih murah)
            
        Returns:
            Summary of operation
        """
        print(f"\n{'='*60}")
        print(f"🚀 SCRAPE & UPLOAD AUTOMATION")
        print(f"{'='*60}")
        print(f"📍 Target: {seller_url}")
        print(f"💰 Price adjustment: {price_adjustment}x (competitor's price)")
        print(f"{'='*60}\n")
        
        # Step 1: Scrape products
        print("STEP 1: Scraping products...")
        products = self.scraper.scrape_seller_products(seller_url)
        
        if not products:
            return {'error': 'No products found'}
        
        # Save scraped data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        scrape_file = f'scraped_{timestamp}.json'
        self.scraper.save_to_json(products, scrape_file)
        
        # Step 2: Adjust prices if enabled
        if auto_adjust_price:
            print(f"\nSTEP 2: Adjusting prices ({price_adjustment}x)...")
            for product in products:
                if product.get('price_numeric'):
                    original_price = product['price_numeric']
                    product['price_numeric'] = round(original_price * price_adjustment, 4)
                    product['price_adjusted'] = True
                    print(f"   {product.get('game_name', 'Unknown')}: ${original_price} → ${product['price_numeric']}")
        
        # Step 3: Upload products
        print(f"\nSTEP 3: Uploading products...")
        upload_results = self.uploader.bulk_upload(products)
        
        # Summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'source_seller': seller_url,
            'products_scraped': len(products),
            'upload_results': upload_results,
            'scrape_file': scrape_file
        }
        
        # Save summary
        self._save_operation_log(summary)
        
        print(f"\n{'='*60}")
        print(f"✅ AUTOMATION COMPLETED")
        print(f"{'='*60}")
        print(f"📊 Products scraped: {len(products)}")
        print(f"✅ Successfully uploaded: {upload_results['success']}")
        print(f"❌ Failed: {upload_results['failed']}")
        print(f"💾 Saved to: {scrape_file}")
        print(f"{'='*60}\n")
        
        return summary
    
    def setup_monitoring(self, seller_urls: List[str], check_interval: int = 3600,
                        notification_email: str = None) -> None:
        """
        Setup monitoring untuk multiple sellers
        
        Args:
            seller_urls: List of seller URLs to monitor
            check_interval: Check interval in seconds
            notification_email: Email for notifications
        """
        config = {
            'sellers': seller_urls,
            'check_interval': check_interval,
            'notification_email': notification_email or self.monitor.notification_email,
            'created_at': datetime.now().isoformat()
        }
        
        # Save config
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Monitoring config saved to {self.config_file}")
        print(f"📍 Monitoring {len(seller_urls)} seller(s)")
        print(f"⏱️ Check interval: {check_interval/60} minutes")
        
        # Start monitoring first seller (for demo)
        if seller_urls:
            print(f"\n🔍 Starting monitoring for: {seller_urls[0]}")
            self.monitor.monitor_seller(seller_urls[0], check_interval)
    
    def sync_products(self, seller_url: str) -> Dict:
        """
        Sync produk: scrape, compare dengan listing Anda, update yang berubah
        
        Args:
            seller_url: URL seller competitor
            
        Returns:
            Sync summary
        """
        print(f"\n{'='*60}")
        print(f"🔄 PRODUCT SYNC")
        print(f"{'='*60}\n")
        
        # Scrape competitor products
        print("Step 1: Scraping competitor products...")
        competitor_products = self.scraper.scrape_seller_products(seller_url)
        
        # Load our previous products
        try:
            with open('our_products.json', 'r', encoding='utf-8') as f:
                our_products = json.load(f)
            print(f"Step 2: Loaded {len(our_products)} of our products")
        except FileNotFoundError:
            print("Step 2: No existing products found, will upload all")
            our_products = []
        
        # Compare and update
        updates_needed = []
        new_products = []
        
        for comp_prod in competitor_products:
            # Find matching product in our listings
            match = None
            for our_prod in our_products:
                if (our_prod.get('game_name') == comp_prod.get('game_name') and
                    our_prod.get('server_region') == comp_prod.get('server_region')):
                    match = our_prod
                    break
            
            if match:
                # Check if price changed
                if match.get('price_numeric') != comp_prod.get('price_numeric'):
                    updates_needed.append({
                        'offer_id': match.get('offer_id'),
                        'game': comp_prod.get('game_name'),
                        'old_price': match.get('price_numeric'),
                        'new_price': comp_prod.get('price_numeric') * 0.95  # 5% cheaper
                    })
            else:
                new_products.append(comp_prod)
        
        # Apply updates
        print(f"\nStep 3: Applying updates...")
        print(f"   Updates needed: {len(updates_needed)}")
        print(f"   New products: {len(new_products)}")
        
        for update in updates_needed:
            self.uploader.update_product(
                update['offer_id'],
                {'price': update['new_price']}
            )
        
        # Upload new products
        if new_products:
            self.uploader.bulk_upload(new_products)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'competitor_url': seller_url,
            'updates_applied': len(updates_needed),
            'new_products_added': len(new_products)
        }
        
        print(f"\n✅ Sync completed!")
        return summary
    
    def _save_operation_log(self, operation: Dict) -> None:
        """Save operation log"""
        log_file = 'automation_log.json'
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = []
        
        logs.append(operation)
        logs = logs[-100:]  # Keep last 100 operations
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Eldorado.gg Automation System')
    parser.add_argument('command', choices=['scrape', 'upload', 'monitor', 'sync', 'scrape-upload'],
                       help='Command to execute')
    parser.add_argument('--seller-url', required=False,
                       help='Seller URL to scrape/monitor')
    parser.add_argument('--file', help='JSON file with products to upload')
    parser.add_argument('--interval', type=int, default=60,
                       help='Monitoring interval in minutes (default: 60)')
    parser.add_argument('--price-adjustment', type=float, default=0.95,
                       help='Price adjustment multiplier (default: 0.95 = 5% cheaper)')
    parser.add_argument('--email', help='Email for notifications')
    parser.add_argument('--api-key', help='Eldorado API key')
    
    args = parser.parse_args()
    
    # Initialize automation
    automation = EldoradoAutomation(
        api_key=args.api_key,
        notification_email=args.email
    )
    
    # Execute command
    if args.command == 'scrape':
        if not args.seller_url:
            print("Error: --seller-url required for scrape command")
            return
        
        products = automation.scraper.scrape_seller_products(args.seller_url)
        automation.scraper.save_to_json(products, 'scraped_products.json')
        automation.scraper.save_to_csv(products, 'scraped_products.csv')
        
    elif args.command == 'upload':
        if not args.file:
            print("Error: --file required for upload command")
            return
        
        products = automation.uploader.load_products_from_json(args.file)
        results = automation.uploader.bulk_upload(products)
        
    elif args.command == 'scrape-upload':
        if not args.seller_url:
            print("Error: --seller-url required")
            return
        
        automation.scrape_and_upload(
            args.seller_url,
            price_adjustment=args.price_adjustment
        )
        
    elif args.command == 'monitor':
        if not args.seller_url:
            print("Error: --seller-url required for monitor command")
            return
        
        automation.setup_monitoring(
            [args.seller_url],
            check_interval=args.interval * 60,
            notification_email=args.email
        )
        
    elif args.command == 'sync':
        if not args.seller_url:
            print("Error: --seller-url required for sync command")
            return
        
        automation.sync_products(args.seller_url)


if __name__ == "__main__":
    main()
