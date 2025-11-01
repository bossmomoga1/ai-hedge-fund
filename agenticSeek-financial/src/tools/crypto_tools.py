"""LangChain-compatible tools for cryptocurrency analysis."""

from typing import Optional, Dict, Any
from langchain_core.tools import tool

from ..mcp_clients import CryptoClient


# Initialize client
crypto_client = CryptoClient()


@tool
def get_crypto_price_tool(symbol: str, vs_currency: str = "usd") -> Dict[str, Any]:
    """
    Get current price for a cryptocurrency.
    
    Args:
        symbol: Crypto symbol (e.g., "BTC", "ETH", "SOL")
        vs_currency: Quote currency (e.g., "usd", "eur")
    
    Returns:
        Current price data including 24h and 7d changes
    """
    try:
        price_data = crypto_client.get_crypto_price(symbol, vs_currency=vs_currency)
        
        if not price_data:
            return {"error": f"No price data found for {symbol}"}
        
        return {
            "symbol": symbol,
            "vs_currency": vs_currency,
            "price_data": price_data
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_crypto_market_data_tool(symbol: str) -> Dict[str, Any]:
    """
    Get comprehensive market data for a cryptocurrency.
    
    Args:
        symbol: Crypto symbol
    
    Returns:
        Market data including market cap, volume, supply, rank
    """
    try:
        market_data = crypto_client.get_market_data(symbol)
        
        if not market_data:
            return {"error": f"No market data found for {symbol}"}
        
        return {
            "symbol": symbol,
            "market_data": market_data
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_crypto_ohlcv_tool(
    symbol: str,
    interval: str = "1d",
    limit: int = 30
) -> Dict[str, Any]:
    """
    Get OHLCV (Open, High, Low, Close, Volume) data for a cryptocurrency.
    
    Args:
        symbol: Crypto symbol
        interval: Time interval ("1m", "5m", "1h", "1d", "1w")
        limit: Number of data points to retrieve
    
    Returns:
        OHLCV data
    """
    try:
        ohlcv_data = crypto_client.get_crypto_ohlcv(symbol, interval=interval)
        
        if not ohlcv_data:
            return {"error": f"No OHLCV data found for {symbol}"}
        
        # Limit results
        limited_data = ohlcv_data[:limit] if len(ohlcv_data) > limit else ohlcv_data
        
        return {
            "symbol": symbol,
            "interval": interval,
            "data_points": len(limited_data),
            "ohlcv": limited_data
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_top_cryptos_tool(limit: int = 20, sort_by: str = "market_cap") -> Dict[str, Any]:
    """
    Get top cryptocurrencies by market cap or other metrics.
    
    Args:
        limit: Maximum number of results
        sort_by: Sort criteria ("market_cap", "volume", "price_change_24h")
    
    Returns:
        List of top cryptocurrencies
    """
    try:
        cryptos = crypto_client.get_top_cryptocurrencies(limit=limit, sort_by=sort_by)
        
        return {
            "sort_by": sort_by,
            "count": len(cryptos),
            "cryptocurrencies": cryptos
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_onchain_metrics_tool(symbol: str) -> Dict[str, Any]:
    """
    Get on-chain metrics for a cryptocurrency.
    
    Args:
        symbol: Crypto symbol
    
    Returns:
        On-chain metrics including active addresses, transaction count, network activity
    """
    try:
        metrics = crypto_client.get_on_chain_metrics(symbol)
        
        if not metrics:
            return {"error": f"No on-chain metrics found for {symbol}"}
        
        return {
            "symbol": symbol,
            "onchain_metrics": metrics
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_defi_metrics_tool(protocol: str) -> Dict[str, Any]:
    """
    Get DeFi protocol metrics.
    
    Args:
        protocol: Protocol name (e.g., "uniswap", "aave", "compound")
    
    Returns:
        DeFi metrics including TVL, volume, revenue
    """
    try:
        metrics = crypto_client.get_defi_metrics(protocol)
        
        if not metrics:
            return {"error": f"No DeFi metrics found for {protocol}"}
        
        return {
            "protocol": protocol,
            "defi_metrics": metrics
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_fear_greed_index_tool() -> Dict[str, Any]:
    """
    Get the crypto Fear & Greed Index.
    
    Returns:
        Fear & Greed Index value and classification
    """
    try:
        index = crypto_client.get_fear_greed_index()
        
        if not index:
            return {"error": "Failed to fetch Fear & Greed Index"}
        
        return {
            "fear_greed_index": index
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_crypto_news_tool(symbol: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get recent news for a cryptocurrency.
    
    Args:
        symbol: Crypto symbol
        limit: Maximum number of news items
    
    Returns:
        Recent news articles
    """
    try:
        news = crypto_client.get_crypto_news(symbol, limit=limit)
        
        return {
            "symbol": symbol,
            "count": len(news),
            "news": news
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_crypto_exchanges_tool(symbol: str) -> Dict[str, Any]:
    """
    Get exchange listings for a cryptocurrency.
    
    Args:
        symbol: Crypto symbol
    
    Returns:
        List of exchanges where the crypto is traded
    """
    try:
        exchanges = crypto_client.get_crypto_exchanges(symbol)
        
        return {
            "symbol": symbol,
            "exchange_count": len(exchanges),
            "exchanges": exchanges
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def compare_cryptos_tool(symbols: list[str]) -> Dict[str, Any]:
    """
    Compare multiple cryptocurrencies.
    
    Args:
        symbols: List of crypto symbols to compare
    
    Returns:
        Comparison data for the cryptocurrencies
    """
    try:
        comparison = {}
        
        for symbol in symbols:
            price_data = crypto_client.get_crypto_price(symbol)
            market_data = crypto_client.get_market_data(symbol)
            
            comparison[symbol] = {
                "price": price_data,
                "market": market_data
            }
        
        return {
            "symbols": symbols,
            "comparison": comparison
        }
    except Exception as e:
        return {"error": str(e)}
