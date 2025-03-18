#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to seed denominations according to the requirements
"""
import os
import logging
from flask import Flask
from models import db, Country, GiftCard, Denomination

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def create_app():
    """Create app for database connection."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    db.init_app(app)
    return app

def seed_denominations():
    """Seed denomination data according to requirements."""
    # Define country groups based on currency
    usd_countries = ["USA", "Canada", "Australia"]
    euro_countries = ["Germany", "France", "Italy", "Spain", "Netherlands"]
    ruble_country = ["Russia"]
    lira_country = ["Turkey"]
    pound_country = ["UK"]
    
    # Get all gift cards
    gift_cards = GiftCard.query.join(Country).filter(GiftCard.active == True).all()
    
    # Define denominations by country group
    denominations = {
        "usd": [
            {"value": 100.0, "currency_symbol": "$", "discount_rate": 45.0},
            {"value": 200.0, "currency_symbol": "$", "discount_rate": 45.0},
            {"value": 300.0, "currency_symbol": "$", "discount_rate": 45.0},
            {"value": 500.0, "currency_symbol": "$", "discount_rate": 45.0},
            {"value": 1000.0, "currency_symbol": "$", "discount_rate": 45.0}
        ],
        "euro": [
            {"value": 100.0, "currency_symbol": "€", "discount_rate": 45.0},
            {"value": 200.0, "currency_symbol": "€", "discount_rate": 45.0},
            {"value": 300.0, "currency_symbol": "€", "discount_rate": 45.0},
            {"value": 500.0, "currency_symbol": "€", "discount_rate": 45.0}
        ],
        "ruble": [
            {"value": 10000.0, "currency_symbol": "₽", "discount_rate": 45.0},
            {"value": 20000.0, "currency_symbol": "₽", "discount_rate": 45.0},
            {"value": 30000.0, "currency_symbol": "₽", "discount_rate": 45.0}
        ],
        "lira": [
            {"value": 1000.0, "currency_symbol": "₺", "discount_rate": 45.0},
            {"value": 2000.0, "currency_symbol": "₺", "discount_rate": 45.0},
            {"value": 3000.0, "currency_symbol": "₺", "discount_rate": 45.0}
        ],
        "pound": [
            {"value": 100.0, "currency_symbol": "£", "discount_rate": 45.0},
            {"value": 200.0, "currency_symbol": "£", "discount_rate": 45.0},
            {"value": 300.0, "currency_symbol": "£", "discount_rate": 45.0},
            {"value": 500.0, "currency_symbol": "£", "discount_rate": 45.0},
            {"value": 1000.0, "currency_symbol": "£", "discount_rate": 45.0}
        ]
    }
    
    # Add denominations based on country groups
    count = 0
    for gift_card in gift_cards:
        country_name = gift_card.country.name
        
        if country_name in usd_countries:
            for denom in denominations["usd"]:
                add_denomination(gift_card, denom)
                count += 1
        elif country_name in euro_countries:
            for denom in denominations["euro"]:
                add_denomination(gift_card, denom)
                count += 1
        elif country_name in ruble_country:
            for denom in denominations["ruble"]:
                add_denomination(gift_card, denom)
                count += 1
        elif country_name in lira_country:
            for denom in denominations["lira"]:
                add_denomination(gift_card, denom)
                count += 1
        elif country_name in pound_country:
            for denom in denominations["pound"]:
                add_denomination(gift_card, denom)
                count += 1
    
    db.session.commit()
    print(f"Added {count} denominations successfully!")

def add_denomination(gift_card, denom_data):
    """Add a denomination for a specific gift card."""
    print(f"Adding denomination: {denom_data['currency_symbol']}{denom_data['value']} for {gift_card.name} in {gift_card.country.name}")
    denomination = Denomination(
        value=denom_data["value"],
        currency_symbol=denom_data["currency_symbol"],
        gift_card_id=gift_card.id,
        discount_rate=denom_data["discount_rate"]
    )
    db.session.add(denomination)

def main():
    """Run database seeding."""
    app = create_app()
    with app.app_context():
        print("Seeding denominations according to requirements...")
        seed_denominations()
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    main()