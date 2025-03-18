#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration settings for the gift card store bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))  # Admin Telegram ID
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Payment configuration
PAYMENT_CHECK_INTERVAL = 60  # seconds
PAYMENT_CONFIRMATIONS_REQUIRED = 1  # Minimum confirmations needed to consider payment successful

# Available cryptocurrencies for payment
CRYPTOCURRENCIES = {
    "BTC": {
        "name": "Bitcoin",
        "address": os.getenv("BTC_ADDRESS", ""),
        "explorer_api": "https://blockchain.info/rawaddr/"
    },
    "ETH": {
        "name": "Ethereum",
        "address": os.getenv("ETH_ADDRESS", ""),
        "explorer_api": "https://api.etherscan.io/api?module=account&action=txlist&address="
    },
    "USDT": {
        "name": "Tether (USDT)",
        "address": os.getenv("USDT_ADDRESS", ""),
        "explorer_api": "https://api.etherscan.io/api?module=account&action=tokentx&address="
    },
    "BNB": {
        "name": "Binance Coin",
        "address": os.getenv("BNB_ADDRESS", ""),
        "explorer_api": "https://api.bscscan.com/api?module=account&action=txlist&address="
    },
    "SOL": {
        "name": "Solana",
        "address": os.getenv("SOL_ADDRESS", ""),
        "explorer_api": "https://api.solscan.io/account/transactions?address="
    },
    "XRP": {
        "name": "XRP (Ripple)",
        "address": os.getenv("XRP_ADDRESS", ""),
        "explorer_api": "https://api.xrpscan.com/api/v1/account/"
    },
    "USDC": {
        "name": "USD Coin",
        "address": os.getenv("USDC_ADDRESS", ""),
        "explorer_api": "https://api.etherscan.io/api?module=account&action=tokentx&address="
    },
    "ADA": {
        "name": "Cardano",
        "address": os.getenv("ADA_ADDRESS", ""),
        "explorer_api": "https://cardanoscan.io/address/"
    },
    "DOGE": {
        "name": "Dogecoin",
        "address": os.getenv("DOGE_ADDRESS", ""),
        "explorer_api": "https://dogechain.info/api/v1/address/"
    },
    "TRX": {
        "name": "Tron",
        "address": os.getenv("TRX_ADDRESS", ""),
        "explorer_api": "https://apilist.tronscan.org/api/account?address="
    },
    "LTC": {
        "name": "Litecoin",
        "address": os.getenv("LTC_ADDRESS", ""),
        "explorer_api": "https://api.blockcypher.com/v1/ltc/main/addrs/"
    },
    "BCH": {
        "name": "Bitcoin Cash",
        "address": os.getenv("BCH_ADDRESS", ""),
        "explorer_api": "https://rest.bitcoin.com/v2/address/details/"
    },
    "TON": {
        "name": "Toncoin",
        "address": os.getenv("TON_ADDRESS", ""),
        "explorer_api": "https://toncenter.com/api/v2/getTransactions?address="
    }
}

# Default language
DEFAULT_LANGUAGE = "en"

# Available languages
LANGUAGES = {
    "en": "English",
    "ru": "Russian",
    "es": "Spanish",
    "fr": "French",
    "de": "German"
}

# Gift card discount percentage
DISCOUNT_PERCENTAGE = 45
