#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main entry point for the Telegram Gift Card Store Bot
"""
import os
import logging
from dotenv import load_dotenv
from bot import create_bot, run_bot

# Import the Flask app for gunicorn
from app import app

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def start_bot():
    """Start the Telegram bot."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Check for required environment variables
        required_env_vars = ['TELEGRAM_BOT_TOKEN', 'ADMIN_USER_ID']
        for var in required_env_vars:
            if not os.getenv(var):
                logger.error(f"Environment variable {var} is not set")
                return
        
        # Log cryptocurrency addresses (truncated for security)
        from config import CRYPTOCURRENCIES
        for crypto, data in CRYPTOCURRENCIES.items():
            address = data.get("address", "")
            if address:
                logger.info(f"{crypto} address configured: {address[:6]}...{address[-4:]}")
            else:
                logger.warning(f"{crypto} address not configured")
        
        # Create and run the bot
        logger.info("Starting Telegram bot...")
        bot = create_bot()
        run_bot(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

# This script will simply run the bot when called directly
if __name__ == '__main__':
    start_bot()
