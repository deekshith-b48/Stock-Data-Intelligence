"""
SQLAlchemy ORM models for Stock Data Intelligence Dashboard.

This module defines the database schema using SQLAlchemy ORM:
- Company: Stores company information (symbol, name)
- StockData: Stores daily stock data with calculated metrics
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    BigInteger,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Company(Base):
    """
    Company model representing stock companies.
    
    Attributes:
        id: Primary key
        symbol: Unique stock symbol (e.g., RELIANCE, TCS)
        name: Company name
        created_at: Timestamp of record creation
        stock_data: Relationship to StockData records
    """
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with cascade delete
    stock_data = relationship(
        "StockData",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Company(symbol='{self.symbol}', name='{self.name}')>"


class StockData(Base):
    """
    StockData model representing daily stock market data and calculated metrics.
    
    Attributes:
        id: Primary key
        company_id: Foreign key to Company
        date: Trading date
        open: Opening price
        high: Highest price of the day
        low: Lowest price of the day
        close: Closing price
        volume: Trading volume
        daily_return: Calculated daily return percentage
        moving_avg_7d: 7-day moving average of closing prices
        volatility_score: Custom volatility metric (0-100 scale)
        created_at: Timestamp of record creation
        company: Relationship to Company record
    """
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    daily_return = Column(Numeric(10, 4))
    moving_avg_7d = Column(Numeric(10, 2))
    volatility_score = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    company = relationship("Company", back_populates="stock_data")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('company_id', 'date', name='uq_company_date'),
        Index('idx_company_date_desc', 'company_id', date.desc()),
    )
    
    def __repr__(self):
        return f"<StockData(company_id={self.company_id}, date='{self.date}', close={self.close})>"
