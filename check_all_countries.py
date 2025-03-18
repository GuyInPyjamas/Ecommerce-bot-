"""
Script to check denominations in all countries
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

from data_manager import get_countries, get_gift_cards_for_country

def check_all_countries():
    """Check the denominations for all countries."""
    
    logger.info("CHECKING DENOMINATIONS FOR ALL COUNTRIES")
    logger.info("===============================")
    
    # Get all countries
    countries = get_countries()
    
    # Check each country's gift cards
    for country_name in countries:
        logger.info(f"\nCOUNTRY: {country_name}")
        logger.info("--------------------")
        
        # Get all gift cards for this country
        gift_cards = get_gift_cards_for_country(country_name)
        
        # Check first gift card's denominations for this country
        if gift_cards:
            first_card_name = next(iter(gift_cards))
            first_card = gift_cards[first_card_name]
            logger.info(f"Example card: {first_card_name}")
            logger.info(f"Denominations: {first_card['denominations']}")
        else:
            logger.info("No gift cards found for this country")
        
        logger.info("==============================")

if __name__ == "__main__":
    check_all_countries()