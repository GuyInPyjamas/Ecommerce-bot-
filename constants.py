#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constant messages used throughout the bot
"""

# Welcome message shown when /start command is issued
WELCOME_MESSAGE = """
🎁 *Welcome to the Gift Card Store Bot!* 🎁

Purchase gift cards for multiple countries with a 45% discount! 
Pay with cryptocurrency for instant delivery.

Please select a country to see available gift cards:
"""

# Help message shown when /help command is issued
HELP_MESSAGE = """
🔍 *Gift Card Store Bot Help* 🔍

*Available Commands:*
• /start - Start shopping for gift cards
• /language - Change your preferred language
• /history - View your purchase history
• /help - Show this help message

*Purchase Process:*
1. Choose a country
2. Select a gift card
3. Pick a denomination
4. Choose a cryptocurrency for payment
5. Send payment to the provided address
6. Click "Check Payment" to verify
7. Receive your gift card code instantly

*Support:*
If you have any questions or issues, please contact our support.

*Payment:*
We accept Bitcoin, Ethereum, USDT, and Litecoin.
All gift cards are offered with a 45% discount.
"""

# Language selection message
LANGUAGE_MESSAGE = """
🌐 *Language Selection* 🌐

Currently, the bot is available in English only.
Support for additional languages will be added soon.
"""

# History message header
HISTORY_MESSAGE = """
📜 *Your Purchase History* 📜

Here are your previous gift card purchases:
"""

# No history message
NO_HISTORY_MESSAGE = """
📜 *Your Purchase History* 📜

You haven't made any purchases yet. Use /start to shop for gift cards.
"""

# Payment successful message template
PAYMENT_SUCCESS_MESSAGE = """
✅ *Payment Received!* ✅

Thank you for your purchase. Here is your gift card code:

`{gift_card_code}`

Use /start to purchase another gift card.
"""

# Payment pending message
PAYMENT_PENDING_MESSAGE = """
⏳ *Payment Pending* ⏳

We haven't received your payment yet. Please send the exact amount to the provided address and click "Check Payment" again.

If you've already sent the payment, please wait for network confirmations and try again.
"""
