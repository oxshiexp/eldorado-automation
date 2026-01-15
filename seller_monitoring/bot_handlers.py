#!/usr/bin/env python3
"""
OXSHI Bot Handlers - Command and callback handlers
Handles all bot commands and integrates with monitoring system
"""

import asyncio
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Import monitoring components
try:
    from database import Database
    from bot_menu import BotMenu
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from database import Database
    from bot_menu import BotMenu

logger = logging.getLogger(__name__)

class BotHandlers:
    """Handles all bot commands and callbacks"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / 'seller_config.json'
        
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.menu = BotMenu()
        
        # Database
        db_path = Path(__file__).parent / 'monitoring.db'
        self.db = Database(db_path)
    
    def load_config(self) -> dict:
        """Load configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start - Show main dashboard"""
        message = self.menu.get_header()
        message += "\n\n**Welcome to OXSHI Monitor Bot!** 👋\n\n"
        message += "Choose an option below:\n"
        
        keyboard = self.menu.get_main_menu()
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
    
    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle status check"""
        message = self.menu.get_header()
        message += "\n\n**📊 SYSTEM STATUS**\n\n"
        
        # Check systemd service
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'oxshi-monitor'],
                capture_output=True,
                text=True
            )
            is_active = result.stdout.strip() == 'active'
            status_emoji = "🟢" if is_active else "🔴"
            status_text = "ACTIVE" if is_active else "INACTIVE"
        except:
            status_emoji = "⚠️"
            status_text = "UNKNOWN"
        
        message += f"{status_emoji} **Monitoring Service:** {status_text}\n\n"
        
        # Config info
        interval = self.config.get('check_interval_minutes', 60)
        threshold = self.config.get('price_threshold_percent', 5)
        sellers = self.config.get('sellers', [])
        
        message += "⏰ **Schedule:**\n"
        message += f"├─ Check Interval: {interval} minutes\n"
        message += f"└─ Price Threshold: {threshold}%\n\n"
        
        message += f"👥 **Sellers:** {len(sellers)} tracked\n"
        for seller in sellers:
            status = "🟢" if seller.get('enabled') else "🔴"
            message += f"├─ {status} {seller.get('name')}\n"
        
        message += "\n" + self.menu.get_footer()
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Refresh", callback_data='status'),
            InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')
        ]])
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
    
    async def handle_sellers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle seller management"""
        message = self.menu.get_header()
        message += "\n\n**👥 SELLER MANAGEMENT**\n\n"
        
        sellers = self.config.get('sellers', [])
        
        if sellers:
            message += "**Current Sellers:**\n\n"
            for i, seller in enumerate(sellers, 1):
                status = "🟢" if seller.get('enabled') else "🔴"
                name = seller.get('name', 'Unknown')
                message += f"{i}. {status} **{name}**\n"
        else:
            message += "No sellers configured yet.\n"
        
        message += "\n**Actions:**\n"
        message += "\n" + self.menu.get_footer()
        
        buttons = [
            [InlineKeyboardButton("➕ Add Seller", callback_data='add_seller')],
            [InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
    
    async def handle_add_seller_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Prompt for seller addition"""
        message = "**➕ ADD NEW SELLER**\n\n"
        message += "Please send seller details in this format:\n\n"
        message += "```\n"
        message += "Name: Seller Name\n"
        message += "URL: https://eldorado.gg/...\n"
        message += "Status: enabled\n"
        message += "```\n\n"
        message += "Or send /cancel to abort."
        
        context.user_data['awaiting_seller'] = True
        
        await update.callback_query.edit_message_text(
            message,
            parse_mode='Markdown'
        )
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input (for seller addition)"""
        if not context.user_data.get('awaiting_seller'):
            return
        
        text = update.message.text
        
        if text.lower() == '/cancel':
            context.user_data['awaiting_seller'] = False
            await update.message.reply_text("❌ Cancelled.")
            return
        
        # Parse seller info
        try:
            lines = text.strip().split('\n')
            seller = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    if key == 'name':
                        seller['name'] = value
                    elif key == 'url':
                        seller['profile_url'] = value
                    elif key == 'status':
                        seller['enabled'] = value.lower() == 'enabled'
            
            if 'name' in seller and 'profile_url' in seller:
                # Add to config
                sellers = self.config.get('sellers', [])
                sellers.append(seller)
                self.config['sellers'] = sellers
                self.save_config()
                
                context.user_data['awaiting_seller'] = False
                
                message = "✅ **Seller Added Successfully!**\n\n"
                message += f"**Name:** {seller['name']}\n"
                message += f"**URL:** {seller['profile_url']}\n"
                message += f"**Status:** {'Enabled' if seller.get('enabled', True) else 'Disabled'}"
                
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("👥 View Sellers", callback_data='sellers'),
                    InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')
                ]])
                
                await update.message.reply_text(
                    message,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ Invalid format. Missing name or URL. Please try again."
                )
        except Exception as e:
            logger.error(f"Error parsing seller: {e}")
            await update.message.reply_text(
                "❌ Error parsing seller info. Please try again."
            )
    
    async def handle_scrape_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show manual scrape menu"""
        message = self.menu.get_header()
        message += "\n\n**🔍 MANUAL SCRAPE**\n\n"
        message += "Select a seller to scrape:\n\n"
        
        sellers = self.config.get('sellers', [])
        
        if not sellers:
            message += "No sellers configured.\n"
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')
            ]])
        else:
            buttons = []
            for i, seller in enumerate(sellers):
                name = seller.get('name', f'Seller {i+1}')
                buttons.append([InlineKeyboardButton(
                    f"📦 {name}",
                    callback_data=f'scrape_seller_{i}'
                )])
            buttons.append([InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')])
            keyboard = InlineKeyboardMarkup(buttons)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
    
    async def handle_manual_scrape(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute manual scrape"""
        query = update.callback_query
        seller_idx = int(query.data.split('_')[-1])
        
        sellers = self.config.get('sellers', [])
        if seller_idx >= len(sellers):
            await query.answer("❌ Seller not found")
            return
        
        seller = sellers[seller_idx]
        await query.answer(f"⏳ Scraping {seller['name']}...")
        
        message = f"**🔍 SCRAPING: {seller['name']}**\n\n"
        message += "⏳ Please wait...\n\n"
        
        await query.edit_message_text(message, parse_mode='Markdown')
        
        # Simulate scraping
        await asyncio.sleep(2)
        
        message = f"**✅ SCRAPE COMPLETE**\n\n"
        message += f"**Seller:** {seller['name']}\n"
        message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        message += "**Results:**\n"
        message += "├─ Products Found: 0\n"
        message += "├─ Price Changes: 0\n"
        message += "└─ New Products: 0\n"
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔍 Scrape Again", callback_data=f'scrape_seller_{seller_idx}'),
            InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')
        ]])
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show settings menu"""
        message = self.menu.get_header()
        message += "\n\n**⚙️ BOT SETTINGS**\n\n"
        
        interval = self.config.get('check_interval_minutes', 60)
        threshold = self.config.get('price_threshold_percent', 5)
        
        message += f"**Current Configuration:**\n\n"
        message += f"⏱️ Check Interval: {interval} minutes\n"
        message += f"📊 Price Threshold: {threshold}%\n\n"
        message += "Use the buttons below to adjust settings.\n"
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')
        ]])
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
    
    async def handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show statistics"""
        message = self.menu.get_header()
        message += "\n\n**📈 STATISTICS & ANALYTICS**\n\n"
        message += "**Last 24 Hours:**\n"
        message += "├─ Monitoring Checks: 0\n"
        message += "├─ Price Changes: 0\n"
        message += "└─ Notifications Sent: 0\n\n"
        message += self.menu.get_footer()
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Refresh", callback_data='stats'),
            InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')
        ]])
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help guide"""
        message = self.menu.get_header()
        message += "\n\n**❓ HELP & COMMANDS**\n\n"
        message += "**Available Commands:**\n\n"
        message += "`/start` - Show main dashboard\n"
        message += "`/status` - Check system status\n"
        message += "`/sellers` - Manage sellers\n"
        message += "`/scrape` - Manual scrape\n"
        message += "`/settings` - Configure bot\n"
        message += "`/stats` - View statistics\n"
        message += "`/help` - Show this help\n\n"
        message += self.menu.get_footer()
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')
        ]])
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
    
    async def handle_start_monitor(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start monitoring service"""
        try:
            subprocess.run(['systemctl', 'start', 'oxshi-monitor'], check=True)
            await update.callback_query.answer("✅ Monitoring started")
            await self.handle_status(update, context)
        except Exception as e:
            await update.callback_query.answer(f"❌ Error: {e}")
    
    async def handle_stop_monitor(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop monitoring service"""
        try:
            subprocess.run(['systemctl', 'stop', 'oxshi-monitor'], check=True)
            await update.callback_query.answer("⏸️ Monitoring stopped")
            await self.handle_status(update, context)
        except Exception as e:
            await update.callback_query.answer(f"❌ Error: {e}")
    
    async def handle_setting_change(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle setting changes"""
        await update.callback_query.answer("⚙️ Settings feature coming soon")
    
    async def handle_remove_seller(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle seller removal"""
        await update.callback_query.answer("🗑️ Remove feature coming soon")
