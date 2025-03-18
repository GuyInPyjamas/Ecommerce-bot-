#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data management functions for storing and retrieving gift card data and orders
Using PostgreSQL database with SQLAlchemy
"""
import os
import logging
import uuid
import datetime
from flask import current_app
from models import db, Country, GiftCard, Denomination, Order, User, CryptoPayment
from app import app
from config import DISCOUNT_PERCENTAGE

logger = logging.getLogger(__name__)

def format_denomination_with_discount(denomination):
    """Format a denomination value with the discounted price in brackets."""
    # Remove commas and extract the numeric value
    if '€' in denomination:
        value = float(denomination.replace('€', '').replace(',', ''))
        currency_symbol = '€'
        prefix = False  # Euro symbol comes after the number
    elif '₽' in denomination:
        value = float(denomination.replace('₽', '').replace(',', ''))
        currency_symbol = '₽'
        prefix = True   # Ruble symbol comes before the number
    elif '₺' in denomination:
        value = float(denomination.replace('₺', '').replace(',', ''))
        currency_symbol = '₺'
        prefix = True   # Lira symbol comes before the number
    elif '£' in denomination:
        value = float(denomination.replace('£', '').replace(',', ''))
        currency_symbol = '£'
        prefix = True   # Pound symbol comes before the number
    elif 'C$' in denomination:
        value = float(denomination.replace('C$', '').replace(',', ''))
        currency_symbol = 'C$'
        prefix = True   # Canadian dollar symbol comes before the number
    elif 'A$' in denomination:
        value = float(denomination.replace('A$', '').replace(',', ''))
        currency_symbol = 'A$'
        prefix = True   # Australian dollar symbol comes before the number
    elif '$' in denomination:
        value = float(denomination.replace('$', '').replace(',', ''))
        currency_symbol = '$'
        prefix = True   # Dollar symbol comes before the number
    else:
        # Default case (should not happen with our current setup)
        return denomination

    # Calculate the discounted price
    discounted_value = value * (1 - DISCOUNT_PERCENTAGE / 100)
    
    # Format with original denomination and discounted price in brackets
    if prefix:
        # For currencies with the symbol before the number (£, $, etc.)
        if value == int(value) and discounted_value == int(discounted_value):
            return f"{currency_symbol}{int(value)} ({currency_symbol}{int(discounted_value)})"
        elif value == int(value):
            return f"{currency_symbol}{int(value)} ({currency_symbol}{discounted_value:.2f})"
        else:
            return f"{currency_symbol}{value:.2f} ({currency_symbol}{discounted_value:.2f})"
    else:
        # For currencies with the symbol after the number (€)
        if value == int(value) and discounted_value == int(discounted_value):
            return f"{int(value)}{currency_symbol} ({int(discounted_value)}{currency_symbol})"
        elif value == int(value):
            return f"{int(value)}{currency_symbol} ({discounted_value:.2f}{currency_symbol})"
        else:
            return f"{value:.2f}{currency_symbol} ({discounted_value:.2f}{currency_symbol})"

def get_countries():
    """Get the list of available countries."""
    try:
        with app.app_context():
            countries = Country.query.filter_by(active=True).all()
            result = {}
            for country in countries:
                result[country.name] = {
                    "currency": country.code,
                    "flag": country.flag_emoji
                }
            return result
    except Exception as e:
        logger.error(f"Error loading countries data: {e}")
        return {}

def get_gift_cards_for_country(country):
    """Get the list of gift cards available for a specific country."""
    try:
        with app.app_context():
            country_obj = Country.query.filter_by(name=country, active=True).first()
            if not country_obj:
                return {}
            
            gift_cards = GiftCard.query.filter_by(country_id=country_obj.id, active=True).all()
            result = {}
            
            for card in gift_cards:
                # Skip Visa and Mastercard Prepaid cards for Russia
                if country == "Russia" and card.name in ["Visa Prepaid", "Mastercard Prepaid"]:
                    continue
                
                # Assign appropriate emoji based on gift card name
                logo = "🎁"  # Default gift card emoji
                
                # Map gift card names to appropriate emojis
                gift_card_emojis = {
                    "Apple": "🍎",
                    "Google Play": "🎮",
                    "Visa Prepaid": "💳",
                    "Mastercard Prepaid": "💳",
                    "PlayStation": "🎮",
                    "Xbox": "🎯",
                    "Netflix": "🎬",
                    "Spotify": "🎧",
                    # Keep other entries for backward compatibility or future use
                    "Amazon": "🛒",
                    "Steam": "🎲",
                    "iTunes": "🎵",
                    "Nintendo": "🎮",
                    "Uber": "🚗",
                    "Roblox": "👾",
                    "Starbucks": "☕",
                    "McDonald's": "🍔",
                    "Visa": "💳",
                    "Mastercard": "💳",
                    "Walmart": "🛒",
                    "Target": "🎯",
                    "eBay": "📦",
                    "Best Buy": "🖥️"
                }
                
                # Get the appropriate emoji if available, otherwise use default
                if card.name in gift_card_emojis:
                    logo = gift_card_emojis[card.name]
                
                result[card.name] = {
                    "logo": logo,
                    "denominations": []
                }
                
                # Get denominations for this card
                denominations = Denomination.query.filter_by(gift_card_id=card.id, active=True).all()
                
                # Countries that should show whole numbers
                euro_countries = ["Germany", "France", "Italy", "Spain", "Netherlands"]
                exact_value_countries = ["UK", "Canada", "Australia"] + euro_countries
                
                # Special case for countries to ensure ALL gift cards have all 5 standard denominations
                if country == "Canada":
                    standard_denoms = ["C$100", "C$200", "C$250", "C$300", "C$500"]
                    result[card.name]["denominations"] = [format_denomination_with_discount(denom) for denom in standard_denoms]
                elif country == "Australia":
                    standard_denoms = ["A$100", "A$200", "A$250", "A$300", "A$500"]
                    result[card.name]["denominations"] = [format_denomination_with_discount(denom) for denom in standard_denoms]
                elif country == "UK":
                    standard_denoms = ["£100", "£200", "£250", "£300", "£500"]
                    result[card.name]["denominations"] = [format_denomination_with_discount(denom) for denom in standard_denoms]
                elif country == "Germany":
                    standard_denoms = ["100€", "200€", "250€", "300€", "500€"]
                    result[card.name]["denominations"] = [format_denomination_with_discount(denom) for denom in standard_denoms]
                elif country == "Spain":
                    standard_denoms = ["100€", "200€", "250€", "300€", "500€"]
                    result[card.name]["denominations"] = [format_denomination_with_discount(denom) for denom in standard_denoms]
                elif country == "Netherlands":
                    standard_denoms = ["100€", "200€", "250€", "300€", "500€"]
                    result[card.name]["denominations"] = [format_denomination_with_discount(denom) for denom in standard_denoms]
                elif country == "France":
                    standard_denoms = ["100€", "200€", "250€", "300€", "500€"]
                    result[card.name]["denominations"] = [format_denomination_with_discount(denom) for denom in standard_denoms]
                elif country == "Italy":
                    standard_denoms = ["100€", "200€", "250€", "300€", "500€"]
                    result[card.name]["denominations"] = [format_denomination_with_discount(denom) for denom in standard_denoms]
                elif country == "USA":
                    standard_denoms = ["$100", "$200", "$250", "$300", "$500"]
                    result[card.name]["denominations"] = [format_denomination_with_discount(denom) for denom in standard_denoms]
                elif country == "Russia":
                    standard_denoms = ["₽10000", "₽20000", "₽25000", "₽30000", "₽50000"]
                    result[card.name]["denominations"] = [format_denomination_with_discount(denom) for denom in standard_denoms]
                elif country == "Turkey":
                    standard_denoms = ["₺10000", "₺20000", "₺25000", "₺30000", "₺50000"]
                    result[card.name]["denominations"] = [format_denomination_with_discount(denom) for denom in standard_denoms]
                else:
                    for denom in denominations:
                        # For Euro countries, put the € symbol after the number (100€)
                        if country in euro_countries and denom.value == int(denom.value):
                            formatted_denom = f"{int(denom.value)}{denom.currency_symbol}"
                            result[card.name]["denominations"].append(format_denomination_with_discount(formatted_denom))
                        # For UK, always show £ symbol before the value (£100)
                        elif country == "UK" and denom.value == int(denom.value):
                            formatted_denom = f"{denom.currency_symbol}{int(denom.value)}"
                            result[card.name]["denominations"].append(format_denomination_with_discount(formatted_denom))
                        # For Canada, always show C$ symbol before the value (C$100)
                        elif country == "Canada" and denom.value == int(denom.value):
                            formatted_denom = f"{denom.currency_symbol}{int(denom.value)}"
                            result[card.name]["denominations"].append(format_denomination_with_discount(formatted_denom))
                        # For other countries in exact_value_countries, format with whole numbers
                        elif country in exact_value_countries and denom.value == int(denom.value):
                            formatted_denom = f"{denom.currency_symbol}{int(denom.value)}"
                            result[card.name]["denominations"].append(format_denomination_with_discount(formatted_denom))
                        else:
                            # Keep default formatting for other countries or non-integer values
                            formatted_denom = f"{denom.currency_symbol}{denom.value}"
                            result[card.name]["denominations"].append(format_denomination_with_discount(formatted_denom))
            
            return result
    except Exception as e:
        logger.error(f"Error loading gift cards data: {e}")
        return {}

def get_card_denominations(country, gift_card):
    """Get the denominations available for a specific gift card in a country."""
    try:
        with app.app_context():
            country_obj = Country.query.filter_by(name=country, active=True).first()
            if not country_obj:
                return []
            
            card_obj = GiftCard.query.filter_by(
                name=gift_card, 
                country_id=country_obj.id, 
                active=True
            ).first()
            
            if not card_obj:
                return []
            
            denominations = Denomination.query.filter_by(
                gift_card_id=card_obj.id, 
                active=True
            ).all()
            
            # Countries that need to show whole numbers for denominations (100€, £100, etc. instead of decimal values)
            euro_countries = ["Germany", "France", "Italy", "Spain", "Netherlands"]
            exact_value_countries = ["UK", "Canada", "Australia"] + euro_countries
            
            # Special case for countries to ensure ALL gift cards have all 5 standard denominations
            if country == "Canada":
                # For all Canadian gift cards, use the standardized denominations with discounted prices
                standard_denoms = ["C$100", "C$200", "C$250", "C$300", "C$500"]
                return [format_denomination_with_discount(denom) for denom in standard_denoms]
            elif country == "Australia":
                # For all Australian gift cards, use the standardized denominations with discounted prices
                standard_denoms = ["A$100", "A$200", "A$250", "A$300", "A$500"]
                return [format_denomination_with_discount(denom) for denom in standard_denoms]
            elif country == "UK":
                # For all UK gift cards, use the standardized denominations with discounted prices
                standard_denoms = ["£100", "£200", "£250", "£300", "£500"]
                return [format_denomination_with_discount(denom) for denom in standard_denoms]
            elif country == "Germany":
                # For all German gift cards, use the standardized denominations with discounted prices
                standard_denoms = ["100€", "200€", "250€", "300€", "500€"]
                return [format_denomination_with_discount(denom) for denom in standard_denoms]
            elif country == "Spain":
                # For all Spanish gift cards, use the standardized denominations with discounted prices
                standard_denoms = ["100€", "200€", "250€", "300€", "500€"]
                return [format_denomination_with_discount(denom) for denom in standard_denoms]
            elif country == "Netherlands":
                # For all Dutch gift cards, use the standardized denominations with discounted prices
                standard_denoms = ["100€", "200€", "250€", "300€", "500€"]
                return [format_denomination_with_discount(denom) for denom in standard_denoms]
            elif country == "USA":
                # For all USA gift cards, use the standardized denominations with discounted prices
                standard_denoms = ["$100", "$200", "$250", "$300", "$500"]
                return [format_denomination_with_discount(denom) for denom in standard_denoms]
            elif country == "France":
                # For all French gift cards, use the standardized denominations with discounted prices
                standard_denoms = ["100€", "200€", "250€", "300€", "500€"]
                return [format_denomination_with_discount(denom) for denom in standard_denoms]
            elif country == "Italy":
                # For all Italian gift cards, use the standardized denominations with discounted prices
                standard_denoms = ["100€", "200€", "250€", "300€", "500€"]
                return [format_denomination_with_discount(denom) for denom in standard_denoms]
            elif country == "Russia":
                # For all Russian gift cards, use higher denominations with discounted prices
                standard_denoms = ["₽10000", "₽20000", "₽25000", "₽30000", "₽50000"]
                return [format_denomination_with_discount(denom) for denom in standard_denoms]
            elif country == "Turkey":
                # For all Turkish gift cards, use higher denominations with discounted prices
                standard_denoms = ["₺10000", "₺20000", "₺25000", "₺30000", "₺50000"]
                return [format_denomination_with_discount(denom) for denom in standard_denoms]
            elif country in exact_value_countries:
                # Format denominations as integers (without decimal places) for countries that need exact values
                formatted_denominations = []
                for denom in denominations:
                    # For Euro countries, put the € symbol after the number (100€)
                    if country in euro_countries:
                        if denom.value == int(denom.value):
                            formatted_denom = f"{int(denom.value)}{denom.currency_symbol}"
                            formatted_denominations.append(format_denomination_with_discount(formatted_denom))
                        else:
                            formatted_denom = f"{denom.value}{denom.currency_symbol}"
                            formatted_denominations.append(format_denomination_with_discount(formatted_denom))
                    # For UK, always show £ symbol before the value (£100)
                    elif country == "UK":
                        if denom.value == int(denom.value):
                            formatted_denom = f"{denom.currency_symbol}{int(denom.value)}"
                            formatted_denominations.append(format_denomination_with_discount(formatted_denom))
                        else:
                            formatted_denom = f"{denom.currency_symbol}{denom.value}"
                            formatted_denominations.append(format_denomination_with_discount(formatted_denom))
                    # For Canada, always show C$ symbol before the value (C$100)
                    elif country == "Canada":
                        if denom.value == int(denom.value):
                            formatted_denom = f"{denom.currency_symbol}{int(denom.value)}"
                            formatted_denominations.append(format_denomination_with_discount(formatted_denom))
                        else:
                            formatted_denom = f"{denom.currency_symbol}{denom.value}"
                            formatted_denominations.append(format_denomination_with_discount(formatted_denom))
                    # For other countries (Australia), keep symbols before the value
                    else:
                        if denom.value == int(denom.value):
                            formatted_denom = f"{denom.currency_symbol}{int(denom.value)}"
                            formatted_denominations.append(format_denomination_with_discount(formatted_denom))
                        else:
                            formatted_denom = f"{denom.currency_symbol}{denom.value}"
                            formatted_denominations.append(format_denomination_with_discount(formatted_denom))
                return formatted_denominations
            else:
                # For other countries, maintain the original formatting but add discounted values
                return [format_denomination_with_discount(f"{denom.currency_symbol}{denom.value}") 
                        for denom in denominations]
    except Exception as e:
        logger.error(f"Error loading gift card denominations: {e}")
        return []

def save_order(order_data):
    """Save a new order to the database."""
    try:
        with app.app_context():
            # Extract original price from the order data if available, otherwise use 0.0
            original_price = order_data.get("original_price", 0.0)
            
            # Create a new order
            order = Order(
                order_id=order_data.get("order_id", str(uuid.uuid4())),
                user_id=str(order_data.get("user_id")),
                user_name=order_data.get("user_name"),
                country=order_data.get("country"),
                gift_card=order_data.get("gift_card"),
                denomination=order_data.get("denomination"),
                original_price=original_price,
                discounted_price=order_data.get("discounted_price", 0.0),
                crypto=order_data.get("crypto"),
                crypto_amount=order_data.get("crypto_amount", 0.0),
                payment_address=order_data.get("payment_address"),
                status=order_data.get("status", "pending")
            )
            
            db.session.add(order)
            db.session.commit()
            
            # Create a payment record if it doesn't exist
            payment = CryptoPayment.query.filter_by(order_id=order.order_id).first()
            if not payment:
                payment = CryptoPayment(
                    order_id=order.order_id,
                    crypto=order_data.get("crypto"),
                    amount=order_data.get("crypto_amount", 0.0),
                    status="pending"
                )
                db.session.add(payment)
                db.session.commit()
            
            return True
    except Exception as e:
        try:
            with app.app_context():
                db.session.rollback()
        except:
            pass
        logger.error(f"Error saving order: {e}")
        return False

def get_order(order_id):
    """Get a specific order by its ID."""
    try:
        with app.app_context():
            order = Order.query.filter_by(order_id=order_id).first()
            if order:
                return order.to_dict()
            return None
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        return None

def get_payment_status(order_id):
    """
    Get detailed payment status for an order.
    
    Args:
        order_id (str): The order ID.
        
    Returns:
        dict: Payment status information including transaction details or None if not found.
    """
    try:
        with app.app_context():
            order = Order.query.filter_by(order_id=order_id).first()
            if not order:
                return None
                
            # Get payment information if it exists
            payment = CryptoPayment.query.filter_by(order_id=order_id).first()
            
            result = {
                "order_id": order_id,
                "status": order.status,
                "crypto": order.crypto,
                "amount": order.crypto_amount,
                "address": order.payment_address,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            }
            
            # Add payment details if available
            if payment:
                result.update({
                    "transaction_id": payment.transaction_id,
                    "confirmations": payment.confirmations,
                    "payment_status": payment.status,
                    "confirmed_at": payment.confirmed_at.isoformat() if payment.confirmed_at else None
                })
            else:
                result.update({
                    "transaction_id": None,
                    "confirmations": 0,
                    "payment_status": "pending",
                    "confirmed_at": None
                })
                
            return result
            
    except Exception as e:
        logger.error(f"Error getting payment status for order {order_id}: {e}")
        return None

def get_user_orders(user_id):
    """Get all orders for a specific user."""
    try:
        with app.app_context():
            orders = Order.query.filter_by(user_id=str(user_id)).order_by(Order.created_at.desc()).all()
            return [order.to_dict() for order in orders]
    except Exception as e:
        logger.error(f"Error getting user orders: {e}")
        return []

def get_all_orders():
    """Get all orders in the system."""
    try:
        with app.app_context():
            orders = Order.query.order_by(Order.created_at.desc()).all()
            return [order.to_dict() for order in orders]
    except Exception as e:
        logger.error(f"Error getting all orders: {e}")
        return []

def save_crypto_payment(order_id, tx_data):
    """
    Save or update a cryptocurrency payment transaction.
    
    Args:
        order_id (str): The order ID.
        tx_data (dict): Transaction data including transaction_id, amount, confirmations, etc.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with app.app_context():
            # Check if a payment record already exists for this order
            payment = CryptoPayment.query.filter_by(order_id=order_id).first()
            
            if not payment:
                # Create a new payment record
                order = Order.query.filter_by(order_id=order_id).first()
                if not order:
                    logger.error(f"Order {order_id} not found.")
                    return False
                
                payment = CryptoPayment(
                    order_id=order_id,
                    crypto=order.crypto,
                    amount=order.crypto_amount,
                    status="pending"
                )
                db.session.add(payment)
            
            # Update payment with transaction data
            if 'transaction_id' in tx_data:
                payment.transaction_id = tx_data['transaction_id']
            
            if 'confirmations' in tx_data:
                payment.confirmations = tx_data['confirmations']
            
            if 'status' in tx_data:
                payment.status = tx_data['status']
                if tx_data['status'] == "confirmed" and not payment.confirmed_at:
                    payment.confirmed_at = datetime.datetime.utcnow()
            
            db.session.commit()
            return True
    
    except Exception as e:
        logger.error(f"Error saving crypto payment: {e}")
        return False

def update_order_status(order_id, status, gift_card_code=None):
    """Update the status of an order."""
    try:
        with app.app_context():
            order = Order.query.filter_by(order_id=order_id).first()
            if order:
                order.status = status
                if gift_card_code:
                    order.gift_card_code = gift_card_code
                order.updated_at = datetime.datetime.utcnow()
                
                # Also update the crypto payment if it exists
                if status == "completed":
                    payment = CryptoPayment.query.filter_by(order_id=order_id).first()
                    if payment:
                        payment.status = "confirmed"
                        payment.confirmed_at = datetime.datetime.utcnow()
                
                db.session.commit()
                return True
            return False
    except Exception as e:
        try:
            with app.app_context():
                db.session.rollback()
        except:
            pass
        logger.error(f"Error updating order status: {e}")
        return False

def cancel_order(order_id):
    """Cancel an order by changing its status to 'cancelled'."""
    return update_order_status(order_id, "cancelled")

def get_or_create_user(telegram_id, username=None, first_name=None, last_name=None, language_code=None):
    """Get an existing user or create a new one."""
    try:
        with app.app_context():
            user = User.query.filter_by(telegram_id=str(telegram_id)).first()
            if not user:
                # Create new user
                user = User(
                    telegram_id=str(telegram_id),
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    language_code=language_code or 'en',
                    is_admin=(str(telegram_id) == os.environ.get('ADMIN_USER_ID', ''))
                )
                db.session.add(user)
                db.session.commit()
            else:
                # Update existing user data
                if username and username != user.username:
                    user.username = username
                if first_name and first_name != user.first_name:
                    user.first_name = first_name
                if last_name and last_name != user.last_name:
                    user.last_name = last_name
                if language_code and language_code != user.language_code:
                    user.language_code = language_code
                    
                user.last_activity = datetime.datetime.utcnow()
                db.session.commit()
                
            return user
    except Exception as e:
        try:
            with app.app_context():
                db.session.rollback()
        except:
            pass
        logger.error(f"Error getting or creating user: {e}")
        return None
