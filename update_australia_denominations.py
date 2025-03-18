"""
Script to update all Australian gift card denominations to the standardized values
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

from app import app
from models import Country, GiftCard, Denomination
from data_manager import db

def update_australia_denominations():
    """Update all Australian gift card denominations to the standardized values."""
    
    logger.info("Updating all Australian gift card denominations to standardized values")
    logger.info("===============================================================")
    
    try:
        with app.app_context():
            # Get Australia
            australia = Country.query.filter_by(name="Australia").first()
            
            if not australia:
                logger.error("Australia not found in the database")
                return
            
            # Get all gift cards for Australia
            gift_cards = GiftCard.query.filter_by(country_id=australia.id).all()
            
            if not gift_cards:
                logger.error("No gift cards found for Australia")
                return
            
            # The standardized denominations for Australia (updated to match requirements)
            standard_denominations = [
                {"value": 100.0, "currency_symbol": "A$", "discount_rate": 45.0},
                {"value": 200.0, "currency_symbol": "A$", "discount_rate": 45.0},
                {"value": 300.0, "currency_symbol": "A$", "discount_rate": 45.0},
                {"value": 500.0, "currency_symbol": "A$", "discount_rate": 45.0},
                {"value": 1000.0, "currency_symbol": "A$", "discount_rate": 45.0}
            ]
            
            for gift_card in gift_cards:
                logger.info(f"Processing gift card: {gift_card.name}")
                
                # Delete existing denominations
                Denomination.query.filter_by(gift_card_id=gift_card.id).delete()
                
                # Add standardized denominations
                for denom_data in standard_denominations:
                    denomination = Denomination(
                        value=denom_data["value"],
                        currency_symbol=denom_data["currency_symbol"],
                        gift_card_id=gift_card.id,
                        discount_rate=denom_data["discount_rate"],
                        active=True
                    )
                    db.session.add(denomination)
                
                logger.info(f"Updated denominations for {gift_card.name}")
            
            # Commit all changes
            db.session.commit()
            logger.info("All Australian gift card denominations have been updated successfully")
    
    except Exception as e:
        logger.error(f"Error updating Australian denominations: {e}")
        # Rollback in case of error
        try:
            with app.app_context():
                db.session.rollback()
        except:
            pass

if __name__ == "__main__":
    update_australia_denominations()