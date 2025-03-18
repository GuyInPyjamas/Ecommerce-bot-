#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main command and callback handlers for the bot
"""
import logging
import json
from telegram import Update, ParseMode, InputFile
from telegram.ext import CallbackContext

from constants import (
    WELCOME_MESSAGE, 
    HELP_MESSAGE, 
    LANGUAGE_MESSAGE, 
    HISTORY_MESSAGE,
    NO_HISTORY_MESSAGE
)
from keyboards import (
    get_countries_keyboard,
    get_gift_cards_keyboard,
    get_denominations_keyboard,
    get_crypto_keyboard,
    get_back_keyboard,
    get_check_payment_keyboard
)
from data_manager import (
    get_countries,
    get_gift_cards_for_country,
    get_card_denominations,
    get_user_orders,
    get_order,
    save_order,
    update_order_status,
    get_payment_status
)
from payment import generate_payment_invoice, check_payment
from utils import generate_qr_code, generate_qr_code_image

logger = logging.getLogger(__name__)

# User state dictionary to track where users are in the conversation
user_states = {}
# Current selections for users
user_selections = {}
# Dictionary to keep track of QR code visibility for each user
qr_visibility = {}

def start_command(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started the bot")
    
    # Reset user state and selections
    user_states[user_id] = "country_selection"
    user_selections[user_id] = {}
    
    # Get countries keyboard
    keyboard = get_countries_keyboard()
    
    update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

def language_command(update: Update, context: CallbackContext) -> None:
    """Handle the /language command."""
    update.message.reply_text(
        LANGUAGE_MESSAGE,
        parse_mode=ParseMode.MARKDOWN
    )

def history_command(update: Update, context: CallbackContext) -> None:
    """Show user's purchase history."""
    user_id = update.effective_user.id
    orders = get_user_orders(user_id)
    
    if not orders:
        update.message.reply_text(
            NO_HISTORY_MESSAGE,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    history_text = HISTORY_MESSAGE + "\n\n"
    for order in orders:
        history_text += (
            f"*Order ID:* `{order['order_id']}`\n"
            f"*Date:* {order['date']}\n"
            f"*Country:* {order['country']}\n"
            f"*Gift Card:* {order['gift_card']}\n"
            f"*Value:* {order['denomination']}\n"
            f"*Status:* {order['status']}\n"
            f"{'*Code:* `' + order['gift_card_code'] + '`' if order.get('gift_card_code') else ''}\n\n"
        )
    
    update.message.reply_text(
        history_text,
        parse_mode=ParseMode.MARKDOWN
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Provide help information to the user."""
    update.message.reply_text(
        HELP_MESSAGE,
        parse_mode=ParseMode.MARKDOWN
    )

def button_callback(update: Update, context: CallbackContext) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Provide response feedback
    query.answer()
    
    # Get callback data
    data = query.data
    
    # Handle back button
    if data == "back_to_countries":
        user_states[user_id] = "country_selection"
        keyboard = get_countries_keyboard()
        query.edit_message_text(
            text="Please select a country:",
            reply_markup=keyboard
        )
        return
    
    if data == "back_to_gift_cards":
        user_states[user_id] = "gift_card_selection"
        country = user_selections[user_id].get("country", "")
        keyboard = get_gift_cards_keyboard(country)
        query.edit_message_text(
            text=f"Choose a gift card for {country}:",
            reply_markup=keyboard
        )
        return
    
    if data == "back_to_denominations":
        user_states[user_id] = "denomination_selection"
        country = user_selections[user_id].get("country", "")
        gift_card = user_selections[user_id].get("gift_card", "")
        keyboard = get_denominations_keyboard(country, gift_card)
        query.edit_message_text(
            text=f"Choose a denomination for {gift_card}:",
            reply_markup=keyboard
        )
        return
        
    if data == "back_to_crypto":
        user_states[user_id] = "crypto_selection"
        keyboard = get_crypto_keyboard()
        denomination = user_selections[user_id].get("denomination", "")
        
        # Check if the message has a photo (QR code)
        if query.message and query.message.photo:
            # Delete the message with QR code and send a new message
            query.message.delete()
            query.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"You selected {denomination}. Now choose a cryptocurrency for payment:",
                reply_markup=keyboard
            )
        else:
            # Normal edit if the message doesn't have a photo
            query.edit_message_text(
                text=f"You selected {denomination}. Now choose a cryptocurrency for payment:",
                reply_markup=keyboard
            )
        return
    
    # Handle country selection
    if user_states.get(user_id) == "country_selection":
        country = data
        user_selections[user_id]["country"] = country
        user_states[user_id] = "gift_card_selection"
        
        keyboard = get_gift_cards_keyboard(country)
        query.edit_message_text(
            text=f"You selected {country}. Now choose a gift card:",
            reply_markup=keyboard
        )
    
    # Handle gift card selection
    elif user_states.get(user_id) == "gift_card_selection":
        gift_card = data
        user_selections[user_id]["gift_card"] = gift_card
        user_states[user_id] = "denomination_selection"
        
        country = user_selections[user_id]["country"]
        keyboard = get_denominations_keyboard(country, gift_card)
        query.edit_message_text(
            text=f"You selected {gift_card}. Now choose a denomination:",
            reply_markup=keyboard
        )
    
    # Handle denomination selection
    elif user_states.get(user_id) == "denomination_selection":
        denomination = data
        user_selections[user_id]["denomination"] = denomination
        user_states[user_id] = "crypto_selection"
        
        keyboard = get_crypto_keyboard()
        query.edit_message_text(
            text=f"You selected {denomination}. Now choose a cryptocurrency for payment:",
            reply_markup=keyboard
        )
    
    # Handle cryptocurrency selection
    elif user_states.get(user_id) == "crypto_selection":
        crypto = data
        user_selections[user_id]["crypto"] = crypto
        user_states[user_id] = "payment"
        
        # Generate payment invoice
        country = user_selections[user_id]["country"]
        gift_card = user_selections[user_id]["gift_card"]
        denomination = user_selections[user_id]["denomination"]
        
        invoice = generate_payment_invoice(
            user_id, 
            country, 
            gift_card, 
            denomination, 
            crypto
        )
        
        # Store order ID for reference
        user_selections[user_id]["order_id"] = invoice["order_id"]
        
        # Generate QR code text for later use
        qr_code_text = f"{invoice['payment_address']}?amount={invoice['crypto_amount']}"
        user_selections[user_id]["qr_code_text"] = qr_code_text
        
        # Store payment address and amount for later reconstruction if needed
        user_selections[user_id]["payment_address"] = invoice['payment_address']
        user_selections[user_id]["crypto_amount"] = invoice['crypto_amount']
        user_selections[user_id]["crypto"] = crypto
        
        # Set QR code as hidden by default
        qr_visibility[user_id] = False
        
        # Create a payment message without QR code by default
        currency_symbol = invoice.get('currency_symbol', '$')
        original_discounted = invoice.get('original_discounted_amount', invoice['discounted_price'])
        
        # Calculate savings percentage
        original_price = invoice.get('original_price', 0)
        discounted_price = invoice.get('discounted_price', 0)
        savings_percentage = 0
        if original_price > 0:
            savings_percentage = int(((original_price - discounted_price) / original_price) * 100)
            
        # Format date and time
        from datetime import datetime
        current_time = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
        
        # Create a structured payment invoice with consistent format and emojis
        payment_text = (
            f"🧾 *PAYMENT INVOICE* 🧾\n\n"
            f"🔖 Order ID: #`{invoice['order_id'][:8]}...`\n"
            f"📅 Date Created: {current_time}\n\n"
            f"📊 Payment Status: *Payment Not Yet Confirmed* ❌\n\n"
            f"💳 *Payment Details:*\n"
            f"• 🔗 Blockchain: {crypto} Network\n"
            f"• 📬 Recipient Address: `{invoice['payment_address']}`\n"
            f"• 💰 Amount to send: *{invoice['crypto_amount']} {crypto}*\n\n"
            f"🎁 *Gift Card Details:*\n"
            f"• 🏪 Gift Card: {gift_card} ({country})\n"
            f"• 💲 Gift Card Amount: {denomination}\n"
            f"• 🔑 Gift Card Code: *Will be provided after payment*\n"
            f"Thank you for using Gift Card Store Bot. For assistance: @CardMerchantSupport"
        )
        
        # Get keyboard with QR toggle button (show_qr=False since QR is hidden by default)
        keyboard = get_check_payment_keyboard(show_qr=False)
        
        # Send message without QR code initially
        query.edit_message_text(
            text=payment_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Handle QR code toggling (show/hide)
    elif user_states.get(user_id) == "payment" and (data == "show_qr_code" or data == "hide_qr_code"):
        # Toggle QR code visibility
        show_qr = data == "show_qr_code"
        qr_visibility[user_id] = show_qr
        
        # Get the saved payment information
        order_id = user_selections[user_id]["order_id"]
        qr_code_text = user_selections[user_id].get("qr_code_text", "")
        
        # Get order details
        order = get_order(order_id)
        if not order:
            query.edit_message_text(
                text="Error: Order not found. Please start again with /start",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Re-create the payment message
        # Get currency symbol with fallback to $
        currency_symbol = order.get('currency_symbol', '$')
        
        # Format date and time
        from datetime import datetime
        current_time = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
        
        # Calculate savings percentage
        original_price = order.get('original_price', 0)
        discounted_price = order.get('discounted_price', 0)
        original_discounted = order.get('original_discounted_amount', order['discounted_price'])
        savings_percentage = 0
        if original_price > 0:
            savings_percentage = int(((original_price - discounted_price) / original_price) * 100)
            
        # Create a structured payment verification receipt with consistent format and emojis
        payment_text = (
            f"🧾 *PAYMENT VERIFICATION RECEIPT* 🧾\n\n"
            f"🔖 Order ID: #`{order['order_id'][:8]}...`\n"
            f"📅 Date Checked: {current_time}\n\n"
            f"📊 Payment Status: *Payment Not Yet Confirmed* ❌\n\n"
            f"💳 *Payment Details:*\n"
            f"• 🔗 Blockchain: {order['crypto']} Network\n"
            f"• 📬 Recipient Address: `{order['payment_address']}`\n"
            f"• 💰 Amount to send: *{order['crypto_amount']} {order['crypto']}*\n\n"
            f"🎁 *Gift Card Details:*\n"
            f"• 🏪 Gift Card: {order['gift_card']} ({order['country']})\n"
            f"• 💲 Gift Card Amount: {order['denomination']}\n"
            f"• 🔑 Gift Card Code: *Will be provided after payment*\n"
            f"Thank you for using Gift Card Store Bot. For assistance: @CardMerchantSupport"
        )
        
        if show_qr and qr_code_text:
            # User wants to show QR code
            # First delete the existing message to prevent errors with message too long
            query.message.delete()
            
            # Generate image QR code
            qr_image = generate_qr_code_image(qr_code_text)
            
            # Send a new message with QR code image and payment details
            context.bot.send_photo(
                chat_id=user_id,
                photo=InputFile(qr_image, filename="payment_qr.png"),
                caption=payment_text,
                reply_markup=get_check_payment_keyboard(show_qr=show_qr),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # User wants to hide QR code
            # Check if this is a photo message (with QR code) that needs to be replaced
            if query.message.photo:
                # This is a photo message, we need to delete it and send a text message
                query.message.delete()
                
                # Send a new text message without QR code
                context.bot.send_message(
                    chat_id=user_id,
                    text=payment_text,
                    reply_markup=get_check_payment_keyboard(show_qr=show_qr),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                # This is already a text message, just update it
                query.edit_message_text(
                    text=payment_text,
                    reply_markup=get_check_payment_keyboard(show_qr=show_qr),
                    parse_mode=ParseMode.MARKDOWN
                )
    
    # Handle payment check
    elif user_states.get(user_id) == "payment" and data == "check_payment":
        order_id = user_selections[user_id]["order_id"]
        
        # First, show a popup notification that we're checking payment
        query.answer("Checking payment status... Please wait.", show_alert=False)
        
        payment_status = check_payment(order_id)
        
        # Parse payment status into three cases:
        # 1. Payment confirmed (status is True or dict with completed/confirmed)
        # 2. Payment pending (status is dict with pending details)
        # 3. No payment found (status is False)
        
        # Case 1: Payment confirmed
        if payment_status is True or (isinstance(payment_status, dict) and 
            (payment_status.get("status") in ["completed", "confirmed"] or 
             payment_status.get("payment_status") == "confirmed")):
            
            # Show a shorter popup notification with the payment status
            query.answer("✅ Payment confirmed! Gift card ready.", show_alert=True)
            
            # Get gift card code
            if isinstance(payment_status, dict) and payment_status.get("gift_card_code"):
                gift_card_code = payment_status.get("gift_card_code")
            else:
                # Fallback code generation if not provided
                gift_card_code = f"GIFT-{order_id[:8]}"
                
                # Ensure order status is updated if needed
                if isinstance(payment_status, dict) and payment_status.get("status") != "completed":
                    update_order_status(order_id, "completed", gift_card_code)
            
            # Format date and time
            from datetime import datetime
            current_time = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
            
            # Get gift card and country from user selections
            gift_card = user_selections[user_id].get('gift_card', 'Gift Card')
            country = user_selections[user_id].get('country', '')
            
            # Create a structured payment verification receipt for confirmed payment with emojis and redemption instructions
            success_text = (
                f"🧾 *PAYMENT VERIFICATION RECEIPT* 🧾\n\n"
                f"🔖 Order ID: #`{order_id[:8]}...`\n"
                f"📅 Date Confirmed: {current_time}\n\n"
                f"📊 Payment Status: *Payment Confirmed* ✅\n\n"
                f"💳 *Payment Details:*\n"
                f"• 🔗 Blockchain: {user_selections[user_id].get('crypto', 'Crypto')} Network\n"
                f"• ✓ Transaction Status: Verified and Completed\n\n"
                f"🎁 *Gift Card Details:*\n"
                f"• 🏪 Gift Card: {gift_card} ({country})\n"
                f"• 💲 Gift Card Amount: {user_selections[user_id].get('denomination', '')}\n"
                f"• 🔑 Gift Card Code: `{gift_card_code}`\n\n"
                f"📋 *Redemption Instructions:*\n"
                f"• Visit the official {gift_card} website or app\n"
                f"• Select 'Redeem Gift Card' or similar option\n"
                f"• Enter the code shown above\n"
                f"• ⚠️ *IMPORTANT:* Please save this message by forwarding it to Saved Messages or taking a screenshot\n\n"
                f"Thank you for using Gift Card Store Bot. For assistance: @CardMerchantSupport"
            )
            
            # Use different methods based on whether we're showing a QR code
            show_qr = qr_visibility.get(user_id, False)
            if show_qr and query.message and query.message.photo:
                # If QR code is showing, we need to send a new message (since we used send_photo)
                query.message.delete()
                
                # Send a new text message with success message
                context.bot.send_message(
                    chat_id=user_id,
                    text=success_text,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                # If no QR code, we can just edit the text
                query.edit_message_text(
                    text=success_text,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            # Reset user state
            user_states[user_id] = None
            
        # Case 2: Payment pending (detected but waiting for confirmations)
        elif isinstance(payment_status, dict) and payment_status.get("status") == "pending":
            # Payment is pending, show status details
            confirmations = payment_status.get("confirmations", 0)
            required_confirms = payment_status.get("required_confirmations", 1)
            tx_id = payment_status.get("transaction_id", "Not available")
            
            # Calculate remaining time estimate
            remaining_confirms = required_confirms - confirmations
            est_minutes = remaining_confirms * 10  # Approx 10 minutes per confirmation
            est_time_text = f"~{est_minutes} minutes" if est_minutes > 0 else "any moment now"
            
            # Show a shorter popup alert with pending status information
            query.answer(f"⏳ Payment detected! Waiting for confirmations ({confirmations}/{required_confirms}). Ready in ~{est_time_text}.", show_alert=True)
            
            # Format the transaction ID for display (truncate if too long)
            if len(tx_id) > 16:
                tx_id_display = f"{tx_id[:8]}...{tx_id[-8:]}"
            else:
                tx_id_display = tx_id
                
            # Format date and time
            from datetime import datetime
            current_time = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
            
            # Get gift card and country from user selections
            gift_card = user_selections[user_id].get('gift_card', 'Gift Card')
            country = user_selections[user_id].get('country', '')
            
            # Create a structured payment verification receipt for pending payment with emojis
            pending_text = (
                f"🧾 *PAYMENT VERIFICATION RECEIPT* 🧾\n\n"
                f"🔖 Order ID: #`{order_id[:8]}...`\n"
                f"📅 Date Checked: {current_time}\n\n"
                f"📊 Payment Status: *Payment Pending Confirmation* ⏳\n\n"
                f"💳 *Payment Details:*\n"
                f"• 🔗 Blockchain: {user_selections[user_id].get('crypto', 'Crypto')} Network\n"
                f"• 🧾 Transaction ID: `{tx_id_display}`\n"
                f"• 📶 Progress: {confirmations}/{required_confirms} confirmations\n"
                f"• ⏱️ Estimated wait time: {est_time_text}\n\n"
                f"🎁 *Gift Card Details:*\n"
                f"• 🏪 Gift Card: {gift_card} ({country})\n"
                f"• 💲 Gift Card Amount: {user_selections[user_id].get('denomination', '')}\n"
                f"• 🔑 Gift Card Code: *Will be provided after confirmation*\n\n"
                f"⚙️ *Next Steps:*\n"
                f"• Your payment has been detected and is being processed\n"
                f"• Click 'Check Payment' again in {est_time_text} to get your code\n"
                f"• No further action is needed from your side\n\n"
                f"Thank you for using Gift Card Store Bot. For assistance: @CardMerchantSupport"
            )
            
            # Send professionally formatted pending message
            query.edit_message_text(
                text=pending_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_check_payment_keyboard(show_qr=False)
            )
            
        # Case 3: No payment found
        else:
            # Show shorter popup notification about payment not found
            query.answer("❌ No payment detected yet. Please send the exact amount shown and check again after 10-30 minutes.", show_alert=True)
            
            show_qr = qr_visibility.get(user_id, True)  # Default to showing QR code
            
            # Use different methods based on whether we're showing a QR code
            if show_qr:
                # If we need to show QR, get order details
                order = get_order(order_id)
                
                # If order not found, use stored user selections as fallback
                if not order:
                    # Create a fallback order from stored user selections
                    payment_address = user_selections[user_id].get("payment_address", "")
                    crypto_amount = user_selections[user_id].get("crypto_amount", "")
                    crypto = user_selections[user_id].get("crypto", "")
                    
                    # Format date and time
                    from datetime import datetime
                    current_time = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
                    
                    # Fallback for gift card name and country
                    gift_card = user_selections[user_id].get("gift_card", "Gift Card")
                    country = user_selections[user_id].get("country", "")
                    denomination = user_selections[user_id].get("denomination", "")
                    
                    # Create a structured payment verification receipt for awaiting payment with fallback and emojis
                    payment_text = (
                        f"🧾 *PAYMENT VERIFICATION RECEIPT* 🧾\n\n"
                        f"🔖 Order ID: #`{order_id[:8]}...`\n"
                        f"📅 Date Checked: {current_time}\n\n"
                        f"📊 Payment Status: *Awaiting Payment* ❌\n\n"
                        f"💳 *Payment Details:*\n"
                        f"• 🔗 Blockchain: {crypto} Network\n"
                        f"• 📬 Recipient Address: `{payment_address}`\n"
                        f"• 💰 Amount to send: *{crypto_amount} {crypto}*\n\n"
                        f"🎁 *Gift Card Details:*\n"
                        f"• 🏪 Gift Card: {gift_card} ({country})\n"
                        f"• 💲 Gift Card Amount: {denomination}\n"
                        f"• 🔑 Gift Card Code: *Will be provided after payment*\n\n"
                        f"📱 *Payment Instructions:*\n"
                        f"• Scan QR code with your wallet app\n"
                        f"• Send *exactly* {crypto_amount} {crypto}\n"
                        f"• After sending, click 'Check Payment' button\n"
                        f"• Allow up to 10-30 minutes for blockchain confirmation\n\n"
                        f"Thank you for using Gift Card Store Bot. For assistance: @CardMerchantSupport"
                    )
                    # Use the fallback QR code text
                    qr_code_text = user_selections[user_id].get("qr_code_text", "")
                else:
                    # Format date and time
                    from datetime import datetime
                    current_time = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
                    
                    # Get order details safely with defaults
                    order_id_display = order.get('order_id', order_id)[:8] + "..."
                    crypto = order.get('crypto', 'BTC')
                    payment_address = order.get('payment_address', '')
                    crypto_amount = order.get('crypto_amount', 0)
                    gift_card_name = order.get('gift_card', 'Gift Card')
                    country_name = order.get('country', '')
                    denomination_val = order.get('denomination', '')
                    
                    # Create a structured payment verification receipt for awaiting payment with order data and emojis
                    payment_text = (
                        f"🧾 *PAYMENT VERIFICATION RECEIPT* 🧾\n\n"
                        f"🔖 Order ID: #`{order_id_display}`\n"
                        f"📅 Date Checked: {current_time}\n\n"
                        f"📊 Payment Status: *Awaiting Payment* ❌\n\n"
                        f"💳 *Payment Details:*\n"
                        f"• 🔗 Blockchain: {crypto} Network\n"
                        f"• 📬 Recipient Address: `{payment_address}`\n"
                        f"• 💰 Amount to send: *{crypto_amount} {crypto}*\n\n"
                        f"🎁 *Gift Card Details:*\n"
                        f"• 🏪 Gift Card: {gift_card_name} ({country_name})\n"
                        f"• 💲 Gift Card Amount: {denomination_val}\n"
                        f"• 🔑 Gift Card Code: *Will be provided after payment*\n\n"
                        f"📱 *Payment Instructions:*\n"
                        f"• Scan QR code with your wallet app\n"
                        f"• Send *exactly* {crypto_amount} {crypto}\n"
                        f"• After sending, click 'Check Payment' button\n"
                        f"• Allow up to 10-30 minutes for blockchain confirmation\n\n"
                        f"Thank you for using Gift Card Store Bot. For assistance: @CardMerchantSupport"
                    )
                    # Use the order QR code text
                    qr_code_text = f"{payment_address}?amount={crypto_amount}"
                
                # If we already have a photo message, edit the caption
                if query.message and query.message.photo:
                    query.edit_message_caption(
                        caption=payment_text,
                        reply_markup=get_check_payment_keyboard(show_qr=True),
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    # Generate QR code image
                    qr_image = generate_qr_code_image(qr_code_text)
                    
                    # Delete existing message if any
                    if query.message:
                        query.message.delete()
                    
                    # Send a new message with QR code image and payment details
                    context.bot.send_photo(
                        chat_id=user_id,
                        photo=InputFile(qr_image, filename="payment_qr.png"),
                        caption=payment_text,
                        reply_markup=get_check_payment_keyboard(show_qr=True),
                        parse_mode=ParseMode.MARKDOWN
                    )
            else:
                # If no QR code needed, we still want to display the full invoice details
                # Get order details
                order = get_order(order_id)
                
                # Create appropriate message based on whether we have the order details
                payment_text = ""
                if not order:
                    # Fallback to user selections if order not found
                    payment_address = user_selections[user_id].get("payment_address", "")
                    crypto_amount = user_selections[user_id].get("crypto_amount", "")
                    crypto = user_selections[user_id].get("crypto", "")
                    gift_card = user_selections[user_id].get("gift_card", "")
                    country = user_selections[user_id].get("country", "")
                    denomination = user_selections[user_id].get("denomination", "")
                    
                    # Format date and time
                    from datetime import datetime
                    current_time = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
                    
                    # Create a structured payment verification receipt for awaiting payment with no QR and emojis
                    payment_text = (
                        f"🧾 *PAYMENT VERIFICATION RECEIPT* 🧾\n\n"
                        f"🔖 Order ID: #`{order_id[:8]}...`\n"
                        f"📅 Date Checked: {current_time}\n\n"
                        f"📊 Payment Status: *Awaiting Payment* ❌\n\n"
                        f"💳 *Payment Details:*\n"
                        f"• 🔗 Blockchain: {crypto} Network\n"
                        f"• 📬 Recipient Address: `{payment_address}`\n"
                        f"• 💰 Amount to send: *{crypto_amount} {crypto}*\n\n"
                        f"🎁 *Gift Card Details:*\n"
                        f"• 🏪 Gift Card: {gift_card} ({country})\n"
                        f"• 💲 Gift Card Amount: {denomination}\n"
                        f"• 🔑 Gift Card Code: *Will be provided after payment*\n\n"
                        f"📱 *Payment Instructions:*\n"
                        f"• Click 'Show QR Code' to display scan code for your wallet\n"
                        f"• Send *exactly* {crypto_amount} {crypto}\n"
                        f"• After sending, click 'Check Payment' button\n"
                        f"• Allow up to 10-30 minutes for blockchain confirmation\n\n"
                        f"Thank you for using Gift Card Store Bot. For assistance: @CardMerchantSupport"
                    )
                else:
                    # Format date and time
                    from datetime import datetime
                    current_time = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
                    
                    # Get order details safely with defaults
                    order_id_display = order.get('order_id', order_id)[:8] + "..."
                    crypto = order.get('crypto', 'BTC')
                    payment_address = order.get('payment_address', '')
                    crypto_amount = order.get('crypto_amount', 0)
                    gift_card_name = order.get('gift_card', 'Gift Card')
                    country_name = order.get('country', '')
                    denomination_val = order.get('denomination', '')
                    
                    # Create a structured payment verification receipt for awaiting payment with order and emojis
                    payment_text = (
                        f"🧾 *PAYMENT VERIFICATION RECEIPT* 🧾\n\n"
                        f"🔖 Order ID: #`{order_id_display}`\n"
                        f"📅 Date Checked: {current_time}\n\n"
                        f"📊 Payment Status: *Awaiting Payment* ❌\n\n"
                        f"💳 *Payment Details:*\n"
                        f"• 🔗 Blockchain: {crypto} Network\n"
                        f"• 📬 Recipient Address: `{payment_address}`\n"
                        f"• 💰 Amount to send: *{crypto_amount} {crypto}*\n\n"
                        f"🎁 *Gift Card Details:*\n"
                        f"• 🏪 Gift Card: {gift_card_name} ({country_name})\n"
                        f"• 💲 Gift Card Amount: {denomination_val}\n"
                        f"• 🔑 Gift Card Code: *Will be provided after payment*\n\n"
                        f"📱 *Payment Instructions:*\n"
                        f"• Click 'Show QR Code' to display scan code for your wallet\n"
                        f"• Send *exactly* {crypto_amount} {crypto}\n"
                        f"• After sending, click 'Check Payment' button\n"
                        f"• Allow up to 10-30 minutes for blockchain confirmation\n\n"
                        f"Thank you for using Gift Card Store Bot. For assistance: @CardMerchantSupport"
                    )
                
                # Update the message with the detailed payment info
                query.edit_message_text(
                    text=payment_text,
                    reply_markup=get_check_payment_keyboard(show_qr=False),
                    parse_mode=ParseMode.MARKDOWN
                )

def handle_text(update: Update, context: CallbackContext) -> None:
    """Handle normal text messages from users."""
    # Direct users to use commands instead
    update.message.reply_text(
        "Please use the /start command to begin shopping for gift cards or "
        "/help for assistance."
    )
