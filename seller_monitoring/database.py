"""
Eldorado Seller Monitoring - Database Handler
==============================================

Manages SQLite database for product tracking and change history.

Features:
- Product storage with history
- Price change tracking
- Change log for notifications
- Statistics and reporting

Usage:
    from database import MonitoringDatabase
    
    db = MonitoringDatabase()
    db.add_product("seller1", product_data)
    changes = db.update_product("prod_123", new_data)
    db.close()

Author: Nebula AI
Date: 2024-01-15
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os


class MonitoringDatabase:
    """
    SQLite database handler for seller monitoring.
    
    Methods:
        - create_tables(): Initialize database schema
        - add_product(): Add new product
        - update_product(): Update and detect changes
        - mark_product_deleted(): Mark product as inactive
        - get_seller_products(): Get all seller products
        - log_change(): Log changes for notification
        - get_unnotified_changes(): Get pending notifications
        - mark_changes_notified(): Mark as sent
        - get_stats(): Get monitoring statistics
    """
    
    def __init__(self, db_path: str = "seller_monitoring/monitor.db"):
        """
        Initialize database connection and create tables.
        
        Args:
            db_path (str): Path to SQLite database file
        
        Example:
            db = MonitoringDatabase("monitoring.db")
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """
        Create database tables if they don't exist.
        
        Tables:
        - products: Current product snapshots
        - price_history: Historical price changes
        - change_log: All changes for notifications
        
        Indexes:
        - product_id, seller_username, is_active, notified
        """
        cursor = self.conn.cursor()
        
        # Products table - current snapshot
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_username TEXT NOT NULL,
                product_id TEXT NOT NULL UNIQUE,
                title TEXT,
                price REAL,
                stock INTEGER,
                description TEXT,
                category TEXT,
                image_url TEXT,
                url TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Price history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                old_price REAL,
                new_price REAL,
                price_change_percent REAL,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        """)
        
        # Change log table - all changes for notification
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS change_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_username TEXT NOT NULL,
                product_id TEXT,
                change_type TEXT NOT NULL,
                details TEXT,
                notified BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_id ON products(product_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_seller ON products(seller_username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_active ON products(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_change_notified ON change_log(notified)")
        
        self.conn.commit()
    
    def add_product(self, seller: str, product_data: Dict) -> bool:
        """
        Add new product to database.
        
        Args:
            seller (str): Seller username
            product_data (dict): Product information
                Required: product_id
                Optional: title, price, stock, description, category, image_url, url
        
        Returns:
            bool: True if added successfully, False if duplicate
        
        Example:
            success = db.add_product("seller1", {
                "product_id": "prod_123",
                "title": "Valorant 100 VP",
                "price": 15000,
                "stock": 999
            })
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO products (
                    seller_username, product_id, title, price, stock,
                    description, category, image_url, url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                seller,
                product_data['product_id'],
                product_data.get('title'),
                product_data.get('price'),
                product_data.get('stock'),
                product_data.get('description'),
                product_data.get('category'),
                product_data.get('image_url'),
                product_data.get('url')
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error adding product: {e}")
            return False
    
    def update_product(self, product_id: str, product_data: Dict) -> Dict[str, any]:
        """
        Update existing product and detect changes.
        
        Args:
            product_id (str): Product ID to update
            product_data (dict): New product data
        
        Returns:
            dict: {
                'changed': bool,
                'changes': List of changes detected,
                'product': Old product data
            }
        
        Example:
            result = db.update_product("prod_123", {
                "price": 12000,  # Changed from 15000
                "title": "Valorant 100 VP"
            })
            
            if result['changed']:
                for change in result['changes']:
                    print(f"{change['field']}: {change['old']} -> {change['new']}")
        """
        cursor = self.conn.cursor()
        
        # Get current product data
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        old_data = cursor.fetchone()
        
        if not old_data:
            return {'changed': False, 'changes': []}
        
        changes = []
        
        # Check price change
        old_price = old_data['price']
        new_price = product_data.get('price')
        if old_price and new_price and old_price != new_price:
            price_change = ((new_price - old_price) / old_price) * 100
            changes.append({
                'type': 'price',
                'field': 'price',
                'old': old_price,
                'new': new_price,
                'percent': round(price_change, 2)
            })
            
            # Log price history
            cursor.execute("""
                INSERT INTO price_history (product_id, old_price, new_price, price_change_percent)
                VALUES (?, ?, ?, ?)
            """, (product_id, old_price, new_price, round(price_change, 2)))
        
        # Check other field changes
        fields_to_check = ['title', 'description', 'stock', 'category', 'image_url']
        for field in fields_to_check:
            old_value = old_data[field]
            new_value = product_data.get(field)
            if new_value and old_value != new_value:
                changes.append({
                    'type': 'edit',
                    'field': field,
                    'old': old_value,
                    'new': new_value
                })
        
        # Update product in database
        cursor.execute("""
            UPDATE products 
            SET title = ?, price = ?, stock = ?, description = ?,
                category = ?, image_url = ?, last_checked = CURRENT_TIMESTAMP
            WHERE product_id = ?
        """, (
            product_data.get('title'),
            product_data.get('price'),
            product_data.get('stock'),
            product_data.get('description'),
            product_data.get('category'),
            product_data.get('image_url'),
            product_id
        ))
        
        self.conn.commit()
        
        return {
            'changed': len(changes) > 0,
            'changes': changes,
            'product': dict(old_data)
        }
    
    def mark_product_deleted(self, product_id: str) -> Optional[Dict]:
        """
        Mark product as deleted (inactive).
        
        Args:
            product_id (str): Product ID
        
        Returns:
            dict or None: Product data if marked deleted, None otherwise
        
        Example:
            deleted = db.mark_product_deleted("prod_123")
            if deleted:
                print(f"Product {deleted['title']} was deleted")
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        product = cursor.fetchone()
        
        if product and product['is_active']:
            cursor.execute("""
                UPDATE products SET is_active = 0, last_checked = CURRENT_TIMESTAMP
                WHERE product_id = ?
            """, (product_id,))
            self.conn.commit()
            return dict(product)
        return None
    
    def get_seller_products(self, seller: str, active_only: bool = True) -> List[Dict]:
        """
        Get all products for a seller.
        
        Args:
            seller (str): Seller username
            active_only (bool): If True, only return active products
        
        Returns:
            List[dict]: List of product dictionaries
        
        Example:
            products = db.get_seller_products("competitor1")
            print(f"Found {len(products)} products")
        """
        cursor = self.conn.cursor()
        query = "SELECT * FROM products WHERE seller_username = ?"
        params = [seller]
        
        if active_only:
            query += " AND is_active = 1"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def log_change(self, seller: str, product_id: str, change_type: str, 
                   details: Dict, notified: bool = False):
        """
        Log a change to change_log table.
        
        Args:
            seller (str): Seller username
            product_id (str): Product ID
            change_type (str): Type of change (new, price, edit, delete)
            details (dict): Change details
            notified (bool): Whether notification was sent
        
        Example:
            db.log_change("seller1", "prod_123", "price", {
                "old": 15000,
                "new": 12000,
                "percent": -20
            })
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO change_log (seller_username, product_id, change_type, details, notified)
            VALUES (?, ?, ?, ?, ?)
        """, (seller, product_id, change_type, json.dumps(details), notified))
        self.conn.commit()
    
    def get_unnotified_changes(self) -> List[Dict]:
        """
        Get all changes that haven't been notified yet.
        
        Returns:
            List[dict]: List of unnotified changes
        
        Example:
            changes = db.get_unnotified_changes()
            for change in changes:
                send_notification(change)
            db.mark_changes_notified([c['id'] for c in changes])
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM change_log 
            WHERE notified = 0 
            ORDER BY timestamp ASC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_changes_notified(self, change_ids: List[int]):
        """
        Mark changes as notified.
        
        Args:
            change_ids (List[int]): List of change log IDs
        
        Example:
            db.mark_changes_notified([1, 2, 3])
        """
        if not change_ids:
            return
        
        cursor = self.conn.cursor()
        placeholders = ','.join('?' * len(change_ids))
        cursor.execute(f"""
            UPDATE change_log 
            SET notified = 1 
            WHERE id IN ({placeholders})
        """, change_ids)
        self.conn.commit()
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """
        Get single product by ID.
        
        Args:
            product_id (str): Product ID
        
        Returns:
            dict or None: Product data or None if not found
        
        Example:
            product = db.get_product("prod_123")
            if product:
                print(product['title'], product['price'])
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_price_history(self, product_id: str, limit: int = 10) -> List[Dict]:
        """
        Get price history for a product.
        
        Args:
            product_id (str): Product ID
            limit (int): Maximum number of records
        
        Returns:
            List[dict]: Price history records
        
        Example:
            history = db.get_price_history("prod_123")
            for h in history:
                print(f"{h['changed_at']}: {h['old_price']} -> {h['new_price']}")
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM price_history 
            WHERE product_id = ? 
            ORDER BY changed_at DESC 
            LIMIT ?
        """, (product_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self, seller: str = None) -> Dict:
        """
        Get statistics about monitored products.
        
        Args:
            seller (str, optional): Specific seller or all sellers
        
        Returns:
            dict: Statistics including:
                - total_products: Total products tracked
                - active_products: Currently active products
                - sellers: Number of sellers monitored
                - changes_today: Changes detected today
        
        Example:
            stats = db.get_stats()
            print(f"Monitoring {stats['active_products']} products")
            print(f"{stats['changes_today']} changes today")
        """
        cursor = self.conn.cursor()
        
        if seller:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_products,
                    COUNT(DISTINCT seller_username) as sellers
                FROM products
                WHERE seller_username = ?
            """, (seller,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_products,
                    COUNT(DISTINCT seller_username) as sellers
                FROM products
            """)
        
        stats = dict(cursor.fetchone())
        
        # Get total changes today
        cursor.execute("""
            SELECT COUNT(*) as changes_today
            FROM change_log
            WHERE date(timestamp) = date('now')
        """)
        stats.update(dict(cursor.fetchone()))
        
        return stats
    
    def close(self):
        """
        Close database connection.
        
        Example:
            db = MonitoringDatabase()
            # ... use database ...
            db.close()
        """
        self.conn.close()
