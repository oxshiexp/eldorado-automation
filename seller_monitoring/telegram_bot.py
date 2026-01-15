#!/usr/bin/env python3
"""
OXSHI Telegram Bot - Interactive Control Dashboard
Provides user-friendly menu interface for monitoring system control
"""

import json
import logging
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Import handlers
try:
    from bot_handlers import BotHandlers
    from bot_menu import BotMenu
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from bot_handlers import BotHandlers
    from bot_menu import BotMenu

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class OxshiBot:
    """Main Telegram Bot class"""
    
    def __init__(self, config_path: str = None):
        """Initialize bot with configuration"""
        if config_path is None:
            config_path = Path(__file__).parent / 'seller_config.json'
        
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.handlers = BotHandlers(config_path)
        self.menu = BotMenu()
        
    def load_config(self) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config: {e}")
            raise
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - Show main dashboard"""
        await self.handlers.start_command(update, context)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - Show system status"""
        await self.handlers.handle_status(update, context)
    
    async def sellers_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sellers command - Seller management"""
        await self.handlers.handle_sellers(update, context)
    
    async def scrape_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scrape command - Manual scraping"""
        await self.handlers.handle_scrape_menu(update, context)
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command - Bot settings"""
        await self.handlers.handle_settings(update, context)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command - Statistics"""
        await self.handlers.handle_stats(update, context)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command - Help guide"""
        await self.handlers.handle_help(update, context)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        # Route to appropriate handler
        if callback_data == 'main_menu':
            await self.handlers.start_command(update, context)
        elif callback_data == 'status':
            await self.handlers.handle_status(update, context)
        elif callback_data == 'sellers':
            await self.handlers.handle_sellers(update, context)
        elif callback_data == 'scrape':
            await self.handlers.handle_scrape_menu(update, context)
        elif callback_data == 'settings':
            await self.handlers.handle_settings(update, context)
        elif callback_data == 'stats':
            await self.handlers.handle_stats(update, context)
        elif callback_data == 'help':
            await self.handlers.handle_help(update, context)
        elif callback_data.startswith('scrape_seller_'):
            await self.handlers.handle_manual_scrape(update, context)
        elif callback_data == 'add_seller':
            await self.handlers.handle_add_seller_prompt(update, context)
        elif callback_data.startswith('remove_seller_'):
            await self.handlers.handle_remove_seller(update, context)
        elif callback_data == 'start_monitor':
            await self.handlers.handle_start_monitor(update, context)
        elif callback_data == 'stop_monitor':
            await self.handlers.handle_stop_monitor(update, context)
        elif callback_data.startswith('setting_'):
            await self.handlers.handle_setting_change(update, context)
    
    def run(self):
        """Start the bot"""
        token = self.config.get('telegram_bot_token')
        if not token:
            raise ValueError("telegram_bot_token not found in config")
        
        # Create application
        application = Application.builder().token(token).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("sellers", self.sellers_command))
        application.add_handler(CommandHandler("scrape", self.scrape_command))
        application.add_handler(CommandHandler("settings", self.settings_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("help", self.help_command))
        
        # Add button callback handler
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Add message handler for seller addition
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handlers.handle_text_input
        ))
        
        # Log startup
        logger.info("🤖 OXSHI Telegram Bot starting...")
        logger.info(f"📝 Config loaded from: {self.config_path}")
        logger.info("✅ Bot is running! Press Ctrl+C to stop.")
        
        # Start polling
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    try:
        bot = OxshiBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        raise


if __name__ == '__main__':
    main()
