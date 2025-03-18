#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Payment processing functions for cryptocurrency transactions
"""
import os
import uuid
import json
import logging
import requests
from datetime import datetime
from config import CRYPTOCURRENCIES, DISCOUNT_PERCENTAGE
from data_manager import save_order, get_order, update_order_status, get_payment_status, save_crypto_payment

logger = logging.getLogger(__name__)

# CoinMarketCap API configuration
CMC_API_KEY = os.getenv("COINMARKETCAP_API_KEY")
CMC_API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

# Cache for cryptocurrency prices (5 minutes)
CRYPTO_PRICE_CACHE = {}
CACHE_DURATION = 300  # 5 minutes in seconds

def get_live_crypto_price(crypto):
    """Get live cryptocurrency price from CoinMarketCap API."""
    now = datetime.now().timestamp()
    
    # Check cache first
    if crypto in CRYPTO_PRICE_CACHE:
        cached_price, cached_time = CRYPTO_PRICE_CACHE[crypto]
        if now - cached_time < CACHE_DURATION:
            return cached_price
    
    # Prepare API request
    headers = {
        "X-CMC_PRO_API_KEY": CMC_API_KEY,
        "Accept": "application/json"
    }
    
    # Map our crypto symbols to CoinMarketCap IDs if needed
    symbol_map = {
        "TON": "TONCOIN",  # Handle special cases
    }
    
    symbol = symbol_map.get(crypto, crypto)
    
    params = {
        "symbol": symbol,
        "convert": "USD"
    }
    
    try:
        response = requests.get(CMC_API_URL, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and symbol in data["data"]:
                price = float(data["data"][symbol]["quote"]["USD"]["price"])
                # Cache the price
                CRYPTO_PRICE_CACHE[crypto] = (price, now)
                return price
            else:
                logger.error(f"Invalid response format from CoinMarketCap API for {crypto}")
                return None
        else:
            logger.error(f"CoinMarketCap API error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching {crypto} price from CoinMarketCap: {str(e)}")
        return None

def get_crypto_price(crypto, usd_amount):
    """Calculate the cryptocurrency amount based on live USD price."""
    try:
        logger.info(f"Getting price for {crypto}, amount: {usd_amount}...")
        crypto_price = get_live_crypto_price(crypto)
        
        if crypto_price is None:
            logger.error(f"Could not get price for cryptocurrency: {crypto}")
            # Fallback to static prices for reliability
            fallback_prices = {
                "BTC": 50000, "ETH": 3000, "USDT": 1, "BNB": 380, "SOL": 120,
                "XRP": 0.50, "USDC": 1, "ADA": 0.40, "DOGE": 0.08, "TRX": 0.10,
                "LTC": 150, "BCH": 400, "TON": 5.50
            }
            
            if crypto in fallback_prices:
                logger.warning(f"Using fallback price for {crypto}: {fallback_prices[crypto]}")
                crypto_price = fallback_prices[crypto]
            else:
                return None
        
        # Convert USD to crypto
        crypto_amount = usd_amount / crypto_price
        logger.info(f"Calculated amount: {crypto_amount} {crypto} for ${usd_amount}")
        
    except Exception as e:
        logger.error(f"Error in get_crypto_price: {str(e)}")
        return None
    
    # Round to appropriate decimal places
    if crypto == "BTC":
        return round(crypto_amount, 8)  # BTC uses 8 decimal places
    elif crypto in ["ETH", "LTC", "BNB", "SOL", "BCH"]:
        return round(crypto_amount, 6)  # ETH, LTC, BNB, SOL, BCH use 6 decimal places
    elif crypto in ["XRP", "ADA", "DOGE", "TRX", "TON"]:
        return round(crypto_amount, 4)  # XRP, ADA, DOGE, TRX, TON use 4 decimal places
    else:
        return round(crypto_amount, 2)  # USDT, USDC use 2 decimal places

def parse_denomination(denomination):
    """Parse denomination value to get numeric value and currency symbol."""
    # Remove commas
    cleaned = denomination.replace(',', '')
    
    # Check if the denomination has a format like "$100 ($55.00)"
    # This happens when a denomination with discount is passed
    if '(' in cleaned:
        # Extract just the original amount before the bracket
        cleaned = cleaned.split('(')[0].strip()
    
    # Handle all currency formats
    if 'C$' in cleaned:
        return float(cleaned.replace('C$', '')), 'C$'
    elif 'A$' in cleaned:
        return float(cleaned.replace('A$', '')), 'A$'
    elif '$' in cleaned:
        return float(cleaned.replace('$', '')), '$'
    elif '€' in cleaned:
        return float(cleaned.replace('€', '')), '€'
    elif '₽' in cleaned:
        return float(cleaned.replace('₽', '')), '₽'
    elif '₺' in cleaned:
        return float(cleaned.replace('₺', '')), '₺'
    elif '£' in cleaned:
        return float(cleaned.replace('£', '')), '£'
    else:
        # For cases where there's no currency symbol but just a number
        # or formats like "C100" (without the $ symbol)
        if cleaned.startswith('C') and cleaned[1:].isdigit():
            return float(cleaned[1:]), 'C$'  # Canadian Dollar
        elif cleaned.startswith('A') and cleaned[1:].isdigit():
            return float(cleaned[1:]), 'A$'  # Australian Dollar
        else:
            # Default case, assume USD
            try:
                return float(cleaned), '$'
            except ValueError:
                # Log the error for debugging
                logger.error(f"Failed to parse denomination: {denomination}, cleaned: {cleaned}")
                # Return a default to prevent complete failure
                return 100.0, '$'

def calculate_discounted_price(denomination):
    """Calculate discounted price based on denomination."""
    amount, currency = parse_denomination(denomination)
    
    # Calculate discount
    discounted_amount = amount * (1 - DISCOUNT_PERCENTAGE / 100)
    
    # Convert to USD for payment processing
    # In a real app, would use exchange rates API for accurate conversion
    if currency == '€':
        usd_amount = discounted_amount * 1.1  # Example EUR to USD conversion
    elif currency == '₽':
        usd_amount = discounted_amount * 0.01  # Example RUB to USD conversion
    elif currency == '₺':
        usd_amount = discounted_amount * 0.03  # Example TRY to USD conversion
    elif currency == '£':
        usd_amount = discounted_amount * 1.28  # Example GBP to USD conversion
    else:
        usd_amount = discounted_amount  # USD remains the same
    
    return round(usd_amount, 2)

def generate_payment_invoice(user_id, country, gift_card, denomination, crypto):
    """Generate a payment invoice for the order."""
    # Generate a unique order ID
    order_id = str(uuid.uuid4())
    
    # Parse denomination to get amount and currency
    amount, currency_symbol = parse_denomination(denomination)
    
    # Calculate discounted price in USD
    discounted_price = calculate_discounted_price(denomination)
    
    # Calculate original discounted amount (before conversion to USD)
    original_discounted_amount = amount * (1 - DISCOUNT_PERCENTAGE / 100)
    
    # Calculate crypto amount based on USD price
    crypto_amount = get_crypto_price(crypto, discounted_price)
    
    # Get payment address for the selected cryptocurrency
    payment_address = CRYPTOCURRENCIES[crypto]["address"]
    
    # Create invoice data
    invoice = {
        "order_id": order_id,
        "user_id": user_id,
        "date": datetime.now().isoformat(),
        "country": country,
        "gift_card": gift_card,
        "denomination": denomination,
        "original_price": amount,
        "currency_symbol": currency_symbol,
        "original_discounted_amount": round(original_discounted_amount, 2),
        "discounted_price": discounted_price,  # USD equivalent for payment
        "crypto": crypto,
        "crypto_amount": crypto_amount,
        "payment_address": payment_address,
        "status": "pending"
    }
    
    # Save order to database
    save_order(invoice)
    
    return invoice

def check_payment(order_id):
    """
    Check if a payment has been received for an order.
    
    Args:
        order_id (str): The order ID to check payment for.
        
    Returns:
        dict or bool: Payment status information including transaction details if found,
                      True if payment is confirmed, False if payment not found or error.
    """
    # Get order details
    order = get_order(order_id)
    if not order:
        logger.error(f"Order not found: {order_id}")
        return False
    
    crypto = order["crypto"]
    address = order["payment_address"]
    expected_amount = float(order["crypto_amount"])
    
    # Check if the order is already completed
    if order["status"] == "completed":
        payment_status = get_payment_status(order_id)
        if payment_status:
            return payment_status
        return True  # Order is completed even if payment details not found
    
    # Configure API endpoints based on cryptocurrency
    if crypto == "BTC":
        try:
            # Query blockchain.info API
            response = requests.get(f"https://blockchain.info/rawaddr/{address}")
            if response.status_code != 200:
                logger.error(f"Error from blockchain.info API: {response.status_code}")
                return False
                
            data = response.json()
            
            # Check recent transactions
            for tx in data.get("txs", []):
                # Find incoming transactions
                for output in tx.get("out", []):
                    if output.get("addr") == address:
                        # Convert satoshis to BTC
                        amount = float(output.get("value", 0)) / 100000000
                        if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                            # Get confirmation status
                            confirmations = tx.get("confirmations", 0)
                            required_confirmations = int(os.getenv("PAYMENT_CONFIRMATIONS_REQUIRED", "1"))
                            
                            # Create transaction data
                            tx_data = {
                                "transaction_id": tx.get("hash", ""),
                                "confirmations": confirmations,
                                "status": "pending"
                            }
                            
                            # Check if confirmations are enough
                            if confirmations >= required_confirmations:
                                tx_data["status"] = "confirmed"
                                
                                # Update order with gift card code
                                gift_card_code = f"GIFT-{order_id[:8]}"
                                update_order_status(order_id, "completed", gift_card_code)
                            
                            # Save transaction data
                            save_crypto_payment(order_id, tx_data)
                            
                            # Return payment status info
                            payment_status = get_payment_status(order_id)
                            if payment_status:
                                return payment_status
                            
                            # If payment status not available but confirmed, return True
                            if tx_data["status"] == "confirmed":
                                return True
                                
                            # If pending, return status object
                            return {
                                "order_id": order_id,
                                "status": "pending",
                                "confirmations": confirmations,
                                "required_confirmations": required_confirmations,
                                "transaction_id": tx_data["transaction_id"]
                            }
            
            return False
        except Exception as e:
            logger.error(f"Error checking BTC payment: {e}")
            return False
    
    elif crypto == "ETH":
        try:
            # Use Etherscan API
            api_key = os.getenv("ETHERSCAN_API_KEY", "")
            api_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&apikey={api_key}"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Error from Etherscan API: {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "1":
                logger.error(f"Etherscan API error: {data.get('message')}")
                return False
                
            transactions = data.get("result", [])
            
            for tx in transactions:
                if tx.get("to", "").lower() == address.lower():
                    # Convert wei to ETH
                    amount = float(tx.get("value", 0)) / 1e18
                    if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                        # Get confirmation status
                        confirmations = int(tx.get("confirmations", 0))
                        required_confirmations = int(os.getenv("PAYMENT_CONFIRMATIONS_REQUIRED", "1"))
                        
                        # Create transaction data
                        tx_data = {
                            "transaction_id": tx.get("hash", ""),
                            "confirmations": confirmations,
                            "status": "pending"
                        }
                        
                        # Check if confirmations are enough
                        if confirmations >= required_confirmations:
                            tx_data["status"] = "confirmed"
                            
                            # Update order with gift card code
                            gift_card_code = f"GIFT-{order_id[:8]}"
                            update_order_status(order_id, "completed", gift_card_code)
                        
                        # Save transaction data
                        save_crypto_payment(order_id, tx_data)
                        
                        # Return payment status info
                        payment_status = get_payment_status(order_id)
                        if payment_status:
                            return payment_status
                        
                        # If payment status not available but confirmed, return True
                        if tx_data["status"] == "confirmed":
                            return True
                            
                        # If pending, return status object
                        return {
                            "order_id": order_id,
                            "status": "pending",
                            "confirmations": confirmations,
                            "required_confirmations": required_confirmations,
                            "transaction_id": tx_data["transaction_id"]
                        }
            
            return False
        except Exception as e:
            logger.error(f"Error checking ETH payment: {e}")
            return False
    
    elif crypto == "USDT":
        try:
            # USDT on Ethereum (ERC-20)
            api_key = os.getenv("ETHERSCAN_API_KEY", "")
            contract_address = "0xdac17f958d2ee523a2206206994597c13d831ec7"  # USDT contract
            api_url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={contract_address}&address={address}&apikey={api_key}"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Error from Etherscan API: {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "1":
                logger.error(f"Etherscan API error: {data.get('message')}")
                return False
                
            transactions = data.get("result", [])
            
            for tx in transactions:
                if tx.get("to", "").lower() == address.lower():
                    # Convert to USDT (6 decimals)
                    amount = float(tx.get("value", 0)) / 1e6
                    if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                        # Get confirmation status
                        confirmations = int(tx.get("confirmations", 0))
                        required_confirmations = int(os.getenv("PAYMENT_CONFIRMATIONS_REQUIRED", "1"))
                        
                        # Create transaction data
                        tx_data = {
                            "transaction_id": tx.get("hash", ""),
                            "confirmations": confirmations,
                            "status": "pending"
                        }
                        
                        # Check if confirmations are enough
                        if confirmations >= required_confirmations:
                            tx_data["status"] = "confirmed"
                            
                            # Update order with gift card code
                            gift_card_code = f"GIFT-{order_id[:8]}"
                            update_order_status(order_id, "completed", gift_card_code)
                        
                        # Save transaction data
                        save_crypto_payment(order_id, tx_data)
                        
                        # Return payment status info
                        payment_status = get_payment_status(order_id)
                        if payment_status:
                            return payment_status
                        
                        # If payment status not available but confirmed, return True
                        if tx_data["status"] == "confirmed":
                            return True
                            
                        # If pending, return status object
                        return {
                            "order_id": order_id,
                            "status": "pending",
                            "confirmations": confirmations,
                            "required_confirmations": required_confirmations,
                            "transaction_id": tx_data["transaction_id"]
                        }
            
            return False
        except Exception as e:
            logger.error(f"Error checking USDT payment: {e}")
            return False
    
    elif crypto == "LTC":
        try:
            # Use BlockCypher API for Litecoin
            api_url = f"https://api.blockcypher.com/v1/ltc/main/addrs/{address}"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Error from BlockCypher API: {response.status_code}")
                return False
                
            data = response.json()
            
            # Check transactions
            for tx in data.get("txrefs", []):
                if not tx.get("spent", True):  # Unspent output
                    amount = float(tx.get("value", 0)) / 1e8  # Convert satoshis to LTC
                    if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                        # Check confirmations
                        if int(tx.get("confirmations", 0)) >= int(os.getenv("PAYMENT_CONFIRMATIONS_REQUIRED", "1")):
                            # Store transaction ID
                            tx_id = tx.get("tx_hash", "")
                            # Update order status with gift card code
                            gift_card_code = f"GIFT-{order_id[:8]}"
                            update_order_status(order_id, "completed", gift_card_code)
                            return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking LTC payment: {e}")
            return False
    
    elif crypto == "BNB":
        try:
            # Use BscScan API for Binance Smart Chain
            api_key = os.getenv("BSCSCAN_API_KEY", "")
            api_url = f"https://api.bscscan.com/api?module=account&action=txlist&address={address}&apikey={api_key}"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Error from BscScan API: {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "1":
                logger.error(f"BscScan API error: {data.get('message')}")
                return False
                
            transactions = data.get("result", [])
            
            for tx in transactions:
                if tx.get("to", "").lower() == address.lower():
                    # Convert wei to BNB
                    amount = float(tx.get("value", 0)) / 1e18
                    if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                        # Check confirmations
                        if int(tx.get("confirmations", 0)) >= int(os.getenv("PAYMENT_CONFIRMATIONS_REQUIRED", "1")):
                            # Store transaction ID
                            tx_id = tx.get("hash", "")
                            # Update order status with gift card code
                            gift_card_code = f"GIFT-{order_id[:8]}"
                            update_order_status(order_id, "completed", gift_card_code)
                            return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking BNB payment: {e}")
            return False
    
    elif crypto == "SOL":
        try:
            # Use Solscan API for Solana
            api_url = f"https://api.solscan.io/account/transactions?account={address}"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Error from Solscan API: {response.status_code}")
                return False
                
            data = response.json()
            
            # Check transactions
            for tx in data.get("data", []):
                if tx.get("status") == "Success":
                    # Check if transaction is a lamport transfer to our address
                    if tx.get("type") == "SOL_TRANSFER" and tx.get("dstAddress") == address:
                        # Convert lamports to SOL
                        amount = float(tx.get("lamport", 0)) / 1e9
                        if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                            # Update order status with gift card code
                            gift_card_code = f"GIFT-{order_id[:8]}"
                            update_order_status(order_id, "completed", gift_card_code)
                            return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking SOL payment: {e}")
            return False
    
    elif crypto == "XRP":
        try:
            # Use XRP API for Ripple
            api_url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Error from XRP API: {response.status_code}")
                return False
                
            transactions = response.json()
            
            # Check transactions
            for tx in transactions:
                # Check if this is a payment and it's successful
                if tx.get("type") == "Payment" and tx.get("status") == "tesSUCCESS":
                    if tx.get("Destination") == address:
                        amount = float(tx.get("Amount", 0)) / 1e6
                        if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                            # Update order status with gift card code
                            gift_card_code = f"GIFT-{order_id[:8]}"
                            update_order_status(order_id, "completed", gift_card_code)
                            return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking XRP payment: {e}")
            return False
    
    elif crypto == "USDC":
        try:
            # USDC on Ethereum (ERC-20)
            api_key = os.getenv("ETHERSCAN_API_KEY", "")
            contract_address = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"  # USDC contract
            api_url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={contract_address}&address={address}&apikey={api_key}"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Error from Etherscan API: {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "1":
                logger.error(f"Etherscan API error: {data.get('message')}")
                return False
                
            transactions = data.get("result", [])
            
            for tx in transactions:
                if tx.get("to", "").lower() == address.lower():
                    # Convert to USDC (6 decimals)
                    amount = float(tx.get("value", 0)) / 1e6
                    if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                        # Get confirmation status
                        confirmations = int(tx.get("confirmations", 0))
                        required_confirmations = int(os.getenv("PAYMENT_CONFIRMATIONS_REQUIRED", "1"))
                        
                        # Create transaction data
                        tx_data = {
                            "transaction_id": tx.get("hash", ""),
                            "confirmations": confirmations,
                            "status": "pending"
                        }
                        
                        # Check if confirmations are enough
                        if confirmations >= required_confirmations:
                            tx_data["status"] = "confirmed"
                            
                            # Update order with gift card code
                            gift_card_code = f"GIFT-{order_id[:8]}"
                            update_order_status(order_id, "completed", gift_card_code)
                        
                        # Save transaction data
                        save_crypto_payment(order_id, tx_data)
                        
                        # Return payment status info
                        payment_status = get_payment_status(order_id)
                        if payment_status:
                            return payment_status
                        
                        # If payment status not available but confirmed, return True
                        if tx_data["status"] == "confirmed":
                            return True
                            
                        # If pending, return status object
                        return {
                            "order_id": order_id,
                            "status": "pending",
                            "confirmations": confirmations,
                            "required_confirmations": required_confirmations,
                            "transaction_id": tx_data["transaction_id"]
                        }
            
            return False
        except Exception as e:
            logger.error(f"Error checking USDC payment: {e}")
            return False
    
    elif crypto == "ADA":
        try:
            # Use Cardanoscan API for Cardano
            api_url = f"https://cardanoscan.io/api/transaction/{address}"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Error from Cardanoscan API: {response.status_code}")
                return False
                
            data = response.json()
            
            # Check transactions
            for tx in data.get("transactions", []):
                # Check outputs for payments to our address
                for output in tx.get("outputs", []):
                    if output.get("address") == address:
                        # Convert lovelace to ADA
                        amount = float(output.get("value", 0)) / 1e6
                        if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                            # Update order status with gift card code
                            gift_card_code = f"GIFT-{order_id[:8]}"
                            update_order_status(order_id, "completed", gift_card_code)
                            return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking ADA payment: {e}")
            return False
    
    elif crypto == "DOGE":
        try:
            # Use Dogechain API for Dogecoin
            api_url = f"https://dogechain.info/api/v1/address/transactions/{address}"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Error from Dogechain API: {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("success") != 1:
                logger.error(f"Dogechain API error: {data.get('error')}")
                return False
                
            transactions = data.get("transactions", [])
            
            # Check transactions
            for tx in transactions:
                # Check if this is an incoming transaction
                if tx.get("direction") == "incoming":
                    amount = float(tx.get("value", 0))
                    if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                        # Check confirmations
                        if int(tx.get("confirmations", 0)) >= int(os.getenv("PAYMENT_CONFIRMATIONS_REQUIRED", "1")):
                            # Update order status with gift card code
                            gift_card_code = f"GIFT-{order_id[:8]}"
                            update_order_status(order_id, "completed", gift_card_code)
                            return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking DOGE payment: {e}")
            return False
    
    elif crypto == "TRX":
        try:
            # Use Tronscan API for Tron
            api_url = f"https://apilist.tronscan.org/api/transaction?address={address}&direction=in"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Error from Tronscan API: {response.status_code}")
                return False
                
            data = response.json()
            
            # Check transactions
            for tx in data.get("data", []):
                # Check if this is a successful transaction to our address
                if tx.get("toAddress") == address and tx.get("confirmed"):
                    amount = float(tx.get("amount", 0)) / 1e6
                    if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                        # Update order status with gift card code
                        gift_card_code = f"GIFT-{order_id[:8]}"
                        update_order_status(order_id, "completed", gift_card_code)
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking TRX payment: {e}")
            return False
    
    elif crypto == "BCH":
        try:
            # Use Bitcoin.com API for Bitcoin Cash
            api_url = f"https://rest.bitcoin.com/v2/address/details/{address}"
            
            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Error from Bitcoin.com API: {response.status_code}")
                return False
                
            data = response.json()
            
            # Check transactions
            for tx in data.get("transactions", []):
                # Use Blockchain.com API to get transaction details
                tx_url = f"https://rest.bitcoin.com/v2/transaction/details/{tx}"
                
                tx_response = requests.get(tx_url)
                if tx_response.status_code != 200:
                    continue
                    
                tx_data = tx_response.json()
                
                # Check outputs
                for output in tx_data.get("vout", []):
                    # Check if the output is to our address
                    if address in output.get("scriptPubKey", {}).get("addresses", []):
                        amount = float(output.get("value", 0))
                        if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                            # Check confirmations
                            if int(tx_data.get("confirmations", 0)) >= int(os.getenv("PAYMENT_CONFIRMATIONS_REQUIRED", "1")):
                                # Update order status with gift card code
                                gift_card_code = f"GIFT-{order_id[:8]}"
                                update_order_status(order_id, "completed", gift_card_code)
                                return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking BCH payment: {e}")
            return False
    
    elif crypto == "TON":
        try:
            # Use Toncenter API for TON
            api_key = os.getenv("TONCENTER_API_KEY", "")
            headers = {"X-API-Key": api_key} if api_key else {}
            api_url = f"https://toncenter.com/api/v2/getTransactions?address={address}&limit=10"
            
            response = requests.get(api_url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Error from Toncenter API: {response.status_code}")
                return False
                
            data = response.json()
            
            if not data.get("ok", False):
                logger.error(f"Toncenter API error: {data.get('error')}")
                return False
                
            transactions = data.get("result", [])
            
            # Check transactions
            for tx in transactions:
                # Check if this is an incoming transaction
                if tx.get("in_msg", {}).get("destination") == address:
                    # TON uses nanograms (1 TON = 1e9 nanograms)
                    amount = float(tx.get("in_msg", {}).get("value", 0)) / 1e9
                    if amount >= expected_amount * 0.99:  # Allow 1% tolerance
                        # Update order status with gift card code
                        gift_card_code = f"GIFT-{order_id[:8]}"
                        update_order_status(order_id, "completed", gift_card_code)
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking TON payment: {e}")
            return False
    
    # For demo purposes, if environment variables are missing, simulate payment
    # This should be removed in production
    if not address or address == "" or "ADDRESS" not in os.environ:
        logger.warning("No cryptocurrency addresses configured. Simulating successful payment for demo.")
        gift_card_code = f"DEMO-GIFT-{order_id[:8]}"
        update_order_status(order_id, "completed", gift_card_code)
        return True
    
    logger.error(f"Unsupported cryptocurrency: {crypto}")
    return False
