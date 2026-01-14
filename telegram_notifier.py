#!/usr/bin/env python3
"""
Telegram Notifier Utility
Sends notifications to Telegram bot for monitoring and alerts
"""

import os
import asyncio
from typing import Optional
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError


class TelegramNotifier:
    """Telegram notification handler for Eldorado Automation"""
    
    def __init__(self):
        """Initialize Telegram bot with credentials from environment"""
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = os.getenv('ENABLE_TELEGRAM_NOTIFICATIONS', 'true').lower() == 'true'
        
        if self.enabled and (not self.bot_token or not self.chat_id):
            print("⚠️ WARNING: Telegram notifications enabled but credentials missing!")
            print("   Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file")
            self.enabled = False
        
        self.bot = Bot(token=self.bot_token) if self.bot_token else None
    
    async def _send_message_async(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send message asynchronously"""
        if not self.enabled or not self.bot:
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            print(f"❌ Telegram send failed: {e}")
            return False
    
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Send message to Telegram (synchronous wrapper)
        
        Args:
            message: Message text (supports HTML formatting)
            parse_mode: 'HTML' or 'Markdown'
        
        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._send_message_async(message, parse_mode))
            loop.close()
            return result
        except Exception as e:
            print(f"❌ Telegram notification error: {e}")
            return False
    
    def notify_start(self, script_name: str) -> bool:
        """Notify automation start"""
        message = (
            f"🚀 <b>Eldorado Automation Started</b>\n\n"
            f"📋 Script: <code>{script_name}</code>\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🖥️ Status: Running"
        )
        return self.send_message(message)
    
    def notify_success(self, script_name: str, details: str = "") -> bool:
        """Notify successful completion"""
        message = (
            f"✅ <b>Success: {script_name}</b>\n\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        if details:
            message += f"\n📊 Details:\n{details}"
        return self.send_message(message)
    
    def notify_error(self, script_name: str, error: str) -> bool:
        """Notify error occurred"""
        message = (
            f"❌ <b>Error: {script_name}</b>\n\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🔴 Error: <code>{error}</code>"
        )
        return self.send_message(message)
    
    def notify_scraping_complete(self, seller: str, count: int) -> bool:
        """Notify scraping completion"""
        message = (
            f"🕷️ <b>Scraping Complete</b>\n\n"
            f"👤 Seller: <code>{seller}</code>\n"
            f"📦 Items found: <b>{count}</b>\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return self.send_message(message)
    
    def notify_upload_complete(self, success: int, failed: int) -> bool:
        """Notify upload completion"""
        status = "✅ Success" if failed == 0 else "⚠️ Partial Success"
        message = (
            f"📤 <b>Upload Complete</b>\n\n"
            f"📊 Status: {status}\n"
            f"✅ Successful: <b>{success}</b>\n"
            f"❌ Failed: <b>{failed}</b>\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return self.send_message(message)
    
    def notify_price_change(self, item_name: str, old_price: float, new_price: float) -> bool:
        """Notify price change detected"""
        change = new_price - old_price
        change_percent = (change / old_price) * 100
        emoji = "📈" if change > 0 else "📉"
        
        message = (
            f"{emoji} <b>Price Change Detected!</b>\n\n"
            f"🎮 Item: <code>{item_name}</code>\n"
            f"💰 Old Price: <b>${old_price:.2f}</b>\n"
            f"💵 New Price: <b>${new_price:.2f}</b>\n"
            f"📊 Change: <b>{change:+.2f}</b> ({change_percent:+.1f}%)\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return self.send_message(message)
    
    def notify_monitoring_summary(self, checked: int, changes: int, errors: int) -> bool:
        """Notify monitoring cycle summary"""
        message = (
            f"🔍 <b>Monitoring Summary</b>\n\n"
            f"📋 Items checked: <b>{checked}</b>\n"
            f"🔄 Changes detected: <b>{changes}</b>\n"
            f"❌ Errors: <b>{errors}</b>\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return self.send_message(message)
    
    def notify_custom(self, title: str, details: dict) -> bool:
        """Send custom notification with details"""
        message = f"📢 <b>{title}</b>\n\n"
        for key, value in details.items():
            message += f"{key}: <b>{value}</b>\n"
        message += f"\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return self.send_message(message)


# Global instance (singleton pattern)
_notifier_instance = None

def get_notifier() -> TelegramNotifier:
    """Get global TelegramNotifier instance"""
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = TelegramNotifier()
    return _notifier_instance


# Quick access functions
def notify_start(script_name: str) -> bool:
    """Quick function to notify start"""
    return get_notifier().notify_start(script_name)

def notify_success(script_name: str, details: str = "") -> bool:
    """Quick function to notify success"""
    return get_notifier().notify_success(script_name, details)

def notify_error(script_name: str, error: str) -> bool:
    """Quick function to notify error"""
    return get_notifier().notify_error(script_name, error)


# Example usage
if __name__ == "__main__":
    # Load .env if running directly
    from dotenv import load_dotenv
    load_dotenv()
    
    notifier = TelegramNotifier()
    
    if notifier.enabled:
        print("✅ Telegram notifier initialized successfully!")
        print(f"📱 Bot Token: {notifier.bot_token[:10]}...")
        print(f"💬 Chat ID: {notifier.chat_id}")
        
        # Test notification
        print("\n🧪 Sending test notification...")
        if notifier.send_message("🧪 <b>Test Notification</b>\n\nEldorado Automation is ready! ✅"):
            print("✅ Test notification sent successfully!")
        else:
            print("❌ Failed to send test notification")
    else:
        print("⚠️ Telegram notifications disabled or not configured")
        print("\nTo enable Telegram notifications:")
        print("1. Create a Telegram bot via @BotFather")
        print("2. Get your chat_id via @userinfobot")
        print("3. Add to .env file:")
        print("   TELEGRAM_BOT_TOKEN=your_bot_token")
        print("   TELEGRAM_CHAT_ID=your_chat_id")
        print("   ENABLE_TELEGRAM_NOTIFICATIONS=true")
