"""
Eldorado.gg Product Scraper
Scrape semua produk dari seller profile dengan detail lengkap
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import time

from telegram_notifier import get_notifier

class EldoradoScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def scrape_seller_products(self, seller_url: str) -> List[Dict]:
        """
        Scrape semua produk dari seller profile
        
        Args:
            seller_url: URL seller profile (contoh: https://www.eldorado.gg/users/Alayon?category=Currency)
            
        Returns:
            List of product dictionaries dengan detail lengkap
        """
        products = []
        page = 1
        
        print(f"🔍 Scraping seller: {seller_url}")
        
        while True:
            try:
                # Add pagination parameter
                url = f"{seller_url}&page={page}" if '?' in seller_url else f"{seller_url}?page={page}"
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract seller info
                seller_info = self._extract_seller_info(soup)
                
                # Extract products from page
                page_products = self._extract_products_from_page(soup, seller_info)
                
                if not page_products:
                    break
                    
                products.extend(page_products)
                print(f"📦 Page {page}: Found {len(page_products)} products (Total: {len(products)})")
                
                # Check if there's next page
                if not self._has_next_page(soup):
                    break
                    
                page += 1
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error scraping page {page}: {e}")
                break
        
        print(f"✅ Total products scraped: {len(products)}")
        return products
    
    def _extract_seller_info(self, soup: BeautifulSoup) -> Dict:
        """Extract seller information"""
        seller_info = {
            'seller_name': '',
            'rating': '',
            'total_reviews': 0,
            'verified': False,
            'online_status': False
        }
        
        try:
            # Seller name
            name_elem = soup.find('h1') or soup.find(class_=re.compile('seller.*name', re.I))
            if name_elem:
                seller_info['seller_name'] = name_elem.get_text(strip=True)
            
            # Rating percentage
            rating_elem = soup.find(text=re.compile(r'\d+\.\d+%'))
            if rating_elem:
                seller_info['rating'] = rating_elem.strip()
            
            # Total reviews
            reviews_elem = soup.find(text=re.compile(r'\d+\s*reviews?'))
            if reviews_elem:
                match = re.search(r'([\d,]+)', reviews_elem)
                if match:
                    seller_info['total_reviews'] = int(match.group(1).replace(',', ''))
            
            # Verified status
            if soup.find(text=re.compile('Verified seller', re.I)):
                seller_info['verified'] = True
            
            # Online status
            if soup.find(text=re.compile('Online', re.I)):
                seller_info['online_status'] = True
                
        except Exception as e:
            print(f"⚠️ Warning extracting seller info: {e}")
        
        return seller_info
    
    def _extract_products_from_page(self, soup: BeautifulSoup, seller_info: Dict) -> List[Dict]:
        """Extract all products from current page"""
        products = []
        
        # Find all product cards/links
        product_links = soup.find_all('a', href=re.compile(r'/(?:buy-|osrs-|gta-|wow-|fortnite-).*?/og/'))
        
        for link in product_links:
            try:
                product = self._extract_product_details(link, seller_info)
                if product:
                    products.append(product)
            except Exception as e:
                print(f"⚠️ Error extracting product: {e}")
                continue
        
        return products
    
    def _extract_product_details(self, element, seller_info: Dict) -> Optional[Dict]:
        """Extract detailed product information from element"""
        product = {
            'seller_name': seller_info['seller_name'],
            'seller_rating': seller_info['rating'],
            'seller_verified': seller_info['verified'],
            'product_url': '',
            'game_name': '',
            'product_type': '',
            'server_region': '',
            'faction': '',
            'price': '',
            'price_unit': '',
            'price_numeric': 0.0,
            'stock': '',
            'stock_numeric': 0,
            'min_quantity': '',
            'delivery_time': '',
            'description': '',
            'offer_id': '',
            'scraped_at': datetime.now().isoformat()
        }
        
        # Product URL
        href = element.get('href', '')
        if href:
            product['product_url'] = f"https://www.eldorado.gg{href}" if href.startswith('/') else href
            
            # Extract offer ID from URL
            match = re.search(r'/og/([a-f0-9-]+)', href)
            if match:
                product['offer_id'] = match.group(1)
        
        # Get all text content
        text_content = element.get_text(separator='|', strip=True)
        parts = [p.strip() for p in text_content.split('|') if p.strip()]
        
        # Extract game name (usually first or has icon alt text)
        img = element.find('img')
        if img and img.get('alt'):
            product['game_name'] = img.get('alt')
        
        # Parse text parts for details
        for part in parts:
            # Server/Region/Faction (contoh: "NAFizzcrankAlliance" atau "EUWestHorde")
            if re.match(r'^[A-Z]{2,3}[A-Za-z\'-]+(?:Alliance|Horde)?$', part):
                # Split region, server, faction
                match = re.match(r'^([A-Z]{2,3})([A-Za-z\'-]+?)(Alliance|Horde)?$', part)
                if match:
                    product['server_region'] = match.group(1)
                    product['server_name'] = match.group(2)
                    product['faction'] = match.group(3) or ''
            
            # Price (contoh: "$0.045 / K" atau "$0.1365 / M")
            elif '$' in part and '/' in part:
                product['price'] = part
                match = re.search(r'\$([0-9.]+)\s*/\s*([KMB]?)', part)
                if match:
                    product['price_numeric'] = float(match.group(1))
                    product['price_unit'] = match.group(2) or 'unit'
            
            # Stock (contoh: "Stock 363 M" atau "In stock 581 M")
            elif re.search(r'stock\s*:?\s*\d+', part, re.I):
                product['stock'] = part
                match = re.search(r'(\d+(?:,\d+)?)\s*([KMB])?', part)
                if match:
                    stock_value = int(match.group(1).replace(',', ''))
                    multiplier = {'K': 1000, 'M': 1000000, 'B': 1000000000}.get(match.group(2), 1)
                    product['stock_numeric'] = stock_value * multiplier
            
            # Min quantity
            elif re.search(r'min\.?\s*qty', part, re.I):
                product['min_quantity'] = part
            
            # Delivery time (contoh: "1 h" atau "2 min - 20 min")
            elif re.search(r'\d+\s*(min|hour|h|day)', part, re.I):
                product['delivery_time'] = part
            
            # Product type
            elif part in ['Gold', 'Currency', 'Account', 'Item', 'Boosting']:
                product['product_type'] = part
        
        # Description (biasanya di element terpisah)
        desc_elem = element.find_next(class_=re.compile('description|offer-desc', re.I))
        if desc_elem:
            product['description'] = desc_elem.get_text(strip=True)
        
        return product if product['product_url'] else None
    
    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """Check if there's a next page"""
        # Look for pagination elements
        pagination = soup.find(class_=re.compile('pagination', re.I))
        if pagination:
            next_button = pagination.find('a', text=re.compile('next|›|»', re.I))
            return next_button is not None
        
        # Alternative: check for "Go to page" or numbered pages
        page_links = soup.find_all('a', href=re.compile(r'[?&]page=\d+'))
        return len(page_links) > 0
    
    def save_to_json(self, products: List[Dict], filename: str = 'products.json'):
        """Save products to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(products)} products to {filename}")
    
    def save_to_csv(self, products: List[Dict], filename: str = 'products.csv'):
        """Save products to CSV file"""
        import csv
        
        if not products:
            print("⚠️ No products to save")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=products[0].keys())
            writer.writeheader()
            writer.writerows(products)
        print(f"💾 Saved {len(products)} products to {filename}")


def main():
    """Example usage"""
    scraper = EldoradoScraper()
    
    # Contoh: Scrape seller Alayon
    seller_url = "https://www.eldorado.gg/users/Alayon?category=Currency"
    
    products = scraper.scrape_seller_products(seller_url)
    
    if products:
        # Save to both JSON and CSV
        scraper.save_to_json(products, 'eldorado_products.json')
        scraper.save_to_csv(products, 'eldorado_products.csv')
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"   Total products: {len(products)}")
        print(f"   Seller: {products[0]['seller_name']}")
        print(f"   Rating: {products[0]['seller_rating']}")
        print(f"   Verified: {products[0]['seller_verified']}")
    

if __name__ == "__main__":
    # Initialize Telegram notifier
    notifier = get_notifier()
    notifier.notify_start("Scraper")
    
    main()
