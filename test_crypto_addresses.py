#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify cryptocurrency addresses are loaded correctly
"""
import os
import logging
from dotenv import load_dotenv
from config import CRYPTOCURRENCIES

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def test_crypto_addresses():
    """Test if cryptocurrency addresses are loaded correctly."""
    # Load environment variables
    load_dotenv()
    
    # Print environment variable status
    for crypto in CRYPTOCURRENCIES:
        env_var = f"{crypto}_ADDRESS"
        env_value = os.getenv(env_var)
        config_value = CRYPTOCURRENCIES[crypto]["address"]
        
        print(f"{crypto}:")
        print(f"  Env var name: {env_var}")
        print(f"  Env var value: {env_value}")
        print(f"  Config value: {config_value}")
        print(f"  Match: {env_value == config_value}")
        print()
    
    # Try generating a payment address like in the actual code
    for crypto in CRYPTOCURRENCIES:
        payment_address = CRYPTOCURRENCIES[crypto]["address"]
        print(f"Payment address for {crypto}: {payment_address}")
        
        # Check if address is empty
        if not payment_address:
            print(f"WARNING: Empty payment address for {crypto}")

if __name__ == "__main__":
    test_crypto_addresses()