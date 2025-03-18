#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to seed denominations only
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
    """Seed denomination data."""
    # Structure: country -> gift card -> denominations
    denominations_map = {
        "USA": {
            "Amazon": [
                {"value": 25.0, "currency_symbol": "$", "discount_rate": 10.0},
                {"value": 50.0, "currency_symbol": "$", "discount_rate": 15.0},
                {"value": 100.0, "currency_symbol": "$", "discount_rate": 20.0},
                {"value": 200.0, "currency_symbol": "$", "discount_rate": 25.0}
            ],
            "Google Play": [
                {"value": 25.0, "currency_symbol": "$", "discount_rate": 12.0},
                {"value": 50.0, "currency_symbol": "$", "discount_rate": 18.0},
                {"value": 100.0, "currency_symbol": "$", "discount_rate": 22.0}
            ],
            "Steam": [
                {"value": 20.0, "currency_symbol": "$", "discount_rate": 10.0},
                {"value": 50.0, "currency_symbol": "$", "discount_rate": 15.0},
                {"value": 100.0, "currency_symbol": "$", "discount_rate": 20.0}
            ],
            "iTunes": [
                {"value": 15.0, "currency_symbol": "$", "discount_rate": 8.0},
                {"value": 25.0, "currency_symbol": "$", "discount_rate": 12.0},
                {"value": 50.0, "currency_symbol": "$", "discount_rate": 18.0},
                {"value": 100.0, "currency_symbol": "$", "discount_rate": 25.0}
            ],
            "PlayStation": [
                {"value": 10.0, "currency_symbol": "$", "discount_rate": 5.0},
                {"value": 20.0, "currency_symbol": "$", "discount_rate": 10.0},
                {"value": 50.0, "currency_symbol": "$", "discount_rate": 15.0},
                {"value": 100.0, "currency_symbol": "$", "discount_rate": 20.0}
            ],
            "Xbox": [
                {"value": 15.0, "currency_symbol": "$", "discount_rate": 8.0},
                {"value": 25.0, "currency_symbol": "$", "discount_rate": 12.0},
                {"value": 50.0, "currency_symbol": "$", "discount_rate": 18.0},
                {"value": 100.0, "currency_symbol": "$", "discount_rate": 25.0}
            ],
            "Netflix": [
                {"value": 30.0, "currency_symbol": "$", "discount_rate": 15.0},
                {"value": 60.0, "currency_symbol": "$", "discount_rate": 20.0},
                {"value": 100.0, "currency_symbol": "$", "discount_rate": 25.0}
            ],
            "Spotify": [
                {"value": 10.0, "currency_symbol": "$", "discount_rate": 5.0},
                {"value": 30.0, "currency_symbol": "$", "discount_rate": 15.0},
                {"value": 60.0, "currency_symbol": "$", "discount_rate": 20.0}
            ]
        },
        "UK": {
            "Amazon": [
                {"value": 25.0, "currency_symbol": "£", "discount_rate": 10.0},
                {"value": 50.0, "currency_symbol": "£", "discount_rate": 15.0},
                {"value": 100.0, "currency_symbol": "£", "discount_rate": 20.0},
                {"value": 200.0, "currency_symbol": "£", "discount_rate": 25.0}
            ],
            "Google Play": [
                {"value": 25.0, "currency_symbol": "£", "discount_rate": 12.0},
                {"value": 50.0, "currency_symbol": "£", "discount_rate": 18.0},
                {"value": 100.0, "currency_symbol": "£", "discount_rate": 22.0}
            ],
            "Steam": [
                {"value": 20.0, "currency_symbol": "£", "discount_rate": 10.0},
                {"value": 50.0, "currency_symbol": "£", "discount_rate": 15.0},
                {"value": 100.0, "currency_symbol": "£", "discount_rate": 20.0}
            ]
        }
    }
    
    countries = Country.query.all()
    country_map = {country.name: country.id for country in countries}
    
    for country_name, gift_cards in denominations_map.items():
        country_id = country_map.get(country_name)
        if not country_id:
            print(f"Country not found: {country_name}, skipping")
            continue
        
        for gift_card_name, denominations_list in gift_cards.items():
            gift_card = GiftCard.query.filter_by(name=gift_card_name, country_id=country_id).first()
            if not gift_card:
                print(f"Gift card not found: {gift_card_name} for {country_name}, skipping")
                continue
            
            for denom_data in denominations_list:
                denomination = Denomination.query.filter_by(
                    value=denom_data["value"],
                    currency_symbol=denom_data["currency_symbol"],
                    gift_card_id=gift_card.id
                ).first()
                
                if not denomination:
                    print(f"Adding denomination: {denom_data['currency_symbol']}{denom_data['value']} for {gift_card_name} in {country_name}")
                    denomination = Denomination(
                        value=denom_data["value"],
                        currency_symbol=denom_data["currency_symbol"],
                        gift_card_id=gift_card.id,
                        discount_rate=denom_data["discount_rate"]
                    )
                    db.session.add(denomination)
                else:
                    print(f"Denomination already exists: {denom_data['currency_symbol']}{denom_data['value']} for {gift_card_name} in {country_name}")
    
    db.session.commit()
    print("Denominations seeded successfully!")

def main():
    """Run database seeding."""
    app = create_app()
    with app.app_context():
        print("Seeding denominations only...")
        seed_denominations()
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    main()