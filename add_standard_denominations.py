#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add standard denominations for the standardized gift cards
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

# Standard gift cards and their denominations (in specified order)
STANDARD_DENOMINATIONS = {
    # Order: Apple → Google Play → Visa Prepaid → Mastercard Prepaid → Netflix → Xbox → PlayStation → Spotify
    "Apple": [
        {"value": 100.0, "discount_rate": 15.0},
        {"value": 200.0, "discount_rate": 18.0},
        {"value": 300.0, "discount_rate": 22.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ],
    "Google Play": [
        {"value": 100.0, "discount_rate": 15.0},
        {"value": 200.0, "discount_rate": 18.0},
        {"value": 300.0, "discount_rate": 22.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ],
    "Visa Prepaid": [
        {"value": 100.0, "discount_rate": 10.0},
        {"value": 200.0, "discount_rate": 12.0},
        {"value": 300.0, "discount_rate": 18.0},
        {"value": 500.0, "discount_rate": 20.0},
        {"value": 1000.0, "discount_rate": 25.0}
    ],
    "Mastercard Prepaid": [
        {"value": 100.0, "discount_rate": 10.0},
        {"value": 200.0, "discount_rate": 12.0},
        {"value": 300.0, "discount_rate": 18.0},
        {"value": 500.0, "discount_rate": 20.0},
        {"value": 1000.0, "discount_rate": 25.0}
    ],
    "Netflix": [
        {"value": 100.0, "discount_rate": 15.0},
        {"value": 200.0, "discount_rate": 18.0},
        {"value": 300.0, "discount_rate": 22.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ],
    "Xbox": [
        {"value": 100.0, "discount_rate": 12.0},
        {"value": 200.0, "discount_rate": 15.0},
        {"value": 300.0, "discount_rate": 20.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ],
    "PlayStation": [
        {"value": 100.0, "discount_rate": 12.0},
        {"value": 200.0, "discount_rate": 15.0},
        {"value": 300.0, "discount_rate": 20.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ],
    "Spotify": [
        {"value": 100.0, "discount_rate": 10.0},
        {"value": 200.0, "discount_rate": 15.0},
        {"value": 300.0, "discount_rate": 20.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ]
}

# Specific denominations for USA, UK, Canada, and Australia
WESTERN_DENOMINATIONS = {
    # Order: Apple → Google Play → Visa Prepaid → Mastercard Prepaid → Netflix → Xbox → PlayStation → Spotify
    "Apple": [
        {"value": 100.0, "discount_rate": 15.0},
        {"value": 200.0, "discount_rate": 18.0},
        {"value": 300.0, "discount_rate": 22.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ],
    "Google Play": [
        {"value": 100.0, "discount_rate": 15.0},
        {"value": 200.0, "discount_rate": 18.0},
        {"value": 300.0, "discount_rate": 22.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ],
    "Visa Prepaid": [
        {"value": 100.0, "discount_rate": 10.0},
        {"value": 200.0, "discount_rate": 12.0},
        {"value": 300.0, "discount_rate": 18.0},
        {"value": 500.0, "discount_rate": 20.0},
        {"value": 1000.0, "discount_rate": 25.0}
    ],
    "Mastercard Prepaid": [
        {"value": 100.0, "discount_rate": 10.0},
        {"value": 200.0, "discount_rate": 12.0},
        {"value": 300.0, "discount_rate": 18.0},
        {"value": 500.0, "discount_rate": 20.0},
        {"value": 1000.0, "discount_rate": 25.0}
    ],
    "Netflix": [
        {"value": 100.0, "discount_rate": 15.0},
        {"value": 200.0, "discount_rate": 18.0},
        {"value": 300.0, "discount_rate": 22.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ],
    "Xbox": [
        {"value": 100.0, "discount_rate": 12.0},
        {"value": 200.0, "discount_rate": 15.0},
        {"value": 300.0, "discount_rate": 20.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ],
    "PlayStation": [
        {"value": 100.0, "discount_rate": 12.0},
        {"value": 200.0, "discount_rate": 15.0},
        {"value": 300.0, "discount_rate": 20.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ],
    "Spotify": [
        {"value": 100.0, "discount_rate": 10.0},
        {"value": 200.0, "discount_rate": 15.0},
        {"value": 300.0, "discount_rate": 20.0},
        {"value": 500.0, "discount_rate": 25.0},
        {"value": 1000.0, "discount_rate": 30.0}
    ]
}

# Euro-specific denominations (exact values in Euro without multiplier)
EURO_DENOMINATIONS = {
    # Order: Apple → Google Play → Visa Prepaid → Mastercard Prepaid → Netflix → Xbox → PlayStation → Spotify
    "Apple": [
        {"value": 100.0, "discount_rate": 15.0},
        {"value": 200.0, "discount_rate": 18.0},
        {"value": 300.0, "discount_rate": 22.0},
        {"value": 500.0, "discount_rate": 25.0}
    ],
    "Google Play": [
        {"value": 100.0, "discount_rate": 15.0},
        {"value": 200.0, "discount_rate": 18.0},
        {"value": 300.0, "discount_rate": 22.0},
        {"value": 500.0, "discount_rate": 25.0}
    ],
    "Visa Prepaid": [
        {"value": 100.0, "discount_rate": 10.0},
        {"value": 200.0, "discount_rate": 12.0},
        {"value": 300.0, "discount_rate": 18.0},
        {"value": 500.0, "discount_rate": 20.0}
    ],
    "Mastercard Prepaid": [
        {"value": 100.0, "discount_rate": 10.0},
        {"value": 200.0, "discount_rate": 12.0},
        {"value": 300.0, "discount_rate": 18.0},
        {"value": 500.0, "discount_rate": 20.0}
    ],
    "Netflix": [
        {"value": 100.0, "discount_rate": 15.0},
        {"value": 200.0, "discount_rate": 18.0},
        {"value": 300.0, "discount_rate": 22.0},
        {"value": 500.0, "discount_rate": 25.0}
    ],
    "Xbox": [
        {"value": 100.0, "discount_rate": 12.0},
        {"value": 200.0, "discount_rate": 15.0},
        {"value": 300.0, "discount_rate": 20.0},
        {"value": 500.0, "discount_rate": 25.0}
    ],
    "PlayStation": [
        {"value": 100.0, "discount_rate": 12.0},
        {"value": 200.0, "discount_rate": 15.0},
        {"value": 300.0, "discount_rate": 20.0},
        {"value": 500.0, "discount_rate": 25.0}
    ],
    "Spotify": [
        {"value": 100.0, "discount_rate": 10.0},
        {"value": 200.0, "discount_rate": 15.0},
        {"value": 300.0, "discount_rate": 20.0},
        {"value": 500.0, "discount_rate": 25.0}
    ]
}

# Currency symbols for each country
COUNTRY_CURRENCIES = {
    "USA": "$",
    "UK": "£",
    "Russia": "₽",
    "Germany": "€",
    "Canada": "C$",  # Updated to use C$ for Canadian dollars
    "Australia": "$",
    "France": "€",
    "Italy": "€",
    "Turkey": "₺",
    "Spain": "€",
    "Netherlands": "€"
}

# Value multipliers for different currencies
CURRENCY_MULTIPLIERS = {
    "$": 1.0,       # USD baseline
    "£": 0.8,       # GBP (1 GBP ≈ 1.25 USD)
    "€": 0.9,       # EUR (1 EUR ≈ 1.11 USD)
    "₽": 90.0,      # RUB (1 USD ≈ 90 RUB)
    "₺": 30.0,      # TRY (1 USD ≈ 30 TRY)
    "C$": 1.0       # CAD (Canadian Dollar - using 1:1 for exact values)
}

def add_standard_denominations(country_names=None):
    """
    Add standard denominations for all gift cards in specified countries.
    
    Args:
        country_names (list): List of country names to process. If None, process all countries.
    """
    try:
        with app.app_context():
            # Get countries to process
            if country_names:
                countries = Country.query.filter(Country.name.in_(country_names), Country.active == True).all()
            else:
                countries = Country.query.filter_by(active=True).all()
                
            logger.info(f"Processing {len(countries)} countries")
            
            # Countries that use the special denomination structure
            western_countries = ["USA", "UK", "Canada", "Australia"]  # Non-Euro Western countries
            euro_countries = ["Germany", "France", "Italy", "Spain", "Netherlands"]  # Euro countries
            
            # For each country, set up denominations for all gift cards
            for country in countries:
                logger.info(f"Processing country: {country.name}")
                currency_symbol = COUNTRY_CURRENCIES.get(country.name, "$")
                multiplier = CURRENCY_MULTIPLIERS.get(currency_symbol, 1.0)
                
                # Get all active gift cards for this country
                gift_cards = GiftCard.query.filter_by(country_id=country.id, active=True).all()
                
                for card in gift_cards:
                    logger.info(f"Setting up denominations for {card.name} in {country.name}")
                    
                    # Check if this card has denominations defined
                    if card.name in STANDARD_DENOMINATIONS:
                        # Remove existing denominations for this card
                        existing_denoms = Denomination.query.filter_by(gift_card_id=card.id).all()
                        for denom in existing_denoms:
                            db.session.delete(denom)
                        
                        # Choose the appropriate denominations based on country
                        if country.name in euro_countries and card.name in EURO_DENOMINATIONS:
                            # Use Euro denominations for Euro countries (no multiplier)
                            denominations_to_use = EURO_DENOMINATIONS[card.name]
                            logger.info(f"Using Euro denominations for {card.name} in {country.name}")
                            
                            # Add the denominations (no multiplier for Euro countries)
                            for denom_data in denominations_to_use:
                                denom = Denomination(
                                    value=denom_data["value"],  # Exact Euro value without multiplier
                                    currency_symbol="€",
                                    gift_card_id=card.id,
                                    discount_rate=denom_data["discount_rate"],
                                    active=True
                                )
                                db.session.add(denom)
                        elif country.name in western_countries and card.name in WESTERN_DENOMINATIONS:
                            # Use Western denominations for USA, UK, Canada, and Australia
                            denominations_to_use = WESTERN_DENOMINATIONS[card.name]
                            logger.info(f"Using Western denominations for {card.name} in {country.name}")
                            
                            # Add the denominations
                            for denom_data in denominations_to_use:
                                if country.name == "UK":
                                    # For UK, use exact pound values (no multiplier)
                                    denom = Denomination(
                                        value=denom_data["value"],  # Exact value without multiplier
                                        currency_symbol="£",
                                        gift_card_id=card.id,
                                        discount_rate=denom_data["discount_rate"],
                                        active=True
                                    )
                                    db.session.add(denom)
                                else:
                                    # For other Western countries, apply the currency multiplier
                                    adjusted_value = denom_data["value"] * multiplier
                                    denom = Denomination(
                                        value=adjusted_value,
                                        currency_symbol=currency_symbol,
                                        gift_card_id=card.id,
                                        discount_rate=denom_data["discount_rate"],
                                        active=True
                                    )
                                    db.session.add(denom)
                        else:
                            # Use standard denominations for other countries
                            denominations_to_use = STANDARD_DENOMINATIONS[card.name]
                            logger.info(f"Using standard denominations for {card.name} in {country.name}")
                            
                            # Add the denominations with currency multiplier
                            for denom_data in denominations_to_use:
                                adjusted_value = denom_data["value"] * multiplier
                                denom = Denomination(
                                    value=adjusted_value,
                                    currency_symbol=currency_symbol,
                                    gift_card_id=card.id,
                                    discount_rate=denom_data["discount_rate"],
                                    active=True
                                )
                                db.session.add(denom)
                
                # Commit changes for this country
                db.session.commit()
                
            logger.info("Adding standard denominations completed successfully")
            return True
    except Exception as e:
        logger.error(f"Error adding standard denominations: {e}")
        try:
            with app.app_context():
                db.session.rollback()
        except:
            pass
        return False

def main():
    """Run the script to add standard denominations in batches."""
    # Define country groups
    standard_western = ["USA", "UK", "Canada", "Australia"]
    euro_countries = ["Germany", "France", "Italy", "Spain", "Netherlands"]
    
    # Process Euro countries first
    logger.info(f"Processing Euro countries...")
    for country in euro_countries:
        logger.info(f"Processing Euro country: {country}")
        add_standard_denominations([country])
    
    # Process other Western countries
    logger.info(f"Processing other Western countries...")
    for country in standard_western:
        logger.info(f"Processing Western country: {country}")
        add_standard_denominations([country])

if __name__ == "__main__":
    main()