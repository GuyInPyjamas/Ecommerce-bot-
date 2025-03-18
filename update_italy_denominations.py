"""
Script to update all Italian gift card denominations to the standardized values
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

def update_italy_denominations():
    """Update all Italian gift card denominations to the standardized values."""
    
    logger.info("Updating all Italian gift card denominations to standardized values")
    logger.info("===============================================================")
    
    try:
        with app.app_context():
            # Get Italy
            italy = Country.query.filter_by(name="Italy").first()
            
            if not italy:
                logger.error("Italy not found in the database")
                return
            
            # Get all gift cards for Italy
            gift_cards = GiftCard.query.filter_by(country_id=italy.id).all()
            
            if not gift_cards:
                logger.error("No gift cards found for Italy")
                return
            
            # The standardized denominations for Italy (updated to match requirements)
            standard_denominations = [
                {"value": 100.0, "currency_symbol": "€", "discount_rate": 45.0},
                {"value": 200.0, "currency_symbol": "€", "discount_rate": 45.0},
                {"value": 300.0, "currency_symbol": "€", "discount_rate": 45.0},
                {"value": 500.0, "currency_symbol": "€", "discount_rate": 45.0}
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
            logger.info("All Italian gift card denominations have been updated successfully")
    
    except Exception as e:
        logger.error(f"Error updating Italian denominations: {e}")
        # Rollback in case of error
        try:
            with app.app_context():
                db.session.rollback()
        except:
            pass

if __name__ == "__main__":
    update_italy_denominations()