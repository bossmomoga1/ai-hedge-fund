"""StockScreen MCP Client for screening stocks based on fundamental criteria."""

import os
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime


class StockScreenClient:
    """Client for screening stocks using fundamental criteria via MCP protocol."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize StockScreen client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the MCP server
        """
        self.api_key = api_key or os.getenv("STOCKSCREEN_API_KEY")
        self.base_url = base_url or os.getenv("STOCKSCREEN_BASE_URL", "https://api.stockscreen.io/v1")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def screen_stocks(
        self,
        criteria: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Screen stocks based on fundamental criteria.
        
        Args:
            criteria: Dictionary of screening criteria (e.g., {"pe_ratio": {"min": 0, "max": 15}})
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of stocks matching the criteria
        """
        try:
            response = self.session.post(
                f"{self.base_url}/screen",
                json={
                    "criteria": criteria,
                    "limit": limit,
                    "offset": offset
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("stocks", [])
        except requests.exceptions.RequestException as e:
            print(f"Error screening stocks: {e}")
            return []
    
    def get_value_stocks(
        self,
        min_market_cap: float = 1_000_000_000,
        max_pe_ratio: float = 15,
        min_dividend_yield: float = 2.0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get value stocks based on common value investing criteria.
        
        Args:
            min_market_cap: Minimum market capitalization
            max_pe_ratio: Maximum P/E ratio
            min_dividend_yield: Minimum dividend yield percentage
            limit: Maximum number of results
            
        Returns:
            List of value stocks
        """
        criteria = {
            "market_cap": {"min": min_market_cap},
            "pe_ratio": {"max": max_pe_ratio},
            "dividend_yield": {"min": min_dividend_yield},
            "debt_to_equity": {"max": 1.0}
        }
        return self.screen_stocks(criteria, limit=limit)
    
    def get_growth_stocks(
        self,
        min_revenue_growth: float = 15.0,
        min_earnings_growth: float = 15.0,
        min_market_cap: float = 1_000_000_000,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get growth stocks based on growth metrics.
        
        Args:
            min_revenue_growth: Minimum revenue growth percentage
            min_earnings_growth: Minimum earnings growth percentage
            min_market_cap: Minimum market capitalization
            limit: Maximum number of results
            
        Returns:
            List of growth stocks
        """
        criteria = {
            "market_cap": {"min": min_market_cap},
            "revenue_growth": {"min": min_revenue_growth},
            "earnings_growth": {"min": min_earnings_growth}
        }
        return self.screen_stocks(criteria, limit=limit)
    
    def get_momentum_stocks(
        self,
        min_price_change_1m: float = 10.0,
        min_price_change_3m: float = 20.0,
        min_volume: float = 1_000_000,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get momentum stocks based on price performance.
        
        Args:
            min_price_change_1m: Minimum 1-month price change percentage
            min_price_change_3m: Minimum 3-month price change percentage
            min_volume: Minimum average daily volume
            limit: Maximum number of results
            
        Returns:
            List of momentum stocks
        """
        criteria = {
            "price_change_1m": {"min": min_price_change_1m},
            "price_change_3m": {"min": min_price_change_3m},
            "avg_volume": {"min": min_volume}
        }
        return self.screen_stocks(criteria, limit=limit)
    
    def get_stock_details(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Stock details or None if not found
        """
        try:
            response = self.session.get(
                f"{self.base_url}/stocks/{ticker}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching stock details for {ticker}: {e}")
            return None
    
    def get_sector_leaders(
        self,
        sector: str,
        metric: str = "market_cap",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get leading stocks in a specific sector.
        
        Args:
            sector: Sector name (e.g., "Technology", "Healthcare")
            metric: Metric to rank by (e.g., "market_cap", "revenue_growth")
            limit: Maximum number of results
            
        Returns:
            List of sector leaders
        """
        criteria = {
            "sector": {"equals": sector}
        }
        stocks = self.screen_stocks(criteria, limit=limit * 2)
        
        # Sort by the specified metric
        sorted_stocks = sorted(
            stocks,
            key=lambda x: x.get(metric, 0),
            reverse=True
        )
        
        return sorted_stocks[:limit]
