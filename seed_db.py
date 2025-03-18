import os
import sys
from dotenv import load_dotenv
from flask import Flask
from models import db, Country, GiftCard, Denomination

# Load environment variables
load_dotenv()

def create_app():
    """Create test app for seeding database."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    db.init_app(app)
    return app

def seed_countries():
    """Seed country data."""
    countries = [
        {"name": "USA", "code": "US", "flag_emoji": "🇺🇸"},
        {"name": "UK", "code": "GB", "flag_emoji": "🇬🇧"},
        {"name": "Russia", "code": "RU", "flag_emoji": "🇷🇺"},
        {"name": "Germany", "code": "DE", "flag_emoji": "🇩🇪"},
        {"name": "Canada", "code": "CA", "flag_emoji": "🇨🇦"},
        {"name": "Australia", "code": "AU", "flag_emoji": "🇦🇺"},
        {"name": "France", "code": "FR", "flag_emoji": "🇫🇷"},
        {"name": "Italy", "code": "IT", "flag_emoji": "🇮🇹"},
        {"name": "Turkey", "code": "TR", "flag_emoji": "🇹🇷"},
        {"name": "Spain", "code": "ES", "flag_emoji": "🇪🇸"},
        {"name": "Netherlands", "code": "NL", "flag_emoji": "🇳🇱"}
    ]
    
    for country_data in countries:
        country = Country.query.filter_by(name=country_data["name"]).first()
        if not country:
            print(f"Adding country: {country_data['name']}")
            country = Country(**country_data)
            db.session.add(country)
        else:
            print(f"Country already exists: {country_data['name']}")
    
    db.session.commit()
    print("Countries seeded successfully!")

def seed_gift_cards():
    """Seed gift card data."""
    countries = Country.query.all()
    country_map = {country.name: country.id for country in countries}
    
    gift_cards = [
        {
            "name": "Amazon",
            "description": "Amazon gift cards for online shopping",
            "image_url": "https://cdn.example.com/amazon.png",
            "countries": ["USA", "UK", "Germany", "France", "Italy", "Spain", "Netherlands"]
        },
        {
            "name": "Google Play",
            "description": "Google Play gift cards for apps, games, and content",
            "image_url": "https://cdn.example.com/google_play.png",
            "countries": ["USA", "UK", "Canada", "Australia", "Germany", "France", "Italy", "Spain"]
        },
        {
            "name": "Steam",
            "description": "Steam gift cards for PC games",
            "image_url": "https://cdn.example.com/steam.png",
            "countries": ["USA", "UK", "Canada", "Australia", "Russia", "Germany", "France", "Turkey"]
        },
        {
            "name": "iTunes",
            "description": "iTunes gift cards for Apple's App Store, iTunes, and services",
            "image_url": "https://cdn.example.com/itunes.png",
            "countries": ["USA", "UK", "Canada", "Australia", "Germany", "France", "Italy", "Netherlands"]
        },
        {
            "name": "PlayStation",
            "description": "PlayStation gift cards for games and content",
            "image_url": "https://cdn.example.com/playstation.png",
            "countries": ["USA", "UK", "Canada", "Australia", "Russia", "Germany", "France", "Italy", "Spain"]
        },
        {
            "name": "Xbox",
            "description": "Xbox gift cards for games and content",
            "image_url": "https://cdn.example.com/xbox.png",
            "countries": ["USA", "UK", "Canada", "Australia", "Germany", "France", "Italy", "Spain"]
        },
        {
            "name": "Netflix",
            "description": "Netflix gift cards for streaming service",
            "image_url": "https://cdn.example.com/netflix.png",
            "countries": ["USA", "UK", "Canada", "Australia", "Germany", "France", "Italy", "Spain", "Netherlands"]
        },
        {
            "name": "Spotify",
            "description": "Spotify gift cards for music streaming",
            "image_url": "https://cdn.example.com/spotify.png",
            "countries": ["USA", "UK", "Germany", "France", "Spain", "Netherlands"]
        }
    ]
    
    for gift_card_data in gift_cards:
        for country_name in gift_card_data["countries"]:
            country_id = country_map.get(country_name)
            if country_id:
                gift_card = GiftCard.query.filter_by(name=gift_card_data["name"], country_id=country_id).first()
                if not gift_card:
                    print(f"Adding gift card: {gift_card_data['name']} for {country_name}")
                    gift_card = GiftCard(
                        name=gift_card_data["name"],
                        description=gift_card_data["description"],
                        image_url=gift_card_data["image_url"],
                        country_id=country_id
                    )
                    db.session.add(gift_card)
                else:
                    print(f"Gift card already exists: {gift_card_data['name']} for {country_name}")
    
    db.session.commit()
    print("Gift cards seeded successfully!")

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
        print("Creating database tables if they don't exist...")
        db.create_all()
        
        print("Seeding countries...")
        seed_countries()
        
        print("Seeding gift cards...")
        seed_gift_cards()
        
        print("Seeding denominations...")
        seed_denominations()
        
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    main()