"""
Eldorado.gg Auto Upload Tool
Upload produk secara otomatis menggunakan Seller API atau Bulk Upload
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import time
import os

class EldoradoUploader:
    def __init__(self, api_key: str = None, seller_id: str = None):
        """
        Initialize uploader dengan API credentials
        
        Args:
            api_key: Eldorado Seller API Key (dapatkan dari dashboard seller)
            seller_id: Seller account ID
        """
        self.api_key = api_key or os.getenv('ELDORADO_API_KEY')
        self.seller_id = seller_id or os.getenv('ELDORADO_SELLER_ID')
        self.base_url = "https://api.eldorado.gg/v1"  # Endpoint API (perlu dikonfirmasi)
        
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'EldoradoAutoUploader/1.0'
            })
    
    def upload_product(self, product: Dict) -> Dict:
        """
        Upload single product ke Eldorado
        
        Args:
            product: Product data dictionary
            
        Returns:
            Response from API
        """
        if not self.api_key:
            return {'error': 'API key not configured. Set ELDORADO_API_KEY environment variable'}
        
        # Format product data sesuai Eldorado API schema
        formatted_data = self._format_product_data(product)
        
        try:
            print(f"📤 Uploading: {product.get('game_name')} - {product.get('product_type')}")
            
            # API endpoint untuk create offer
            endpoint = f"{self.base_url}/offers"
            
            response = self.session.post(endpoint, json=formatted_data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Uploaded successfully! Offer ID: {result.get('id')}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Upload failed: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" | Details: {error_detail}"
                except:
                    error_msg += f" | Status: {e.response.status_code}"
            
            print(error_msg)
            return {'error': error_msg, 'product': product}
    
    def bulk_upload(self, products: List[Dict], batch_size: int = 10) -> Dict:
        """
        Upload multiple products in batches
        
        Args:
            products: List of product dictionaries
            batch_size: Number of products per batch
            
        Returns:
            Summary of upload results
        """
        if not self.api_key:
            return {'error': 'API key not configured'}
        
        results = {
            'total': len(products),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        print(f"🚀 Starting bulk upload: {len(products)} products")
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i+batch_size]
            
            print(f"\n📦 Batch {i//batch_size + 1}: Processing {len(batch)} products")
            
            for product in batch:
                result = self.upload_product(product)
                
                if 'error' in result:
                    results['failed'] += 1
                    results['errors'].append({
                        'product': product.get('game_name', 'Unknown'),
                        'error': result['error']
                    })
                else:
                    results['success'] += 1
                
                # Rate limiting
                time.sleep(0.5)
            
            # Pause between batches
            if i + batch_size < len(products):
                print(f"⏸️ Pausing 5 seconds before next batch...")
                time.sleep(5)
        
        print(f"\n✅ Bulk upload completed!")
        print(f"   Success: {results['success']}")
        print(f"   Failed: {results['failed']}")
        
        return results
    
    def update_product(self, offer_id: str, updates: Dict) -> Dict:
        """
        Update existing product
        
        Args:
            offer_id: Eldorado offer ID
            updates: Dictionary of fields to update (price, stock, description, etc)
            
        Returns:
            API response
        """
        if not self.api_key:
            return {'error': 'API key not configured'}
        
        try:
            endpoint = f"{self.base_url}/offers/{offer_id}"
            
            print(f"🔄 Updating offer {offer_id}...")
            
            response = self.session.patch(endpoint, json=updates, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Updated successfully!")
            
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Update failed: {e}"
            print(error_msg)
            return {'error': error_msg}
    
    def delete_product(self, offer_id: str) -> Dict:
        """
        Delete product from listing
        
        Args:
            offer_id: Eldorado offer ID
            
        Returns:
            API response
        """
        if not self.api_key:
            return {'error': 'API key not configured'}
        
        try:
            endpoint = f"{self.base_url}/offers/{offer_id}"
            
            print(f"🗑️ Deleting offer {offer_id}...")
            
            response = self.session.delete(endpoint, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Deleted successfully!")
            return {'success': True}
            
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Delete failed: {e}"
            print(error_msg)
            return {'error': error_msg}
    
    def _format_product_data(self, product: Dict) -> Dict:
        """
        Format scraped product data to Eldorado API schema
        
        NOTE: Schema ini adalah estimasi. Perlu disesuaikan dengan dokumentasi API yang sebenarnya
        """
        formatted = {
            'game': product.get('game_name', ''),
            'type': product.get('product_type', 'Currency'),
            'title': self._generate_title(product),
            'description': product.get('description', ''),
            'price': product.get('price_numeric', 0),
            'price_unit': product.get('price_unit', 'M'),
            'stock': product.get('stock_numeric', 0),
            'min_quantity': self._parse_quantity(product.get('min_quantity', '')),
            'delivery_time': product.get('delivery_time', ''),
            'server': product.get('server_region', ''),
            'faction': product.get('faction', ''),
            'metadata': {
                'scraped_from': product.get('product_url', ''),
                'original_seller': product.get('seller_name', ''),
                'scraped_at': product.get('scraped_at', '')
            }
        }
        
        # Remove empty fields
        formatted = {k: v for k, v in formatted.items() if v}
        
        return formatted
    
    def _generate_title(self, product: Dict) -> str:
        """Generate product title"""
        parts = []
        
        if product.get('game_name'):
            parts.append(product['game_name'])
        
        if product.get('server_region'):
            parts.append(product['server_region'])
        
        if product.get('faction'):
            parts.append(product['faction'])
        
        if product.get('product_type'):
            parts.append(product['product_type'])
        
        return ' - '.join(parts) if parts else 'Product'
    
    def _parse_quantity(self, quantity_str: str) -> int:
        """Parse quantity string to number"""
        import re
        match = re.search(r'(\d+)', quantity_str)
        return int(match.group(1)) if match else 0
    
    def load_products_from_json(self, filename: str) -> List[Dict]:
        """Load products from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                products = json.load(f)
            print(f"📂 Loaded {len(products)} products from {filename}")
            return products
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return []
    
    def generate_csv_template(self, filename: str = 'bulk_upload_template.csv'):
        """Generate CSV template for bulk upload"""
        import csv
        
        headers = [
            'game_name', 'product_type', 'server_region', 'faction',
            'price_numeric', 'price_unit', 'stock_numeric', 'min_quantity',
            'delivery_time', 'description'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            # Add example row
            example = {
                'game_name': 'World of Warcraft',
                'product_type': 'Gold',
                'server_region': 'NA',
                'faction': 'Alliance',
                'price_numeric': '0.045',
                'price_unit': 'K',
                'stock_numeric': '10000',
                'min_quantity': '100',
                'delivery_time': '1 hour',
                'description': 'Fast delivery, safe trade'
            }
            writer.writerow(example)
        
        print(f"📄 Template created: {filename}")


def main():
    """Example usage"""
    # Initialize uploader
    # NOTE: Anda perlu mendapatkan API key dari Eldorado seller dashboard
    uploader = EldoradoUploader()
    
    # Generate template CSV
    uploader.generate_csv_template()
    
    print("\n" + "="*60)
    print("🔑 SETUP INSTRUCTIONS:")
    print("="*60)
    print("1. Daftar sebagai seller di https://www.eldorado.gg/become-seller")
    print("2. Verify akun Anda")
    print("3. Dapatkan API key dari seller dashboard")
    print("4. Set environment variables:")
    print("   export ELDORADO_API_KEY='your_api_key'")
    print("   export ELDORADO_SELLER_ID='your_seller_id'")
    print("\n5. Upload products:")
    print("   python uploader.py upload products.json")
    print("="*60)


if __name__ == "__main__":
    main()
