#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask web application for the Gift Card Store Bot
"""
import os
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for
from dotenv import load_dotenv
from models import db, Country, GiftCard, Denomination, Order, User, CryptoPayment
from flask_migrate import Migrate

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "telegram-gift-card-store")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database
db.init_app(app)
migrate = Migrate(app, db)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """API health check"""
    return jsonify({"status": "ok", "message": "API is operational"})

@app.route('/api/bot-status')
def bot_status():
    """Get bot status"""
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    admin_id = os.environ.get('ADMIN_USER_ID')
    
    status = {
        "bot_configured": bot_token is not None,
        "admin_configured": admin_id is not None,
        "bot_username": "Use the Telegram bot to access gift card store"
    }
    
    return jsonify(status)

# Admin API routes
@app.route('/api/admin/countries', methods=['GET'])
def get_countries():
    """Get all countries"""
    countries = Country.query.all()
    return jsonify([country.to_dict() for country in countries])

@app.route('/api/admin/gift-cards', methods=['GET'])
def get_gift_cards():
    """Get all gift cards"""
    gift_cards = GiftCard.query.all()
    return jsonify([gift_card.to_dict() for gift_card in gift_cards])

@app.route('/api/admin/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {e}")
    return render_template('500.html'), 500

# Start the bot in a separate thread when running the Flask app directly
if __name__ == '__main__':
    import threading
    from bot import create_bot, run_bot
    
    def start_bot():
        # Create and run the bot
        logger.info("Starting Telegram bot in thread...")
        bot = create_bot()
        run_bot(bot)
    
    # Start the bot in a thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask
    app.run(host='0.0.0.0', port=5000, debug=True)