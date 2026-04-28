"""
Data collection module for Stock Data Intelligence Dashboard.

This module provides functionality to fetch stock market data from external sources.
"""

from .collector import AsyncDataCollector, DataCollector

__all__ = ['DataCollector', 'AsyncDataCollector']
