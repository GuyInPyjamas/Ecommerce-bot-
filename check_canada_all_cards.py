"""
Script to check all Canadian gift cards
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

from data_manager import get_gift_cards_for_country

def check_all_canada_cards():
    """Check all gift cards in Canada."""
    country = "Canada"
    
    logger.info("DISPLAYING ALL CANADIAN GIFT CARDS AND THEIR DENOMINATIONS")
    logger.info("==================================================")
    
    # Get all gift cards for Canada
    gift_cards = get_gift_cards_for_country(country)
    
    # Check each gift card's denominations
    for card_name, card_info in gift_cards.items():
        logger.info(f"Card: {card_name}")
        logger.info(f"Denominations shown in UI: {card_info['denominations']}")
        logger.info("-----------------------------------")

if __name__ == "__main__":
    check_all_canada_cards()