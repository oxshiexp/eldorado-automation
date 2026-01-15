#!/usr/bin/env python3
"""
OXSHI Bot Menu - Menu layouts and keyboard structures
Defines all menu layouts for the Telegram bot interface
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class BotMenu:
    """Handles menu layouts and keyboard structures"""
    
    @staticmethod
    def get_header() -> str:
        """Get formatted header for messages"""
        header = "═" * 39 + "\n"
        header += "🔔 **OXSHI PRICE MONITOR** 🔔\n"
        header += "*Automated Trading Monitor*\n"
        header += "═" * 39
        return header
    
    @staticmethod
    def get_footer() -> str:
        """Get formatted footer for messages"""
        footer = "─" * 37 + "\n"
        footer += "⚡ *Powered by OXSHI Monitor Bot v1.0*\n"
        footer += "   github.com/oxshiexp"
        return footer
    
    @staticmethod
    def get_main_menu() -> InlineKeyboardMarkup:
        """Get main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📊 System Status", callback_data='status'),
                InlineKeyboardButton("⚙️ Settings", callback_data='settings')
            ],
            [
                InlineKeyboardButton("👥 Manage Sellers", callback_data='sellers'),
                InlineKeyboardButton("🔍 Manual Scrape", callback_data='scrape')
            ],
            [
                InlineKeyboardButton("▶️ Start Monitor", callback_data='start_monitor'),
                InlineKeyboardButton("⏸️ Stop Monitor", callback_data='stop_monitor')
            ],
            [
                InlineKeyboardButton("📈 Statistics", callback_data='stats'),
                InlineKeyboardButton("❓ Help", callback_data='help')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_button() -> InlineKeyboardMarkup:
        """Get simple back to main menu button"""
        keyboard = [[
            InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')
        ]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_refresh_menu_buttons() -> InlineKeyboardMarkup:
        """Get refresh and back buttons"""
        keyboard = [[
            InlineKeyboardButton("🔄 Refresh", callback_data='status'),
            InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')
        ]]
        return InlineKeyboardMarkup(keyboard)
