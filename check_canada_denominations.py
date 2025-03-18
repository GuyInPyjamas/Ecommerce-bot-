#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to check Canadian denominations
"""
import os
import logging
from models import db, Country, GiftCard, Denomination
from app import app
from data_manager import get_gift_cards_for_country, get_card_denominations

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def check_canada_denominations():
    """Check the Canadian denominations."""
    with app.app_context():
        logger.info("BOT INTERFACE VIEW FOR CANADIAN GIFT CARDS")
        logger.info("===============================")
        
        # Directly check the bot interface view
        gift_cards_data = get_gift_cards_for_country("Canada")
        
        # Just check a couple of important gift cards
        important_cards = ["Apple", "Google Play", "Visa Prepaid", "Mastercard Prepaid", "Xbox", "PlayStation"]
        for card_name in important_cards:
            if card_name in gift_cards_data:
                card_data = gift_cards_data[card_name]
                logger.info(f"Card: {card_name}")
                logger.info(f"Denominations shown in UI: {card_data['denominations']}")
                logger.info("-" * 20)
                
                # Get denominations for keyboard displays
                keyboard_denoms = get_card_denominations("Canada", card_name)
                logger.info(f"Keyboard buttons: {keyboard_denoms}")
                logger.info("=" * 30)

if __name__ == "__main__":
    check_canada_denominations()