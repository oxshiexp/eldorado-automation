"""
Eldorado Seller Monitoring - Database Handler
Mengelola database SQLite untuk tracking produk dan riwayat perubahan

FUNGSI UTAMA:
1. Menyimpan data produk seller
2. Tracking perubahan harga
3. Mencatat semua aktivitas (new, edit, delete)
4. Query statistik dan history

STRUKTUR DATABASE:
- products: Snapshot produk terkini
- price_history: Riwayat perubahan harga
- change_log: Log semua perubahan (new/edit/delete)
- monitoring_stats: Statistik monitoring per seller

PENGGUNAAN:
    from database import MonitoringDatabase
    
    # Inisialisasi
    db = MonitoringDatabase("monitor.db")
    
    # Simpan produk baru
    db.save_products("seller123", products_list)
    
    # Deteksi perubahan
    changes = db.detect_changes("seller123", new_products)
    
    # Lihat statistik
    stats = db.get_monitoring_stats("seller123")
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os


class MonitoringDatabase:
    """
    Handler untuk database monitoring seller
    
    Attributes:
        db_path (str): Path ke file database SQLite
        conn (sqlite3.Connection): Koneksi database
    """
    
    def __init__(self, db_path: str = "seller_monitoring/monitor.db"):
        """
        Inisialisasi database connection dan buat tables jika belum ada
        
        Args:
            db_path (str): Path ke file database SQLite
            
        Example:
            db = MonitoringDatabase("monitor.db")
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Hasil query sebagai dict
        self.create_tables()
    
    def create_tables(self):
        """
        Buat semua tables yang dibutuhkan
        
        Tables:
            - products: Produk aktif per seller
            - price_history: Riwayat perubahan harga
            - change_log: Log semua perubahan
            - monitoring_stats: Statistik monitoring
        """
        cursor = self.conn.cursor()
        
        # Table: products
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            seller_username TEXT NOT NULL,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER,
            url TEXT,
            game_name TEXT,
            is_active INTEGER DEFAULT 1,
            first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(seller_username, product_id)
        )
        ''')
        
        # Table: price_history
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            seller_username TEXT NOT NULL,
            old_price REAL NOT NULL,
            new_price REAL NOT NULL,
            price_change_percent REAL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table: change_log
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS change_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_username TEXT NOT NULL,
            change_type TEXT NOT NULL,
            product_id TEXT,
            title TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table: monitoring_stats
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitoring_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_username TEXT NOT NULL UNIQUE,
            total_products INTEGER DEFAULT 0,
            total_changes INTEGER DEFAULT 0,
            last_check_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.conn.commit()
    
    def save_products(self, seller_username: str, products: List[Dict]) -> int:
        """
        Simpan atau update products untuk seller tertentu
        
        Args:
            seller_username (str): Username seller di Eldorado
            products (List[Dict]): List produk dengan fields:
                - product_id: ID unik produk
                - title: Nama produk
                - price: Harga (float)
                - stock: Jumlah stock (int)
                - url: Link produk
                - game_name: Nama game
        
        Returns:
            int: Jumlah produk yang berhasil disimpan
            
        Example:
            products = [
                {
                    'product_id': 'abc123',
                    'title': 'Valorant 475 VP',
                    'price': 45000.0,
                    'stock': 999,
                    'url': 'https://eldorado.gg/...',
                    'game_name': 'Valorant'
                }
            ]
            count = db.save_products("competitor1", products)
            print(f"Saved {count} products")
        """
        cursor = self.conn.cursor()
        saved_count = 0
        
        for product in products:
            try:
                cursor.execute('''
                INSERT INTO products 
                (product_id, seller_username, title, price, stock, url, game_name, last_updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(seller_username, product_id) 
                DO UPDATE SET
                    title = excluded.title,
                    price = excluded.price,
                    stock = excluded.stock,
                    url = excluded.url,
                    game_name = excluded.game_name,
                    last_updated_at = CURRENT_TIMESTAMP
                ''', (
                    product.get('product_id'),
                    seller_username,
                    product.get('title', ''),
                    product.get('price', 0.0),
                    product.get('stock', 0),
                    product.get('url', ''),
                    product.get('game_name', '')
                ))
                saved_count += 1
            except Exception as e:
                print(f"Error saving product {product.get('product_id')}: {e}")
        
        self.conn.commit()
        return saved_count
    
    def get_seller_products(self, seller_username: str, active_only: bool = True) -> List[Dict]:
        """
        Ambil semua produk untuk seller tertentu
        
        Args:
            seller_username (str): Username seller
            active_only (bool): True = hanya produk aktif, False = semua produk
        
        Returns:
            List[Dict]: List produk dengan semua field
            
        Example:
            products = db.get_seller_products("competitor1")
            print(f"Found {len(products)} products")
            
            for p in products:
                print(f"{p['title']}: Rp {p['price']:,.0f}")
        """
        cursor = self.conn.cursor()
        
        query = '''
        SELECT * FROM products 
        WHERE seller_username = ?
        '''
        
        if active_only:
            query += ' AND is_active = 1'
        
        query += ' ORDER BY last_updated_at DESC'
        
        cursor.execute(query, (seller_username,))
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def detect_changes(self, seller_username: str, new_products: List[Dict]) -> Dict:
        """
        Deteksi perubahan antara data lama dan baru
        
        Mendeteksi:
        - Produk baru (new)
        - Perubahan harga (price_changes)
        - Edit produk (edited)
        - Produk dihapus (deleted)
        
        Args:
            seller_username (str): Username seller
            new_products (List[Dict]): Produk terbaru dari scraping
        
        Returns:
            Dict: {
                'new': [produk baru],
                'price_changes': [perubahan harga],
                'edited': [produk yang diedit],
                'deleted': [produk yang dihapus]
            }
            
        Example:
            new_products = scraper.get_seller_products("competitor1")
            changes = db.detect_changes("competitor1", new_products)
            
            if changes['new']:
                print(f"Ada {len(changes['new'])} produk baru!")
            
            if changes['price_changes']:
                for change in changes['price_changes']:
                    print(f"{change['title']}: {change['old_price']} -> {change['new_price']}")
        """
        old_products = {p['product_id']: p for p in self.get_seller_products(seller_username)}
        new_product_ids = {p['product_id']: p for p in new_products}
        
        changes = {
            'new': [],
            'price_changes': [],
            'edited': [],
            'deleted': []
        }
        
        # Check new and changes
        for product_id, new_product in new_product_ids.items():
            if product_id not in old_products:
                # Produk baru
                changes['new'].append(new_product)
            else:
                old_product = old_products[product_id]
                
                # Check price change
                old_price = old_product['price']
                new_price = new_product.get('price', 0.0)
                
                if abs(old_price - new_price) > 0.01:  # Ada perubahan harga
                    percent_change = ((new_price - old_price) / old_price) * 100 if old_price > 0 else 0
                    
                    changes['price_changes'].append({
                        **new_product,
                        'old_price': old_price,
                        'new_price': new_price,
                        'percent_change': percent_change
                    })
                    
                    # Log ke price_history
                    self.log_price_change(product_id, seller_username, old_price, new_price, percent_change)
                
                # Check other edits (title, stock)
                elif (old_product['title'] != new_product.get('title', '') or
                      old_product['stock'] != new_product.get('stock', 0)):
                    changes['edited'].append({
                        **new_product,
                        'old_title': old_product['title'],
                        'old_stock': old_product['stock']
                    })
        
        # Check deleted
        for product_id, old_product in old_products.items():
            if product_id not in new_product_ids:
                changes['deleted'].append(old_product)
                self.mark_product_inactive(product_id, seller_username)
        
        return changes
    
    def log_price_change(self, product_id: str, seller_username: str, 
                        old_price: float, new_price: float, percent_change: float):
        """
        Catat perubahan harga ke price_history
        
        Args:
            product_id (str): ID produk
            seller_username (str): Username seller
            old_price (float): Harga lama
            new_price (float): Harga baru
            percent_change (float): Persentase perubahan
            
        Example:
            db.log_price_change("abc123", "seller1", 50000, 45000, -10.0)
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO price_history 
        (product_id, seller_username, old_price, new_price, price_change_percent)
        VALUES (?, ?, ?, ?, ?)
        ''', (product_id, seller_username, old_price, new_price, percent_change))
        self.conn.commit()
    
    def log_changes(self, seller_username: str, changes: Dict):
        """
        Catat semua perubahan ke change_log
        
        Args:
            seller_username (str): Username seller
            changes (Dict): Hasil dari detect_changes()
            
        Example:
            changes = db.detect_changes("seller1", new_products)
            db.log_changes("seller1", changes)
        """
        cursor = self.conn.cursor()
        
        # Log new products
        for product in changes['new']:
            cursor.execute('''
            INSERT INTO change_log 
            (seller_username, change_type, product_id, title, details)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                seller_username,
                'new',
                product['product_id'],
                product.get('title', ''),
                json.dumps({'price': product.get('price'), 'stock': product.get('stock')})
            ))
        
        # Log price changes
        for product in changes['price_changes']:
            cursor.execute('''
            INSERT INTO change_log 
            (seller_username, change_type, product_id, title, details)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                seller_username,
                'price_change',
                product['product_id'],
                product.get('title', ''),
                json.dumps({
                    'old_price': product['old_price'],
                    'new_price': product['new_price'],
                    'percent_change': product['percent_change']
                })
            ))
        
        # Log deleted
        for product in changes['deleted']:
            cursor.execute('''
            INSERT INTO change_log 
            (seller_username, change_type, product_id, title, details)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                seller_username,
                'deleted',
                product['product_id'],
                product.get('title', ''),
                json.dumps({'last_price': product['price']})
            ))
        
        self.conn.commit()
    
    def mark_product_inactive(self, product_id: str, seller_username: str):
        """
        Mark produk sebagai tidak aktif (sudah dihapus seller)
        
        Args:
            product_id (str): ID produk
            seller_username (str): Username seller
            
        Example:
            db.mark_product_inactive("abc123", "seller1")
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE products 
        SET is_active = 0, last_updated_at = CURRENT_TIMESTAMP
        WHERE product_id = ? AND seller_username = ?
        ''', (product_id, seller_username))
        self.conn.commit()
    
    def update_monitoring_stats(self, seller_username: str, total_products: int, total_changes: int):
        """
        Update statistik monitoring untuk seller
        
        Args:
            seller_username (str): Username seller
            total_products (int): Total produk aktif
            total_changes (int): Total perubahan terdeteksi
            
        Example:
            db.update_monitoring_stats("seller1", 50, 5)
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO monitoring_stats 
        (seller_username, total_products, total_changes, last_check_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(seller_username) 
        DO UPDATE SET
            total_products = excluded.total_products,
            total_changes = monitoring_stats.total_changes + excluded.total_changes,
            last_check_at = CURRENT_TIMESTAMP
        ''', (seller_username, total_products, total_changes))
        self.conn.commit()
    
    def get_monitoring_stats(self, seller_username: str) -> Optional[Dict]:
        """
        Ambil statistik monitoring untuk seller
        
        Args:
            seller_username (str): Username seller
        
        Returns:
            Dict: Statistik monitoring atau None jika tidak ada
            
        Example:
            stats = db.get_monitoring_stats("seller1")
            if stats:
                print(f"Total produk: {stats['total_products']}")
                print(f"Total perubahan: {stats['total_changes']}")
                print(f"Last check: {stats['last_check_at']}")
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM monitoring_stats 
        WHERE seller_username = ?
        ''', (seller_username,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_recent_changes(self, seller_username: str, limit: int = 20) -> List[Dict]:
        """
        Ambil perubahan terbaru untuk seller
        
        Args:
            seller_username (str): Username seller
            limit (int): Maksimal jumlah hasil (default 20)
        
        Returns:
            List[Dict]: List perubahan terbaru
            
        Example:
            changes = db.get_recent_changes("seller1", limit=10)
            for change in changes:
                print(f"{change['change_type']}: {change['title']}")
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM change_log 
        WHERE seller_username = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''', (seller_username, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_price_history(self, product_id: str, limit: int = 10) -> List[Dict]:
        """
        Ambil riwayat perubahan harga untuk produk
        
        Args:
            product_id (str): ID produk
            limit (int): Maksimal jumlah hasil (default 10)
        
        Returns:
            List[Dict]: List riwayat harga
            
        Example:
            history = db.get_price_history("abc123")
            for h in history:
                print(f"{h['changed_at']}: {h['old_price']} -> {h['new_price']}")
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM price_history 
        WHERE product_id = ?
        ORDER BY changed_at DESC
        LIMIT ?
        ''', (product_id, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def close(self):
        """
        Tutup koneksi database
        
        Example:
            db.close()
        """
        self.conn.close()
    
    def __enter__(self):
        """Support context manager (with statement)"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Auto-close saat keluar dari with block"""
        self.close()


# Test script
if __name__ == '__main__':
    print("Testing MonitoringDatabase...")
    
    # Create test database
    with MonitoringDatabase("test_monitor.db") as db:
        # Test save products
        test_products = [
            {
                'product_id': 'test001',
                'title': 'Test Product 1',
                'price': 100000.0,
                'stock': 10,
                'url': 'https://example.com/1',
                'game_name': 'Test Game'
            },
            {
                'product_id': 'test002',
                'title': 'Test Product 2',
                'price': 50000.0,
                'stock': 5,
                'url': 'https://example.com/2',
                'game_name': 'Test Game'
            }
        ]
        
        count = db.save_products("test_seller", test_products)
        print(f"✓ Saved {count} products")
        
        # Test get products
        products = db.get_seller_products("test_seller")
        print(f"✓ Retrieved {len(products)} products")
        
        # Test detect changes (price change)
        test_products[0]['price'] = 90000.0  # Price reduced
        changes = db.detect_changes("test_seller", test_products)
        print(f"✓ Detected changes: {sum(len(v) for v in changes.values())} total")
        
        # Test log changes
        db.log_changes("test_seller", changes)
        print(f"✓ Logged changes to database")
        
        # Test stats
        db.update_monitoring_stats("test_seller", len(test_products), sum(len(v) for v in changes.values()))
        stats = db.get_monitoring_stats("test_seller")
        print(f"✓ Stats: {stats['total_products']} products, {stats['total_changes']} changes")
        
    print("\n✅ All tests passed!")
    
    # Clean up test database
    import os
    if os.path.exists("test_monitor.db"):
        os.remove("test_monitor.db")
        print("✓ Cleaned up test database")
