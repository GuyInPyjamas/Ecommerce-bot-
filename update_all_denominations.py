#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to update all denominations for all countries with the new standardized structure
"""
import os
import logging
from app import app
from add_standard_denominations import add_standard_denominations, main as add_all_denominations

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def update_all_country_denominations():
    """Update all country denominations to the new standardized structure."""
    logger.info("Starting to update all denominations with new standardized structure...")
    
    # Use the function from add_standard_denominations
    add_all_denominations()
    
    logger.info("Denomination update completed!")
    
if __name__ == "__main__":
    update_all_country_denominations()