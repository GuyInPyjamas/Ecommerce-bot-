#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for denomination formatting
"""
from data_manager import format_denomination_with_discount

# Test various currency formats
test_currencies = [
    '$100',  # USD
    '100€',  # EUR
    '£250',  # GBP
    '₽10000',  # RUB
    '₺10000',  # TRY
    'C$100',  # CAD
    'A$100',  # AUD
]

for currency in test_currencies:
    print(f"Original: {currency} | Formatted: {format_denomination_with_discount(currency)}")