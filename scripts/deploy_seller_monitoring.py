#!/usr/bin/env python3
"""
🚀 Eldorado Seller Monitoring - Easy Deployment Script
======================================================

Script ini akan setup sistem monitoring seller secara otomatis:
1. ✅ Setup Telegram Bot credentials
2. ✅ Configure sellers untuk monitor
3. ✅ Test scraping
4. ✅ Install systemd service
5. ✅ Start monitoring 24/7

USAGE:
    python3 scripts/deploy_seller_monitoring.py

REQUIREMENTS:
    - Python 3.8+
    - Telegram Bot Token (dari @BotFather)
    - Telegram Chat ID (dari @userinfobot)
    - Root/sudo access untuk install service

Author: Nebula AI
Version: 1.0
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple


# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env"
SELLER_CONFIG = BASE_DIR / "seller_monitoring" / "seller_config.json"
MONITOR_SCRIPT = BASE_DIR / "seller_monitoring" / "seller_monitor.py"
SERVICE_FILE = BASE_DIR / "eldorado-seller-monitor.service"
SYSTEMD_PATH = Path("/etc/systemd/system/eldorado-seller-monitor.service")

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(text: str):
    """Print styled header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")


def print_step(step: int, total: int, text: str):
    """Print step indicator"""
    print(f"{Colors.BOLD}{Colors.BLUE}[Step {step}/{total}]{Colors.ENDC} {text}")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.ENDC} {text}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.ENDC} {text}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.ENDC} {text}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ{Colors.ENDC} {text}")


def get_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input from user"""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    return response in ['y', 'yes', 'ya']


def validate_telegram_token(token: str) -> bool:
    """Validate Telegram bot token format"""
    # Format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
    pattern = r'^\d{8,10}:[A-Za-z0-9_-]{35}$'
    return bool(re.match(pattern, token))


def validate_chat_id(chat_id: str) -> bool:
    """Validate Telegram chat ID format"""
    # Format: positive or negative integer
    return chat_id.lstrip('-').isdigit()


def validate_seller_username(username: str) -> bool:
    """Validate Eldorado seller username"""
    # Username should be alphanumeric with possible hyphens/underscores
    pattern = r'^[a-zA-Z0-9_-]{3,}$'
    return bool(re.match(pattern, username))


# ============================================================================
# SETUP FUNCTIONS
# ============================================================================

def check_prerequisites() -> bool:
    """Check if all required files and directories exist"""
    print_step(1, 6, "Checking prerequisites...")
    
    required_files = [
        MONITOR_SCRIPT,
        SERVICE_FILE,
        BASE_DIR / "requirements.txt"
    ]
    
    required_dirs = [
        BASE_DIR / "seller_monitoring",
        BASE_DIR / "shared"
    ]
    
    all_good = True
    
    # Check files
    for file_path in required_files:
        if file_path.exists():
            print_success(f"Found: {file_path.name}")
        else:
            print_error(f"Missing: {file_path}")
            all_good = False
    
    # Check directories
    for dir_path in required_dirs:
        if dir_path.exists():
            print_success(f"Found directory: {dir_path.name}/")
        else:
            print_error(f"Missing directory: {dir_path}")
            all_good = False
    
    if not all_good:
        print_error("\nMissing required files! Please ensure you're in the correct directory.")
        return False
    
    print_success("All prerequisites met!")
    return True


def setup_telegram_credentials() -> Tuple[str, str]:
    """Setup Telegram bot credentials"""
    print_step(2, 6, "Setup Telegram Bot Credentials")
    
    print_info("\n📱 Telegram Bot Setup:")
    print("   1. Chat dengan @BotFather di Telegram")
    print("   2. Ketik /newbot dan ikuti instruksi")
    print("   3. Copy token yang diberikan (format: 1234567890:ABC...)")
    print("   4. Chat dengan @userinfobot untuk mendapatkan Chat ID")
    print("   5. Copy Chat ID Anda (format: 1234567890)\n")
    
    # Get Bot Token
    while True:
        token = get_input("Enter Telegram Bot Token")
        if validate_telegram_token(token):
            print_success("Valid token format!")
            break
        print_error("Invalid token format! Format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    
    # Get Chat ID
    while True:
        chat_id = get_input("Enter Telegram Chat ID")
        if validate_chat_id(chat_id):
            print_success("Valid chat ID format!")
            break
        print_error("Invalid chat ID! Should be a number (e.g., 1234567890)")
    
    return token, chat_id


def update_env_file(token: str, chat_id: str) -> bool:
    """Update or create .env file with credentials"""
    print_step(3, 6, "Updating .env file...")
    
    try:
        # Read existing .env if exists
        env_content = {}
        if ENV_FILE.exists():
            with open(ENV_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key.strip()] = value.strip()
        
        # Update with new values
        env_content['TELEGRAM_BOT_TOKEN'] = token
        env_content['TELEGRAM_CHAT_ID'] = chat_id
        
        # Write back to file
        with open(ENV_FILE, 'w') as f:
            f.write("# Eldorado Automation - Environment Variables\n")
            f.write("# Generated by deploy_seller_monitoring.py\n\n")
            f.write("# Telegram Bot Configuration\n")
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        print_success(f"Updated {ENV_FILE}")
        return True
        
    except Exception as e:
        print_error(f"Failed to update .env file: {e}")
        return False


def configure_sellers() -> List[Dict]:
    """Configure sellers to monitor"""
    print_step(4, 6, "Configure Sellers to Monitor")
    
    print_info("\n👥 Seller Configuration:")
    print("   Masukkan username seller yang ingin dimonitor")
    print("   Username bisa dilihat di URL: eldorado.gg/sellers/USERNAME\n")
    
    sellers = []
    
    while True:
        print(f"\n{Colors.BOLD}Seller #{len(sellers) + 1}{Colors.ENDC}")
        
        # Get username
        while True:
            username = get_input("Enter seller username (or 'done' to finish)")
            
            if username.lower() == 'done':
                if len(sellers) == 0:
                    print_warning("You must add at least 1 seller!")
                    continue
                return sellers
            
            if validate_seller_username(username):
                print_success(f"Valid username: {username}")
                break
            print_error("Invalid username! Use alphanumeric characters, hyphens, or underscores (min 3 chars)")
        
        # Get notification preferences
        print(f"\n  {Colors.CYAN}Notification settings for {username}:{Colors.ENDC}")
        notify_new = get_yes_no("  Notify new products?", True)
        notify_price = get_yes_no("  Notify price changes?", True)
        notify_edits = get_yes_no("  Notify product edits?", True)
        notify_deletions = get_yes_no("  Notify deletions?", True)
        
        seller_config = {
            "username": username,
            "notify_new_products": notify_new,
            "notify_price_changes": notify_price,
            "notify_edits": notify_edits,
            "notify_deletions": notify_deletions
        }
        
        sellers.append(seller_config)
        print_success(f"Added seller: {username}")
        
        if not get_yes_no("\nAdd another seller?", False):
            break
    
    return sellers


def update_seller_config(sellers: List[Dict]) -> bool:
    """Update seller_config.json file"""
    print("\nUpdating seller configuration...")
    
    try:
        # Get check interval
        print_info("\n⏰ Monitoring Interval:")
        print("   How often to check for changes (5-60 minutes)")
        print("   Recommended: 10-15 minutes for balance between freshness and resources\n")
        
        while True:
            interval = get_input("Check interval in minutes", "10")
            try:
                interval = int(interval)
                if 5 <= interval <= 60:
                    break
                print_error("Interval must be between 5 and 60 minutes")
            except ValueError:
                print_error("Please enter a valid number")
        
        # Create config
        config = {
            "sellers": sellers,
            "check_interval_minutes": interval
        }
        
        # Write to file
        with open(SELLER_CONFIG, 'w') as f:
            json.dump(config, f, indent=2)
        
        print_success(f"Updated {SELLER_CONFIG}")
        print_info(f"Monitoring {len(sellers)} seller(s) every {interval} minutes")
        return True
        
    except Exception as e:
        print_error(f"Failed to update seller config: {e}")
        return False


def install_dependencies() -> bool:
    """Install Python dependencies"""
    print_step(5, 6, "Installing dependencies...")
    
    try:
        print_info("Running: pip3 install -r requirements.txt")
        result = subprocess.run(
            ['pip3', 'install', '-r', str(BASE_DIR / 'requirements.txt')],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        
        if result.returncode == 0:
            print_success("Dependencies installed successfully!")
            return True
        else:
            print_error(f"Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error installing dependencies: {e}")
        return False


def test_monitoring() -> bool:
    """Test the monitoring system"""
    print_step(6, 6, "Testing monitoring system...")
    
    print_info("\nRunning test scrape (this may take 10-30 seconds)...\n")
    
    try:
        # Run a quick test
        result = subprocess.run(
            ['python3', str(MONITOR_SCRIPT), '--test'],
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
            timeout=60
        )
        
        if result.returncode == 0:
            print_success("Test successful!")
            print_info("Output preview:")
            print(result.stdout[:500])
            return True
        else:
            print_warning("Test completed with warnings")
            print_info(result.stderr[:500])
            return get_yes_no("Continue anyway?", True)
            
    except subprocess.TimeoutExpired:
        print_warning("Test took too long, skipping...")
        return get_yes_no("Continue anyway?", True)
    except Exception as e:
        print_error(f"Test failed: {e}")
        return get_yes_no("Continue anyway?", False)


def install_systemd_service() -> bool:
    """Install systemd service for 24/7 monitoring"""
    print_header("Service Installation")
    
    print_info("Installing systemd service for 24/7 monitoring...")
    print_warning("This requires sudo/root privileges\n")
    
    if not get_yes_no("Install systemd service?", True):
        print_info("Skipping service installation. You can run manually with:")
        print(f"  python3 {MONITOR_SCRIPT}")
        return False
    
    try:
        # Copy service file
        print_info(f"Copying service file to {SYSTEMD_PATH}")
        result = subprocess.run(
            ['sudo', 'cp', str(SERVICE_FILE), str(SYSTEMD_PATH)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print_error(f"Failed to copy service file: {result.stderr}")
            return False
        
        print_success("Service file copied")
        
        # Reload systemd
        print_info("Reloading systemd daemon...")
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        print_success("Systemd reloaded")
        
        # Enable service
        print_info("Enabling service (auto-start on boot)...")
        subprocess.run(['sudo', 'systemctl', 'enable', 'eldorado-seller-monitor'], check=True)
        print_success("Service enabled")
        
        # Start service
        if get_yes_no("Start monitoring service now?", True):
            print_info("Starting service...")
            subprocess.run(['sudo', 'systemctl', 'start', 'eldorado-seller-monitor'], check=True)
            print_success("Service started!")
            
            # Show status
            print_info("\nService status:")
            subprocess.run(['sudo', 'systemctl', 'status', 'eldorado-seller-monitor', '--no-pager'])
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install service: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def print_usage_guide():
    """Print usage guide and commands"""
    print_header("🎉 Setup Complete!")
    
    print(f"{Colors.BOLD}Your monitoring system is ready!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}📋 Useful Commands:{Colors.ENDC}\n")
    
    print(f"{Colors.CYAN}Check service status:{Colors.ENDC}")
    print(f"  sudo systemctl status eldorado-seller-monitor\n")
    
    print(f"{Colors.CYAN}View live logs:{Colors.ENDC}")
    print(f"  sudo journalctl -u eldorado-seller-monitor -f\n")
    
    print(f"{Colors.CYAN}Stop monitoring:{Colors.ENDC}")
    print(f"  sudo systemctl stop eldorado-seller-monitor\n")
    
    print(f"{Colors.CYAN}Start monitoring:{Colors.ENDC}")
    print(f"  sudo systemctl start eldorado-seller-monitor\n")
    
    print(f"{Colors.CYAN}Restart monitoring:{Colors.ENDC}")
    print(f"  sudo systemctl restart eldorado-seller-monitor\n")
    
    print(f"{Colors.CYAN}Disable auto-start:{Colors.ENDC}")
    print(f"  sudo systemctl disable eldorado-seller-monitor\n")
    
    print(f"{Colors.CYAN}Manual run (for testing):{Colors.ENDC}")
    print(f"  python3 {MONITOR_SCRIPT}\n")
    
    print(f"{Colors.BOLD}📁 Configuration Files:{Colors.ENDC}\n")
    print(f"  Telegram: {ENV_FILE}")
    print(f"  Sellers:  {SELLER_CONFIG}")
    print(f"  Database: {BASE_DIR}/seller_monitoring/monitor.db\n")
    
    print(f"{Colors.BOLD}🔔 Notifications:{Colors.ENDC}")
    print(f"  You will receive Telegram notifications when:")
    print(f"  • New products are listed")
    print(f"  • Prices change")
    print(f"  • Products are edited")
    print(f"  • Products are deleted\n")
    
    print(f"{Colors.BOLD}📊 Database:{Colors.ENDC}")
    print(f"  All changes are logged to SQLite database")
    print(f"  View history: sqlite3 {BASE_DIR}/seller_monitoring/monitor.db\n")
    
    print(f"{Colors.GREEN}✓ Setup successful! Monitor is running 24/7{Colors.ENDC}")
    print(f"{Colors.CYAN}You'll receive your first notification within 10-15 minutes{Colors.ENDC}\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution flow"""
    print_header("🚀 Eldorado Seller Monitoring - Deployment")
    
    print(f"{Colors.BOLD}This script will setup automatic seller monitoring.{Colors.ENDC}")
    print(f"Estimated time: 5 minutes\n")
    
    if not get_yes_no("Ready to begin?", True):
        print_info("Setup cancelled")
        return 1
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        return 1
    
    # Step 2: Setup Telegram
    token, chat_id = setup_telegram_credentials()
    
    # Step 3: Update .env
    if not update_env_file(token, chat_id):
        return 1
    
    # Step 4: Configure sellers
    sellers = configure_sellers()
    if not update_seller_config(sellers):
        return 1
    
    # Step 5: Install dependencies
    if not install_dependencies():
        print_warning("Failed to install dependencies automatically")
        print_info("Please run manually: pip3 install -r requirements.txt")
        if not get_yes_no("Continue anyway?", False):
            return 1
    
    # Step 6: Test monitoring
    if not test_monitoring():
        print_warning("Test not completed successfully")
        if not get_yes_no("Continue with service installation?", False):
            print_info("Setup incomplete. Fix issues and run again.")
            return 1
    
    # Install systemd service
    install_systemd_service()
    
    # Print usage guide
    print_usage_guide()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup cancelled by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
