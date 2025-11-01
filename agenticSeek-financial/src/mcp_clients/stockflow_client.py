"""StockFlow MCP Client for analyzing stock flow and volume patterns."""

import os
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime, timedelta


class StockFlowClient:
    """Client for analyzing stock flow, volume patterns, and order flow via MCP protocol."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize StockFlow client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the MCP server
        """
        self.api_key = api_key or os.getenv("STOCKFLOW_API_KEY")
        self.base_url = base_url or os.getenv("STOCKFLOW_BASE_URL", "https://api.stockflow.io/v1")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def get_volume_analysis(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get volume analysis for a stock.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Volume analysis data
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        try:
            response = self.session.get(
                f"{self.base_url}/volume/{ticker}",
                params={
                    "start_date": start_date,
                    "end_date": end_date
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching volume analysis for {ticker}: {e}")
            return None
    
    def get_order_flow(
        self,
        ticker: str,
        interval: str = "1h"
    ) -> Optional[Dict[str, Any]]:
        """
        Get order flow data for a stock.
        
        Args:
            ticker: Stock ticker symbol
            interval: Time interval (e.g., "1m", "5m", "1h", "1d")
            
        Returns:
            Order flow data including buy/sell pressure
        """
        try:
            response = self.session.get(
                f"{self.base_url}/orderflow/{ticker}",
                params={"interval": interval},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching order flow for {ticker}: {e}")
            return None
    
    def get_money_flow_index(
        self,
        ticker: str,
        period: int = 14
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate Money Flow Index (MFI) for a stock.
        
        Args:
            ticker: Stock ticker symbol
            period: Period for MFI calculation
            
        Returns:
            MFI data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/indicators/mfi/{ticker}",
                params={"period": period},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching MFI for {ticker}: {e}")
            return None
    
    def get_volume_profile(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get volume profile (volume by price level) for a stock.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Volume profile data
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        try:
            response = self.session.get(
                f"{self.base_url}/volume-profile/{ticker}",
                params={
                    "start_date": start_date,
                    "end_date": end_date
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching volume profile for {ticker}: {e}")
            return None
    
    def get_dark_pool_activity(
        self,
        ticker: str,
        days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Get dark pool trading activity for a stock.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days to look back
            
        Returns:
            Dark pool activity data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/darkpool/{ticker}",
                params={"days": days},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching dark pool activity for {ticker}: {e}")
            return None
    
    def get_institutional_flow(
        self,
        ticker: str,
        period: str = "1m"
    ) -> Optional[Dict[str, Any]]:
        """
        Get institutional money flow for a stock.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period ("1w", "1m", "3m", "6m", "1y")
            
        Returns:
            Institutional flow data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/institutional-flow/{ticker}",
                params={"period": period},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching institutional flow for {ticker}: {e}")
            return None
    
    def get_unusual_volume(
        self,
        min_volume_ratio: float = 2.0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get stocks with unusual volume activity.
        
        Args:
            min_volume_ratio: Minimum ratio of current volume to average volume
            limit: Maximum number of results
            
        Returns:
            List of stocks with unusual volume
        """
        try:
            response = self.session.get(
                f"{self.base_url}/unusual-volume",
                params={
                    "min_ratio": min_volume_ratio,
                    "limit": limit
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("stocks", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching unusual volume stocks: {e}")
            return []
    
    def get_block_trades(
        self,
        ticker: str,
        min_size: int = 10000,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get block trades for a stock.
        
        Args:
            ticker: Stock ticker symbol
            min_size: Minimum trade size (shares)
            days: Number of days to look back
            
        Returns:
            List of block trades
        """
        try:
            response = self.session.get(
                f"{self.base_url}/block-trades/{ticker}",
                params={
                    "min_size": min_size,
                    "days": days
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("trades", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching block trades for {ticker}: {e}")
            return []
