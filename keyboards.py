#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Keyboard generation functions for the Telegram bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from data_manager import (
    get_countries, 
    get_gift_cards_for_country, 
    get_card_denominations
)
from config import CRYPTOCURRENCIES

def get_countries_keyboard():
    """Create a keyboard with available countries."""
    countries_data = get_countries()
    keyboard = []
    
    # Create buttons for each country with flag emoji
    for country, data in countries_data.items():
        flag = data.get("flag", "")
        button = InlineKeyboardButton(f"{flag} {country}", callback_data=country)
        keyboard.append([button])  # One button per row
    
    return InlineKeyboardMarkup(keyboard)

def get_gift_cards_keyboard(country):
    """Create a keyboard with gift cards available for a specific country."""
    gift_cards = get_gift_cards_for_country(country)
    keyboard = []
    
    # Define the order of gift cards
    preferred_order = [
        "Apple",
        "Google Play",
        "Visa Prepaid",
        "Mastercard Prepaid",
        "Netflix",
        "Xbox",
        "PlayStation",
        "Spotify"  # Include Spotify at the end if it exists
    ]
    
    # Create buttons for each gift card in the specified order
    for card_name in preferred_order:
        if card_name in gift_cards:
            card_data = gift_cards[card_name]
            logo = card_data.get("logo", "")
            button = InlineKeyboardButton(f"{logo} {card_name}", callback_data=card_name)
            keyboard.append([button])  # One button per row
    
    # Add any remaining gift cards not in the preferred order
    for card_name, card_data in gift_cards.items():
        if card_name not in preferred_order:
            logo = card_data.get("logo", "")
            button = InlineKeyboardButton(f"{logo} {card_name}", callback_data=card_name)
            keyboard.append([button])  # One button per row
    
    # Add back button
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_countries")])
    
    return InlineKeyboardMarkup(keyboard)

def get_denominations_keyboard(country, gift_card):
    """Create a keyboard with available denominations for a gift card."""
    denominations = get_card_denominations(country, gift_card)
    keyboard = []
    
    # Create buttons for each denomination, one per row
    for denomination in denominations:
        button = InlineKeyboardButton(denomination, callback_data=denomination)
        keyboard.append([button])  # One button per row
    
    # Add back button
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_gift_cards")])
    
    return InlineKeyboardMarkup(keyboard)

def get_crypto_keyboard():
    """Create a keyboard with available cryptocurrencies for payment."""
    keyboard = []
    
    # Create buttons for each cryptocurrency, one per row
    for crypto_code, crypto_data in CRYPTOCURRENCIES.items():
        crypto_name = crypto_data.get("name", crypto_code)
        button = InlineKeyboardButton(crypto_name, callback_data=crypto_code)
        keyboard.append([button])  # One button per row
    
    # Add back button
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_denominations")])
    
    return InlineKeyboardMarkup(keyboard)

def get_check_payment_keyboard(show_qr=True):
    """
    Create a keyboard with buttons to check payment status and toggle QR code visibility.
    
    Args:
        show_qr (bool): Whether the QR code is currently shown
    """
    toggle_text = "🙈 Hide QR Code" if show_qr else "📱 Show QR Code"
    toggle_data = "hide_qr_code" if show_qr else "show_qr_code"
    
    keyboard = [
        [InlineKeyboardButton(toggle_text, callback_data=toggle_data)],
        [InlineKeyboardButton("🔄 Check Payment", callback_data="check_payment")],
        [InlineKeyboardButton("⬅️ Back to Crypto", callback_data="back_to_crypto")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard(callback_data):
    """Create a keyboard with a single back button."""
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)
