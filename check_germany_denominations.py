"""
Script to check German denominations
"""
import logging
import os
import sys

from flask import Flask
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Load environment variables
load_dotenv()

from data_manager import get_gift_cards_for_country, get_card_denominations
from keyboards import get_denominations_keyboard

def check_germany_denominations():
    """Check the German denominations."""
    country = "Germany"
    
    logger.info("BOT INTERFACE VIEW FOR GERMAN GIFT CARDS")
    logger.info("===============================")
    
    # Get all gift cards for Germany
    gift_cards = get_gift_cards_for_country(country)
    
    # Check each gift card's denominations
    for card_name, card_info in gift_cards.items():
        logger.info(f"Card: {card_name}")
        logger.info(f"Denominations shown in UI: {card_info['denominations']}")
        logger.info("--------------------")
        
        # Check keyboard representation for this card's denominations
        keyboard_buttons = []
        for row in get_denominations_keyboard(country, card_name).inline_keyboard:
            for button in row:
                # Get the display text from the button instead of callback data
                keyboard_buttons.append(button.text)
        
        logger.info(f"Keyboard buttons: {keyboard_buttons}")
        logger.info("==============================")

if __name__ == "__main__":
    check_germany_denominations()