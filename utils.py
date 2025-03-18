#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility functions for the Telegram bot
"""
import qrcode
import io
from io import StringIO, BytesIO
import os

def generate_qr_code_image(data, size=8):
    """
    Generate a QR code for the given data and return it as an image file.
    
    Args:
        data: The data to encode in the QR code
        size: The box size of the QR code (default: 8)
        
    Returns:
        BytesIO: QR code image in PNG format
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create an image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image to BytesIO
    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    
    return bio

def generate_qr_code(data, size=10):
    """
    Generate a QR code for the given data and return it as ASCII art.
    (Kept for backward compatibility)
    
    Args:
        data: The data to encode in the QR code
        size: The size of the QR code (default: 10)
        
    Returns:
        str: ASCII representation of the QR code
    """
    qr = qrcode.QRCode(
        version=1,
        box_size=1,
        border=1
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create a more compact ASCII representation
    output = StringIO()
    modules = qr.get_matrix()
    
    for row in modules:
        for cell in row:
            if cell:
                output.write("█")  # Single character black module
            else:
                output.write(" ")  # Single character white module
        output.write("\n")
    
    return output.getvalue()

def format_price(amount, currency="$"):
    """
    Format a price with the given currency symbol.
    For Euro and some other currencies, the symbol is displayed after the amount.
    For other currencies, the symbol is displayed before the amount.
    """
    if currency in ["€"]:
        return f"{amount:,.2f}{currency}"
    else:
        return f"{currency}{amount:,.2f}"

def validate_payment_address(address, crypto):
    """
    Validate that a cryptocurrency address is in the correct format.
    
    This is a simplified implementation that just checks basic patterns.
    In a real application, you would use more comprehensive validation.
    
    Args:
        address: The cryptocurrency address to validate
        crypto: The cryptocurrency code (BTC, ETH, etc.)
        
    Returns:
        bool: True if the address appears valid, False otherwise
    """
    if not address:
        return False
    
    if crypto == "BTC":
        # Basic validation for Bitcoin addresses
        return (
            (address.startswith("1") and len(address) in [26, 34]) or  # Legacy
            (address.startswith("3") and len(address) in [26, 34]) or  # P2SH
            (address.startswith("bc1") and len(address) in [42, 62])   # Bech32
        )
    elif crypto == "ETH" or crypto == "USDT":
        # Basic validation for Ethereum/USDT addresses
        return address.startswith("0x") and len(address) == 42
    elif crypto == "LTC":
        # Basic validation for Litecoin addresses
        return (
            (address.startswith("L") and len(address) in [26, 34]) or  # Legacy
            (address.startswith("M") and len(address) in [26, 34]) or  # P2SH
            (address.startswith("ltc1") and len(address) in [42, 62])  # Bech32
        )
    
    return False
