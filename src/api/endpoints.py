"""
API endpoint handlers for Stock Data Intelligence Dashboard.

This module implements all REST API endpoints:
- GET /companies - List all companies
- GET /data/{symbol} - Get stock data for a symbol
- GET /summary/{symbol} - Get summary statistics for a symbol
- GET /compare - Compare two stocks

Requirements: 6.3, 6.4, 6.5, 6.6, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4, 9.5
"""

import logging
from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, Path, status
from sqlalchemy import desc

from .schemas import (
    CompanyResponse,
    StockDataResponse,
    SummaryResponse,
    CompareResponse,
    ErrorResponse,
    validate_symbol
)
from ..models.database import Company as CompanyModel, StockData as StockDataModel
from ..models.connection import get_database
from ..data_processor.processor import DataProcessor

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(
    prefix="",
    responses={
        404: {"model": ErrorResponse, "description": "Resource not found"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.get(
    "/companies",
    response_model=List[CompanyResponse],
    tags=["Companies"],
    summary="List all companies",
    description="Retrieve a list of all available companies with their stock symbols and names",
    status_code=status.HTTP_200_OK
)
async def get_companies():
    """
    Get list of all companies.
    
    Returns:
        List[CompanyResponse]: List of all companies with symbol and name
        
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    """
    logger.info("Fetching all companies")
    
    db = get_database()
    
    try:
        with db.get_session() as session:
            # Query all companies ordered by symbol
            companies = session.query(CompanyModel).order_by(CompanyModel.symbol).all()
            
            # Convert to response models
            result = [
                CompanyResponse(symbol=company.symbol, name=company.name)
                for company in companies
            ]
            
            logger.info(f"Retrieved {len(result)} companies")
            return result
            
    except Exception as e:
        logger.error(f"Error fetching companies: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "DATABASE_ERROR",
                "message": "Failed to retrieve companies"
            }
        )


@router.get(
    "/data/{symbol}",
    response_model=List[StockDataResponse],
    tags=["Stock Data"],
    summary="Get stock data for a symbol",
    description="Retrieve the last 30 days of stock data for a specific company symbol",
    status_code=status.HTTP_200_OK
)
async def get_stock_data(
    symbol: str = Path(
        ...,
        description="Stock symbol (e.g., RELIANCE, TCS)",
        example="RELIANCE"
    ),
    days: int = Query(
        30,
        description="Number of days of historical data to retrieve",
        ge=1,
        le=365
    )
):
    """
    Get stock data for a specific symbol.
    
    Args:
        symbol: Stock symbol (alphanumeric and hyphens only)
        days: Number of days of historical data (default: 30)
        
    Returns:
        List[StockDataResponse]: List of stock data records sorted by date (most recent first)
        
    Raises:
        HTTPException 400: If symbol format is invalid
        HTTPException 404: If symbol does not exist
        
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 10.1, 10.3
    """
    # Validate symbol format
    try:
        symbol = validate_symbol(symbol)
    except ValueError as e:
        logger.warning(f"Invalid symbol format: {symbol}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_SYMBOL",
                "message": str(e)
            }
        )
    
    logger.info(f"Fetching stock data for {symbol} (last {days} days)")
    
    db = get_database()
    
    try:
        with db.get_session() as session:
            # Check if company exists
            company = session.query(CompanyModel).filter(
                CompanyModel.symbol == symbol
            ).first()
            
            if not company:
                logger.warning(f"Company not found: {symbol}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error_code": "SYMBOL_NOT_FOUND",
                        "message": f"Stock symbol '{symbol}' does not exist in the database"
                    }
                )
            
            # Calculate date threshold
            date_threshold = datetime.now().date() - timedelta(days=days)
            
            # Query stock data for last N days, sorted by date descending
            stock_data = session.query(StockDataModel).filter(
                StockDataModel.company_id == company.id,
                StockDataModel.date >= date_threshold
            ).order_by(desc(StockDataModel.date)).all()
            
            # Convert to response models
            result = [
                StockDataResponse(
                    date=record.date,
                    open=float(record.open),
                    high=float(record.high),
                    low=float(record.low),
                    close=float(record.close),
                    volume=int(record.volume),
                    daily_return=float(record.daily_return) if record.daily_return else None,
                    moving_avg_7d=float(record.moving_avg_7d) if record.moving_avg_7d else None
                )
                for record in stock_data
            ]
            
            logger.info(f"Retrieved {len(result)} records for {symbol}")
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "DATABASE_ERROR",
                "message": "Failed to retrieve stock data"
            }
        )


@router.get(
    "/summary/{symbol}",
    response_model=SummaryResponse,
    tags=["Stock Data"],
    summary="Get summary statistics for a symbol",
    description="Retrieve 52-week high, low, and average closing price for a specific company symbol",
    status_code=status.HTTP_200_OK
)
async def get_summary(
    symbol: str = Path(
        ...,
        description="Stock symbol (e.g., RELIANCE, TCS)",
        example="RELIANCE"
    )
):
    """
    Get summary statistics for a specific symbol.
    
    Args:
        symbol: Stock symbol (alphanumeric and hyphens only)
        
    Returns:
        SummaryResponse: 52-week statistics including high, low, average close, and volatility score
        
    Raises:
        HTTPException 400: If symbol format is invalid
        HTTPException 404: If symbol does not exist
        
    Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
    """
    # Validate symbol format
    try:
        symbol = validate_symbol(symbol)
    except ValueError as e:
        logger.warning(f"Invalid symbol format: {symbol}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_SYMBOL",
                "message": str(e)
            }
        )
    
    logger.info(f"Fetching summary for {symbol}")
    
    db = get_database()
    processor = DataProcessor()
    
    try:
        with db.get_session() as session:
            # Check if company exists
            company = session.query(CompanyModel).filter(
                CompanyModel.symbol == symbol
            ).first()
            
            if not company:
                logger.warning(f"Company not found: {symbol}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error_code": "SYMBOL_NOT_FOUND",
                        "message": f"Stock symbol '{symbol}' does not exist in the database"
                    }
                )
            
            # Query all stock data for the company (for 52-week calculation)
            stock_data = session.query(StockDataModel).filter(
                StockDataModel.company_id == company.id
            ).order_by(StockDataModel.date).all()
            
            if not stock_data:
                logger.warning(f"No stock data found for {symbol}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error_code": "NO_DATA",
                        "message": f"No stock data available for symbol '{symbol}'"
                    }
                )
            
            # Convert to DataFrame for processing
            import pandas as pd
            df = pd.DataFrame([
                {
                    'date': record.date,
                    'close': float(record.close),
                    'volatility_score': float(record.volatility_score) if record.volatility_score else None
                }
                for record in stock_data
            ])
            
            # Calculate 52-week statistics
            stats = processor.calculate_52_week_stats(df)
            
            # Get the most recent volatility score
            latest_volatility = None
            if not df['volatility_score'].isna().all():
                latest_volatility = df['volatility_score'].dropna().iloc[-1] if len(df['volatility_score'].dropna()) > 0 else None
            
            result = SummaryResponse(
                symbol=company.symbol,
                name=company.name,
                week_52_high=stats['52_week_high'],
                week_52_low=stats['52_week_low'],
                avg_close=stats['avg_close'],
                volatility_score=float(latest_volatility) if latest_volatility is not None else None
            )
            
            logger.info(f"Retrieved summary for {symbol}")
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching summary for {symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "DATABASE_ERROR",
                "message": "Failed to retrieve summary statistics"
            }
        )


@router.get(
    "/compare",
    response_model=CompareResponse,
    tags=["Stock Data"],
    summary="Compare two stocks",
    description="Compare summary statistics for two different stock symbols side by side",
    status_code=status.HTTP_200_OK
)
async def compare_stocks(
    symbol1: str = Query(
        ...,
        description="First stock symbol to compare",
        example="RELIANCE"
    ),
    symbol2: str = Query(
        ...,
        description="Second stock symbol to compare",
        example="TCS"
    )
):
    """
    Compare two stocks side by side.
    
    Args:
        symbol1: First stock symbol
        symbol2: Second stock symbol
        
    Returns:
        CompareResponse: Side-by-side comparison of both stocks
        
    Raises:
        HTTPException 400: If symbols are identical or format is invalid
        HTTPException 404: If either symbol does not exist
        
    Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
    """
    # Validate symbol formats
    try:
        symbol1 = validate_symbol(symbol1)
        symbol2 = validate_symbol(symbol2)
    except ValueError as e:
        logger.warning(f"Invalid symbol format in comparison")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_SYMBOL",
                "message": str(e)
            }
        )
    
    # Check if symbols are identical
    if symbol1 == symbol2:
        logger.warning(f"Attempted to compare identical symbols: {symbol1}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "IDENTICAL_SYMBOLS",
                "message": f"Cannot compare identical symbols. symbol1 and symbol2 must be different."
            }
        )
    
    logger.info(f"Comparing stocks: {symbol1} vs {symbol2}")
    
    # Get summaries for both stocks
    try:
        summary1 = await get_summary(symbol1)
        summary2 = await get_summary(symbol2)
        
        result = CompareResponse(
            stock1=summary1,
            stock2=summary2
        )
        
        logger.info(f"Successfully compared {symbol1} and {symbol2}")
        return result
        
    except HTTPException as e:
        # Re-raise with more specific error message for comparison
        if e.status_code == status.HTTP_404_NOT_FOUND:
            error_detail = e.detail
            if isinstance(error_detail, dict):
                message = error_detail.get('message', '')
                if symbol1 in message:
                    invalid_symbol = symbol1
                else:
                    invalid_symbol = symbol2
                
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error_code": "SYMBOL_NOT_FOUND",
                        "message": f"Stock symbol '{invalid_symbol}' does not exist in the database"
                    }
                )
        raise
    except Exception as e:
        logger.error(f"Error comparing {symbol1} and {symbol2}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "COMPARISON_ERROR",
                "message": "Failed to compare stocks"
            }
        )
