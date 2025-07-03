#!/usr/bin/env python3
"""
Optional Telegram Bot Launcher for Source Code Scanner
This file provides an optional way to run the Telegram bot interface.
If no TELEGRAM_BOT_TOKEN is provided, it will gracefully exit.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main function to optionally run the Telegram bot."""
    print("🤖 Source Code Scanner - Telegram Bot")
    print("=" * 50)
    
    # Check if Telegram bot token is available
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token or bot_token.strip() == '' or bot_token == 'your_telegram_bot_token_here':
        print("ℹ️  Telegram bot token tidak ditemukan atau belum dikonfigurasi.")
        print("💡 Untuk menggunakan Telegram bot:")
        print("   1. Buat bot baru dengan @BotFather di Telegram")
        print("   2. Salin token yang diberikan")
        print("   3. Tambahkan TELEGRAM_BOT_TOKEN=<your_token> ke file .env")
        print("   4. Jalankan kembali: python bot.py")
        print("")
        print("🔧 Alternatif: Gunakan command line interface dengan:")
        print("   python run.py -u <URL>")
        print("")
        print("📱 Atau jalankan bot langsung dengan:")
        print("   python telegrambot.py")
        return 0
    
    print("✅ Token Telegram bot ditemukan!")
    print("🚀 Memulai Telegram bot...")
    print("")
    
    try:
        # Import and run the telegram bot
        from telegrambot import TelegramJSScanner
        
        bot = TelegramJSScanner()
        bot.run()
        
    except ImportError as e:
        print(f"❌ Error importing telegram bot: {e}")
        print("💡 Pastikan semua dependencies sudah terinstall:")
        print("   pip install -r requirements.txt")
        return 1
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Bot dihentikan oleh user")
        return 0
    except Exception as e:
        print(f"❌ Bot gagal dijalankan: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())