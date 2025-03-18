import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Country(db.Model):
    """Country model for storing country information."""
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=False)
    flag_emoji = Column(String(10), nullable=True)
    active = Column(Boolean, default=True)
    
    # Relationships
    gift_cards = relationship('GiftCard', back_populates='country', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Country {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'flag_emoji': self.flag_emoji,
            'active': self.active
        }


class GiftCard(db.Model):
    """GiftCard model for storing gift card information."""
    __tablename__ = 'gift_cards'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    active = Column(Boolean, default=True)
    
    # Relationships
    country = relationship('Country', back_populates='gift_cards')
    denominations = relationship('Denomination', back_populates='gift_card', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<GiftCard {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'country_id': self.country_id,
            'active': self.active,
            'country': self.country.name if self.country else None
        }


class Denomination(db.Model):
    """Denomination model for storing gift card denominations."""
    __tablename__ = 'denominations'
    
    id = Column(Integer, primary_key=True)
    value = Column(Float, nullable=False)
    currency_symbol = Column(String(10), default='$')
    gift_card_id = Column(Integer, ForeignKey('gift_cards.id'), nullable=False)
    discount_rate = Column(Float, default=0.0)  # As a percentage (e.g., 15.0 for 15%)
    active = Column(Boolean, default=True)
    
    # Relationships
    gift_card = relationship('GiftCard', back_populates='denominations')
    
    def __repr__(self):
        return f"<Denomination {self.currency_symbol}{self.value} for {self.gift_card.name if self.gift_card else 'Unknown'}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'currency_symbol': self.currency_symbol,
            'gift_card_id': self.gift_card_id,
            'discount_rate': self.discount_rate,
            'active': self.active,
            'discounted_price': round(self.value * (1 - (self.discount_rate / 100)), 2)
        }


class Order(db.Model):
    """Order model for storing user orders."""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(String(50), nullable=False, index=True)  # Telegram user ID
    user_name = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    gift_card = Column(String(100), nullable=False)
    denomination = Column(String(50), nullable=False)
    original_price = Column(Float, nullable=False)
    discounted_price = Column(Float, nullable=False)
    crypto = Column(String(10), nullable=False)  # BTC, ETH, etc.
    crypto_amount = Column(Float, nullable=False)
    payment_address = Column(String(255), nullable=False)
    status = Column(String(20), default='pending')  # pending, paid, completed, cancelled
    gift_card_code = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Order {self.order_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'country': self.country,
            'gift_card': self.gift_card,
            'denomination': self.denomination,
            'original_price': self.original_price,
            'discounted_price': self.discounted_price,
            'crypto': self.crypto,
            'crypto_amount': self.crypto_amount,
            'payment_address': self.payment_address,
            'status': self.status,
            'gift_card_code': self.gift_card_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class User(db.Model):
    """User model for storing Telegram user information."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    language_code = Column(String(10), default='en')
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.username or self.telegram_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'language_code': self.language_code,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }


class CryptoPayment(db.Model):
    """CryptoPayment model for storing payment transaction information."""
    __tablename__ = 'crypto_payments'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String(50), ForeignKey('orders.order_id'), nullable=False)
    transaction_id = Column(String(255), nullable=True)
    crypto = Column(String(10), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default='pending')  # pending, confirmed, failed
    confirmations = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<CryptoPayment {self.id} for Order {self.order_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'transaction_id': self.transaction_id,
            'crypto': self.crypto,
            'amount': self.amount,
            'status': self.status,
            'confirmations': self.confirmations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None
        }