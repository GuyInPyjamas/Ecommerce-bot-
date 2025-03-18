#!/usr/bin/env python3
"""
Script to check the current denominations for gift cards in all countries
"""
import logging
import os
from dotenv import load_dotenv

from models import Country, GiftCard, Denomination
from app import app, db

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def check_denominations(country_name):
    """
    Check the current denominations for all gift cards in a specific country.
    
    Args:
        country_name (str): Name of the country to check
    """
    try:
        with app.app_context():
            # Get the country
            country = Country.query.filter_by(name=country_name, active=True).first()
            if not country:
                logger.error(f"Country '{country_name}' not found or inactive")
                return
            
            logger.info(f"Checking denominations for {country_name}")
            
            # Get gift cards for this country
            gift_cards = GiftCard.query.filter_by(country_id=country.id, active=True).all()
            
            for card in gift_cards:
                logger.info(f"Gift card: {card.name}")
                
                # Get denominations for this card
                denominations = Denomination.query.filter_by(gift_card_id=card.id, active=True).all()
                
                # Display denominations
                for denom in denominations:
                    logger.info(f"  {denom.currency_symbol}{denom.value} (Discount: {denom.discount_rate}%)")
                
                logger.info("--------------------")
    
    except Exception as e:
        logger.error(f"Error checking denominations: {e}")

def main():
    """Run the script to check denominations."""
    # Check the Euro countries to verify they have the correct denominations
    check_denominations("Germany")
    check_denominations("France")
    check_denominations("Italy")

if __name__ == "__main__":
    main()