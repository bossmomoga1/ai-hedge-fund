"""TradingView MCP Client for technical analysis and indicators."""

import os
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime, timedelta


class TradingViewClient:
    """Client for accessing TradingView technical indicators and chart data via MCP protocol."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize TradingView client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the MCP server
        """
        self.api_key = api_key or os.getenv("TRADINGVIEW_API_KEY")
        self.base_url = base_url or os.getenv("TRADINGVIEW_BASE_URL", "https://api.tradingview.com/v1")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def get_technical_indicators(
        self,
        ticker: str,
        interval: str = "1D",
        indicators: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get technical indicators for a stock.
        
        Args:
            ticker: Stock ticker symbol
            interval: Time interval ("1m", "5m", "15m", "1h", "4h", "1D", "1W", "1M")
            indicators: List of indicator names (e.g., ["RSI", "MACD", "EMA"])
            
        Returns:
            Technical indicators data
        """
        if indicators is None:
            indicators = ["RSI", "MACD", "EMA", "SMA", "BB", "STOCH"]
        
        try:
            response = self.session.get(
                f"{self.base_url}/technical-analysis/{ticker}",
                params={
                    "interval": interval,
                    "indicators": ",".join(indicators)
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching technical indicators for {ticker}: {e}")
            return None
    
    def get_rsi(
        self,
        ticker: str,
        interval: str = "1D",
        period: int = 14
    ) -> Optional[Dict[str, Any]]:
        """
        Get Relative Strength Index (RSI) for a stock.
        
        Args:
            ticker: Stock ticker symbol
            interval: Time interval
            period: RSI period
            
        Returns:
            RSI data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/indicators/rsi/{ticker}",
                params={
                    "interval": interval,
                    "period": period
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching RSI for {ticker}: {e}")
            return None
    
    def get_macd(
        self,
        ticker: str,
        interval: str = "1D",
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Optional[Dict[str, Any]]:
        """
        Get MACD (Moving Average Convergence Divergence) for a stock.
        
        Args:
            ticker: Stock ticker symbol
            interval: Time interval
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
            
        Returns:
            MACD data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/indicators/macd/{ticker}",
                params={
                    "interval": interval,
                    "fast": fast_period,
                    "slow": slow_period,
                    "signal": signal_period
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching MACD for {ticker}: {e}")
            return None
    
    def get_moving_averages(
        self,
        ticker: str,
        interval: str = "1D",
        periods: Optional[List[int]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get moving averages for a stock.
        
        Args:
            ticker: Stock ticker symbol
            interval: Time interval
            periods: List of periods for moving averages (e.g., [20, 50, 200])
            
        Returns:
            Moving averages data
        """
        if periods is None:
            periods = [20, 50, 100, 200]
        
        try:
            response = self.session.get(
                f"{self.base_url}/indicators/ma/{ticker}",
                params={
                    "interval": interval,
                    "periods": ",".join(map(str, periods))
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching moving averages for {ticker}: {e}")
            return None
    
    def get_bollinger_bands(
        self,
        ticker: str,
        interval: str = "1D",
        period: int = 20,
        std_dev: float = 2.0
    ) -> Optional[Dict[str, Any]]:
        """
        Get Bollinger Bands for a stock.
        
        Args:
            ticker: Stock ticker symbol
            interval: Time interval
            period: Period for moving average
            std_dev: Number of standard deviations
            
        Returns:
            Bollinger Bands data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/indicators/bb/{ticker}",
                params={
                    "interval": interval,
                    "period": period,
                    "std_dev": std_dev
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Bollinger Bands for {ticker}: {e}")
            return None
    
    def get_stochastic(
        self,
        ticker: str,
        interval: str = "1D",
        k_period: int = 14,
        d_period: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Get Stochastic Oscillator for a stock.
        
        Args:
            ticker: Stock ticker symbol
            interval: Time interval
            k_period: %K period
            d_period: %D period
            
        Returns:
            Stochastic data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/indicators/stoch/{ticker}",
                params={
                    "interval": interval,
                    "k_period": k_period,
                    "d_period": d_period
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Stochastic for {ticker}: {e}")
            return None
    
    def get_chart_patterns(
        self,
        ticker: str,
        interval: str = "1D"
    ) -> List[Dict[str, Any]]:
        """
        Detect chart patterns for a stock.
        
        Args:
            ticker: Stock ticker symbol
            interval: Time interval
            
        Returns:
            List of detected chart patterns
        """
        try:
            response = self.session.get(
                f"{self.base_url}/patterns/{ticker}",
                params={"interval": interval},
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("patterns", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching chart patterns for {ticker}: {e}")
            return []
    
    def get_support_resistance(
        self,
        ticker: str,
        interval: str = "1D",
        lookback_periods: int = 100
    ) -> Optional[Dict[str, Any]]:
        """
        Get support and resistance levels for a stock.
        
        Args:
            ticker: Stock ticker symbol
            interval: Time interval
            lookback_periods: Number of periods to analyze
            
        Returns:
            Support and resistance levels
        """
        try:
            response = self.session.get(
                f"{self.base_url}/levels/{ticker}",
                params={
                    "interval": interval,
                    "lookback": lookback_periods
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching support/resistance for {ticker}: {e}")
            return None
    
    def get_technical_summary(
        self,
        ticker: str,
        interval: str = "1D"
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive technical analysis summary.
        
        Args:
            ticker: Stock ticker symbol
            interval: Time interval
            
        Returns:
            Technical summary with buy/sell/neutral signals
        """
        try:
            response = self.session.get(
                f"{self.base_url}/summary/{ticker}",
                params={"interval": interval},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching technical summary for {ticker}: {e}")
            return None
    
    def get_pivot_points(
        self,
        ticker: str,
        interval: str = "1D",
        method: str = "standard"
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate pivot points for a stock.
        
        Args:
            ticker: Stock ticker symbol
            interval: Time interval
            method: Calculation method ("standard", "fibonacci", "woodie", "camarilla")
            
        Returns:
            Pivot points data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/indicators/pivot/{ticker}",
                params={
                    "interval": interval,
                    "method": method
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching pivot points for {ticker}: {e}")
            return None
