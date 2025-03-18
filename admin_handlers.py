#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Admin command handlers for the bot
"""
import os
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CallbackContext

import json
from config import ADMIN_USER_ID, DISCOUNT_PERCENTAGE
from data_manager import get_all_orders, get_countries, get_gift_cards_for_country, update_order_status, cancel_order

logger = logging.getLogger(__name__)

# Admin states
admin_state = {}

def admin_command(update: Update, context: CallbackContext) -> None:
    """Admin panel command handler."""
    user_id = update.effective_user.id
    
    # Verify the user is an admin
    if user_id != ADMIN_USER_ID:
        update.message.reply_text(
            "You are not authorized to use the admin panel."
        )
        return
    
    # Reset admin state
    admin_state[user_id] = "main_menu"
    
    # Create admin panel menu
    keyboard = [
        [InlineKeyboardButton("View Orders", callback_data="admin_view_orders")],
        [InlineKeyboardButton("Edit Discount Rate", callback_data="admin_edit_discount")],
        [InlineKeyboardButton("Manage Gift Cards", callback_data="admin_manage_cards")],
        [InlineKeyboardButton("Manage Countries", callback_data="admin_manage_countries")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "*Admin Panel*\n\nWhat would you like to do?",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

def admin_button_callback(update: Update, context: CallbackContext) -> None:
    """Handle admin panel button callbacks."""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Verify the user is an admin
    if user_id != ADMIN_USER_ID:
        query.answer("You are not authorized to use the admin panel.")
        return
    
    # Provide response feedback
    query.answer()
    
    # Get callback data
    data = query.data
    
    # Handle admin actions
    if data == "admin_view_orders":
        view_orders(query)
    elif data.startswith("admin_order_"):
        order_id = data.split("_")[2]
        view_order_details(query, order_id)
    elif data.startswith("admin_cancel_order_"):
        order_id = data.split("_")[3]
        cancel_order_action(query, order_id)
    elif data.startswith("admin_complete_order_"):
        order_id = data.split("_")[3]
        complete_order_action(query, order_id)
    elif data == "admin_back_to_orders":
        view_orders(query)
    elif data == "admin_back_to_main":
        back_to_admin_main(query)
    elif data == "admin_edit_discount":
        edit_discount(query)
    elif data.startswith("admin_set_discount_"):
        new_rate = data.split("_")[3]
        set_discount_rate(query, new_rate)
    elif data == "admin_manage_cards":
        manage_gift_cards(query)
    elif data.startswith("admin_toggle_card_"):
        card_id = data.split("_")[3]
        toggle_gift_card(query, card_id)
    elif data == "admin_manage_countries":
        manage_countries(query)
    elif data.startswith("admin_toggle_country_"):
        country_id = data.split("_")[3]
        toggle_country(query, country_id)

def view_orders(query):
    """Show all orders for admin."""
    orders = get_all_orders()
    
    if not orders:
        query.edit_message_text(
            "*No orders found*\n\nThere are currently no orders in the system.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Main Menu", callback_data="admin_back_to_main")
            ]])
        )
        return
    
    # Create a list of orders with buttons
    text = "*All Orders*\n\n"
    keyboard = []
    
    for order in orders:
        order_date = datetime.fromisoformat(order.get("date", "")).strftime("%Y-%m-%d %H:%M")
        text += (
            f"*Order ID:* `{order['order_id']}`\n"
            f"*Date:* {order_date}\n"
            f"*User ID:* `{order['user_id']}`\n"
            f"*Card:* {order['gift_card']} ({order['country']})\n"
            f"*Amount:* {order['denomination']}\n"
            f"*Status:* {order['status']}\n\n"
        )
        
        keyboard.append([
            InlineKeyboardButton(f"Order {order['order_id'][:8]}", callback_data=f"admin_order_{order['order_id']}")
        ])
    
    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="admin_back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

def view_order_details(query, order_id):
    """Show detailed information about a specific order."""
    orders = get_all_orders()
    order = next((o for o in orders if o["order_id"] == order_id), None)
    
    if not order:
        query.edit_message_text(
            f"*Error:* Order with ID `{order_id}` not found.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Orders", callback_data="admin_back_to_orders")
            ]])
        )
        return
    
    # Format order details
    order_date = datetime.fromisoformat(order.get("date", "")).strftime("%Y-%m-%d %H:%M")
    text = (
        f"*Order Details*\n\n"
        f"*Order ID:* `{order['order_id']}`\n"
        f"*Date:* {order_date}\n"
        f"*User ID:* `{order['user_id']}`\n"
        f"*Country:* {order['country']}\n"
        f"*Gift Card:* {order['gift_card']}\n"
        f"*Value:* {order['denomination']}\n"
        f"*Discounted Price:* ${order['discounted_price']}\n"
        f"*Payment Method:* {order['crypto']}\n"
        f"*Crypto Amount:* {order['crypto_amount']} {order['crypto']}\n"
        f"*Status:* {order['status']}\n"
    )
    
    if order.get("gift_card_code"):
        text += f"*Gift Card Code:* `{order['gift_card_code']}`\n"
    
    # Action buttons based on order status
    keyboard = []
    if order["status"] == "pending":
        keyboard.append([
            InlineKeyboardButton("Mark as Completed", callback_data=f"admin_complete_order_{order_id}"),
            InlineKeyboardButton("Cancel Order", callback_data=f"admin_cancel_order_{order_id}")
        ])
    elif order["status"] == "completed":
        keyboard.append([
            InlineKeyboardButton("Cancel Order", callback_data=f"admin_cancel_order_{order_id}")
        ])
    
    keyboard.append([InlineKeyboardButton("Back to Orders", callback_data="admin_back_to_orders")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

def cancel_order_action(query, order_id):
    """Cancel an order."""
    result = cancel_order(order_id)
    
    if result:
        query.edit_message_text(
            f"*Success:* Order `{order_id}` has been cancelled.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Orders", callback_data="admin_back_to_orders")
            ]])
        )
    else:
        query.edit_message_text(
            f"*Error:* Failed to cancel order `{order_id}`.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Orders", callback_data="admin_back_to_orders")
            ]])
        )

def complete_order_action(query, order_id):
    """Mark an order as completed."""
    # In a real app, this would generate or retrieve a gift card code
    gift_card_code = f"GIFT-{order_id}-CODE"
    
    result = update_order_status(order_id, "completed", gift_card_code)
    
    if result:
        query.edit_message_text(
            f"*Success:* Order `{order_id}` has been marked as completed.\n\n"
            f"Gift card code: `{gift_card_code}`",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Orders", callback_data="admin_back_to_orders")
            ]])
        )
    else:
        query.edit_message_text(
            f"*Error:* Failed to complete order `{order_id}`.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Orders", callback_data="admin_back_to_orders")
            ]])
        )

def back_to_admin_main(query):
    """Return to the admin main menu."""
    keyboard = [
        [InlineKeyboardButton("View Orders", callback_data="admin_view_orders")],
        [InlineKeyboardButton("Edit Discount Rate", callback_data="admin_edit_discount")],
        [InlineKeyboardButton("Manage Gift Cards", callback_data="admin_manage_cards")],
        [InlineKeyboardButton("Manage Countries", callback_data="admin_manage_countries")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        "*Admin Panel*\n\nWhat would you like to do?",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

def edit_discount(query):
    """Show discount rate editor."""
    # Get current discount rate
    current_rate = DISCOUNT_PERCENTAGE
    
    # Create buttons for preset discount rates
    preset_rates = [15, 25, 35, 45, 55, 65, 75]
    keyboard = []
    
    # Create rows of 3 buttons each
    for i in range(0, len(preset_rates), 3):
        row = []
        for rate in preset_rates[i:i+3]:
            button_text = f"{rate}%" + (" (current)" if rate == current_rate else "")
            row.append(InlineKeyboardButton(button_text, callback_data=f"admin_set_discount_{rate}"))
        keyboard.append(row)
    
    # Add back button
    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="admin_back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        f"*Edit Discount Rate*\n\nCurrent discount rate: *{current_rate}%*\n\n"
        f"Select a new discount rate:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

def set_discount_rate(query, new_rate):
    """Set a new discount rate."""
    try:
        rate = int(new_rate)
        if rate < 0 or rate > 90:
            raise ValueError("Rate out of allowed range")
        
        # In a real application, we would update the database and config
        # For this demonstration, we'll just show a success message
        
        query.edit_message_text(
            f"*Success*\n\nDiscount rate has been updated to *{rate}%*.\n\n"
            f"Note: In a real application, this would update the database and config.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Main Menu", callback_data="admin_back_to_main")
            ]]),
            parse_mode=ParseMode.MARKDOWN
        )
    except ValueError:
        query.edit_message_text(
            "*Error*\n\nInvalid discount rate. Please select a rate between 0% and 90%.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Discount Editor", callback_data="admin_edit_discount")
            ]]),
            parse_mode=ParseMode.MARKDOWN
        )

def manage_gift_cards(query):
    """Show gift card management interface."""
    # Get all countries
    countries = get_countries()
    
    # Create a menu to select country first
    keyboard = []
    for country in countries:
        keyboard.append([InlineKeyboardButton(country, callback_data=f"admin_country_cards_{country}")])
    
    # Add back button
    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="admin_back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        "*Manage Gift Cards*\n\nSelect a country to manage its gift cards:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

def toggle_gift_card(query, card_id):
    """Toggle the active status of a gift card."""
    try:
        # Parse the card_id which includes country and card name
        parts = card_id.split('|')
        if len(parts) != 2:
            raise ValueError("Invalid card ID format")
        
        country, card_name = parts
        
        # In a real application, we would update the database
        # For this demonstration, we'll just show a success message
        
        query.edit_message_text(
            f"*Success*\n\nGift card '{card_name}' in {country} has been toggled.\n\n"
            f"Note: In a real application, this would update the database.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Gift Cards", callback_data="admin_manage_cards")
            ]]),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        query.edit_message_text(
            f"*Error*\n\nFailed to toggle gift card: {str(e)}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Gift Cards", callback_data="admin_manage_cards")
            ]]),
            parse_mode=ParseMode.MARKDOWN
        )

def manage_countries(query):
    """Show country management interface."""
    # Get all countries
    countries = get_countries()
    
    # Create buttons for each country
    keyboard = []
    for country in countries:
        keyboard.append([InlineKeyboardButton(f"{country}", callback_data=f"admin_toggle_country_{country}")])
    
    # Add back button
    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="admin_back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        "*Manage Countries*\n\nSelect a country to toggle its active status:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

def toggle_country(query, country_id):
    """Toggle the active status of a country."""
    try:
        # In a real application, we would update the database
        # For this demonstration, we'll just show a success message
        
        query.edit_message_text(
            f"*Success*\n\nCountry '{country_id}' has been toggled.\n\n"
            f"Note: In a real application, this would update the database.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Countries", callback_data="admin_manage_countries")
            ]]),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        query.edit_message_text(
            f"*Error*\n\nFailed to toggle country: {str(e)}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Back to Countries", callback_data="admin_manage_countries")
            ]]),
            parse_mode=ParseMode.MARKDOWN
        )
