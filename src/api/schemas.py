"""
Pydantic response models for Stock Data Intelligence Dashboard API.

This module defines request/response schemas for API endpoints using Pydantic.
All models include validation, examples, and documentation.

Requirements: 10.4
"""

from datetime import date as date_type
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import re


class CompanyResponse(BaseModel):
    """
    Company information response model.
    
    Requirements: 6.2
    """
    symbol: str = Field(..., description="Stock symbol (e.g., RELIANCE, TCS)")
    name: str = Field(..., description="Company name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "name": "Reliance Industries Limited"
            }
        }


class StockDataResponse(BaseModel):
    """
    Daily stock data response model.
    
    Requirements: 7.2
    """
    date: date_type = Field(..., description="Trading date in YYYY-MM-DD format")
    open: float = Field(..., description="Opening price", gt=0)
    high: float = Field(..., description="Highest price of the day", gt=0)
    low: float = Field(..., description="Lowest price of the day", gt=0)
    close: float = Field(..., description="Closing price", gt=0)
    volume: int = Field(..., description="Trading volume", gt=0)
    daily_return: Optional[float] = Field(None, description="Daily return percentage")
    moving_avg_7d: Optional[float] = Field(None, description="7-day moving average of closing prices")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "open": 2450.50,
                "high": 2475.00,
                "low": 2445.00,
                "close": 2470.25,
                "volume": 5234567,
                "daily_return": 1.25,
                "moving_avg_7d": 2460.50
            }
        }


class SummaryResponse(BaseModel):
    """
    Stock summary statistics response model.
    
    Requirements: 8.2
    """
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    week_52_high: float = Field(..., description="52-week high closing price", gt=0)
    week_52_low: float = Field(..., description="52-week low closing price", gt=0)
    avg_close: float = Field(..., description="Average closing price over 52 weeks", gt=0)
    volatility_score: Optional[float] = Field(None, description="Volatility score (0-100 scale)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "name": "Reliance Industries Limited",
                "week_52_high": 2850.00,
                "week_52_low": 2100.00,
                "avg_close": 2475.50,
                "volatility_score": 45.2
            }
        }


class CompareResponse(BaseModel):
    """
    Stock comparison response model.
    
    Requirements: 9.2
    """
    stock1: SummaryResponse = Field(..., description="First stock summary")
    stock2: SummaryResponse = Field(..., description="Second stock summary")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stock1": {
                    "symbol": "RELIANCE",
                    "name": "Reliance Industries Limited",
                    "week_52_high": 2850.00,
                    "week_52_low": 2100.00,
                    "avg_close": 2475.50,
                    "volatility_score": 45.2
                },
                "stock2": {
                    "symbol": "TCS",
                    "name": "Tata Consultancy Services",
                    "week_52_high": 3800.00,
                    "week_52_low": 3100.00,
                    "avg_close": 3450.00,
                    "volatility_score": 32.8
                }
            }
        }


class ErrorResponse(BaseModel):
    """
    Error response model for API errors.
    
    Requirements: 10.4
    """
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "SYMBOL_NOT_FOUND",
                "message": "Stock symbol 'XYZ' does not exist in the database"
            }
        }


class HealthResponse(BaseModel):
    """
    Health check response model.
    
    Requirements: 6.1
    """
    status: str = Field(..., description="Service health status")
    database: str = Field(..., description="Database connection status")
    timestamp: str = Field(..., description="Current timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": "connected",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


def validate_symbol(symbol: str) -> str:
    """
    Validate stock symbol format.
    
    Symbol must contain only alphanumeric characters, hyphens, and dots.
    Dots are allowed to support exchange suffixes (e.g., RELIANCE.NS).
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        str: Validated symbol in uppercase
        
    Raises:
        ValueError: If symbol format is invalid
        
    Requirements: 10.3
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty")
    
    # Check for valid characters (alphanumeric, hyphens, and dots)
    if not re.match(r'^[A-Za-z0-9\-\.]+$', symbol):
        raise ValueError(
            f"Symbol '{symbol}' contains invalid characters. "
            "Only alphanumeric characters, hyphens, and dots are allowed."
        )
    
    return symbol.upper()
