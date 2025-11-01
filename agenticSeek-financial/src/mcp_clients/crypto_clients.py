"""Crypto MCP Client for cryptocurrency data and analysis."""

import os
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime, timedelta


class CryptoClient:
    """Client for accessing cryptocurrency data via MCP protocol."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize Crypto client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the MCP server
        """
        self.api_key = api_key or os.getenv("CRYPTO_API_KEY")
        self.base_url = base_url or os.getenv("CRYPTO_BASE_URL", "https://api.crypto-data.io/v1")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-API-KEY": self.api_key})
    
    def get_crypto_price(
        self,
        symbol: str,
        vs_currency: str = "usd"
    ) -> Optional[Dict[str, Any]]:
        """
        Get current price for a cryptocurrency.
        
        Args:
            symbol: Crypto symbol (e.g., "BTC", "ETH")
            vs_currency: Quote currency (e.g., "usd", "eur")
            
        Returns:
            Current price data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/price/{symbol}",
                params={"vs_currency": vs_currency},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching crypto price for {symbol}: {e}")
            return None
    
    def get_crypto_ohlcv(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """
        Get OHLCV (Open, High, Low, Close, Volume) data for a cryptocurrency.
        
        Args:
            symbol: Crypto symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Time interval ("1m", "5m", "1h", "1d", "1w")
            
        Returns:
            List of OHLCV data
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        try:
            response = self.session.get(
                f"{self.base_url}/ohlcv/{symbol}",
                params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "interval": interval
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return []
    
    def get_market_data(
        self,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive market data for a cryptocurrency.
        
        Args:
            symbol: Crypto symbol
            
        Returns:
            Market data including market cap, volume, supply, etc.
        """
        try:
            response = self.session.get(
                f"{self.base_url}/market/{symbol}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching market data for {symbol}: {e}")
            return None
    
    def get_top_cryptocurrencies(
        self,
        limit: int = 100,
        sort_by: str = "market_cap"
    ) -> List[Dict[str, Any]]:
        """
        Get top cryptocurrencies by market cap or other metrics.
        
        Args:
            limit: Maximum number of results
            sort_by: Sort criteria ("market_cap", "volume", "price_change_24h")
            
        Returns:
            List of top cryptocurrencies
        """
        try:
            response = self.session.get(
                f"{self.base_url}/top",
                params={
                    "limit": limit,
                    "sort_by": sort_by
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("cryptocurrencies", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching top cryptocurrencies: {e}")
            return []
    
    def get_crypto_exchanges(
        self,
        symbol: str
    ) -> List[Dict[str, Any]]:
        """
        Get exchange listings for a cryptocurrency.
        
        Args:
            symbol: Crypto symbol
            
        Returns:
            List of exchanges where the crypto is traded
        """
        try:
            response = self.session.get(
                f"{self.base_url}/exchanges/{symbol}",
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("exchanges", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exchanges for {symbol}: {e}")
            return []
    
    def get_on_chain_metrics(
        self,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get on-chain metrics for a cryptocurrency.
        
        Args:
            symbol: Crypto symbol
            
        Returns:
            On-chain metrics (active addresses, transaction count, etc.)
        """
        try:
            response = self.session.get(
                f"{self.base_url}/onchain/{symbol}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching on-chain metrics for {symbol}: {e}")
            return None
    
    def get_defi_metrics(
        self,
        protocol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get DeFi protocol metrics.
        
        Args:
            protocol: Protocol name (e.g., "uniswap", "aave", "compound")
            
        Returns:
            DeFi metrics (TVL, volume, fees, etc.)
        """
        try:
            response = self.session.get(
                f"{self.base_url}/defi/{protocol}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching DeFi metrics for {protocol}: {e}")
            return None
    
    def get_crypto_news(
        self,
        symbol: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get cryptocurrency news.
        
        Args:
            symbol: Crypto symbol (optional, for symbol-specific news)
            limit: Maximum number of results
            
        Returns:
            List of news articles
        """
        try:
            params = {"limit": limit}
            if symbol:
                params["symbol"] = symbol
            
            response = self.session.get(
                f"{self.base_url}/news",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("news", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching crypto news: {e}")
            return []
    
    def get_fear_greed_index(self) -> Optional[Dict[str, Any]]:
        """
        Get crypto fear & greed index.
        
        Returns:
            Fear & greed index data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/fear-greed",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching fear & greed index: {e}")
            return None
    
    def get_trending_cryptos(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get trending cryptocurrencies.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of trending cryptocurrencies
        """
        try:
            response = self.session.get(
                f"{self.base_url}/trending",
                params={"limit": limit},
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("trending", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching trending cryptos: {e}")
            return []
    
    def get_nft_data(
        self,
        collection: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get NFT collection data.
        
        Args:
            collection: NFT collection name or address
            
        Returns:
            NFT collection data (floor price, volume, etc.)
        """
        try:
            response = self.session.get(
                f"{self.base_url}/nft/{collection}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching NFT data for {collection}: {e}")
            return None
