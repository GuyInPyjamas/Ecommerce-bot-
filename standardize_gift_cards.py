#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to standardize gift card options across all countries
"""
import os
import logging
from flask import Flask
from dotenv import load_dotenv
from models import db, Country, GiftCard, Denomination
from app import app

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Standard gift cards to be available for all countries in specified order
STANDARD_GIFT_CARDS = [
    "Apple",
    "Google Play",
    "Visa Prepaid",
    "Mastercard Prepaid",
    "Netflix",
    "Xbox",
    "PlayStation",
    "Spotify"
]

def standardize_gift_cards():
    """Standardize gift cards across all countries."""
    try:
        with app.app_context():
            # Get all active countries
            countries = Country.query.filter_by(active=True).all()
            logger.info(f"Found {len(countries)} active countries")
            
            # For each country, ensure standard gift cards exist
            for country in countries:
                logger.info(f"Processing country: {country.name}")
                
                # First, deactivate all existing gift cards that are not in the standard list
                existing_cards = GiftCard.query.filter_by(country_id=country.id).all()
                for card in existing_cards:
                    if card.name not in STANDARD_GIFT_CARDS:
                        logger.info(f"Deactivating non-standard gift card: {card.name}")
                        card.active = False
                
                # Make sure all standard gift cards exist for this country
                for card_name in STANDARD_GIFT_CARDS:
                    # Check if the gift card already exists
                    gift_card = GiftCard.query.filter_by(country_id=country.id, name=card_name).first()
                    
                    if gift_card:
                        # If it exists, make sure it's active
                        logger.info(f"Activating existing gift card: {card_name}")
                        gift_card.active = True
                    else:
                        # If it doesn't exist, create it
                        logger.info(f"Creating new gift card: {card_name}")
                        gift_card = GiftCard(
                            name=card_name,
                            description=f"{card_name} Gift Card",
                            country_id=country.id,
                            active=True
                        )
                        db.session.add(gift_card)
                
                # Commit changes for this country
                db.session.commit()
                
            logger.info("Gift card standardization completed successfully")
            return True
    except Exception as e:
        logger.error(f"Error standardizing gift cards: {e}")
        try:
            with app.app_context():
                db.session.rollback()
        except:
            pass
        return False

def main():
    """Run gift card standardization."""
    standardize_gift_cards()

if __name__ == "__main__":
    main()