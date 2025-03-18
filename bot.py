#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bot configuration and initialization
"""
import os
import logging
from pathlib import Path
from telegram.ext import (
    Updater,
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    Filters
)

from handlers import (
    start_command, 
    language_command, 
    history_command,
    help_command,
    button_callback,
    handle_text
)
from admin_handlers import (
    admin_command,
    admin_button_callback
)

# Create data directory if it doesn't exist
Path("data").mkdir(exist_ok=True)
for file_name in ["countries.json", "gift_cards.json", "orders.json"]:
    file_path = Path(f"data/{file_name}")
    if not file_path.exists():
        with open(file_path, "w") as f:
            f.write("[]" if file_name == "orders.json" else "{}")

logger = logging.getLogger(__name__)

def create_bot():
    """Create and configure the bot"""
    # Get bot token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Create updater and dispatcher
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    
    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("language", language_command))
    dispatcher.add_handler(CommandHandler("history", history_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("admin", admin_command))
    
    # Add callback query handler for inline buttons
    dispatcher.add_handler(CallbackQueryHandler(button_callback, pattern="^(?!admin_).*"))
    dispatcher.add_handler(CallbackQueryHandler(admin_button_callback, pattern="^admin_.*"))
    
    # Add message handler for text messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    
    return updater

def run_bot(updater):
    """Run the bot"""
    # Start the Bot
    logger.info("Starting bot...")
    updater.start_polling()
    updater.idle()
