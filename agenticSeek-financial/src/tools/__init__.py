"""Tools module for LangChain-compatible financial analysis tools."""

from .stock_tools import (
    get_stock_price_tool,
    get_financial_metrics_tool,
    get_technical_indicators_tool,
    screen_stocks_tool
)
from .crypto_tools import (
    get_crypto_price_tool,
    get_crypto_market_data_tool,
    get_onchain_metrics_tool,
    get_top_cryptos_tool
)

__all__ = [
    # Stock tools
    "get_stock_price_tool",
    "get_financial_metrics_tool",
    "get_technical_indicators_tool",
    "screen_stocks_tool",
    # Crypto tools
    "get_crypto_price_tool",
    "get_crypto_market_data_tool",
    "get_onchain_metrics_tool",
    "get_top_cryptos_tool",
]
