"""LangChain-compatible tools for stock analysis."""

from typing import Optional, Dict, Any
from langchain_core.tools import tool

from ..mcp_clients import (
    FinancialDatasetsClient,
    TradingViewClient,
    StockScreenClient,
    StockFlowClient
)


# Initialize clients
financial_client = FinancialDatasetsClient()
tradingview_client = TradingViewClient()
stockscreen_client = StockScreenClient()
stockflow_client = StockFlowClient()


@tool
def get_stock_price_tool(ticker: str, interval: str = "day") -> Dict[str, Any]:
    """
    Get current and historical price data for a stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "MSFT")
        interval: Time interval ("minute", "hour", "day", "week", "month")
    
    Returns:
        Price data including current price, historical prices, and changes
    """
    try:
        prices = financial_client.get_prices(ticker, interval=interval)
        
        if not prices:
            return {"error": f"No price data found for {ticker}"}
        
        # Get latest price
        latest = prices[0] if prices else {}
        
        return {
            "ticker": ticker,
            "current_price": latest.get("close"),
            "open": latest.get("open"),
            "high": latest.get("high"),
            "low": latest.get("low"),
            "volume": latest.get("volume"),
            "date": latest.get("date"),
            "historical_data": prices[:30]  # Last 30 data points
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_financial_metrics_tool(ticker: str, period: str = "ttm") -> Dict[str, Any]:
    """
    Get comprehensive financial metrics and ratios for a stock.
    
    Args:
        ticker: Stock ticker symbol
        period: Period type ("ttm", "quarterly", "annual")
    
    Returns:
        Financial metrics including P/E, ROE, debt ratios, margins, etc.
    """
    try:
        metrics = financial_client.get_financial_metrics(ticker, period=period, limit=1)
        
        if not metrics:
            return {"error": f"No financial metrics found for {ticker}"}
        
        return {
            "ticker": ticker,
            "period": period,
            "metrics": metrics[0]
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_income_statement_tool(ticker: str, period: str = "annual", limit: int = 3) -> Dict[str, Any]:
    """
    Get income statement data for a stock.
    
    Args:
        ticker: Stock ticker symbol
        period: Period type ("quarterly", "annual")
        limit: Number of periods to retrieve
    
    Returns:
        Income statement data including revenue, expenses, and net income
    """
    try:
        statements = financial_client.get_income_statement(ticker, period=period, limit=limit)
        
        if not statements:
            return {"error": f"No income statement data found for {ticker}"}
        
        return {
            "ticker": ticker,
            "period": period,
            "statements": statements
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_balance_sheet_tool(ticker: str, period: str = "annual", limit: int = 3) -> Dict[str, Any]:
    """
    Get balance sheet data for a stock.
    
    Args:
        ticker: Stock ticker symbol
        period: Period type ("quarterly", "annual")
        limit: Number of periods to retrieve
    
    Returns:
        Balance sheet data including assets, liabilities, and equity
    """
    try:
        sheets = financial_client.get_balance_sheet(ticker, period=period, limit=limit)
        
        if not sheets:
            return {"error": f"No balance sheet data found for {ticker}"}
        
        return {
            "ticker": ticker,
            "period": period,
            "balance_sheets": sheets
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_cash_flow_tool(ticker: str, period: str = "annual", limit: int = 3) -> Dict[str, Any]:
    """
    Get cash flow statement data for a stock.
    
    Args:
        ticker: Stock ticker symbol
        period: Period type ("quarterly", "annual")
        limit: Number of periods to retrieve
    
    Returns:
        Cash flow data including operating, investing, and financing cash flows
    """
    try:
        statements = financial_client.get_cash_flow_statement(ticker, period=period, limit=limit)
        
        if not statements:
            return {"error": f"No cash flow data found for {ticker}"}
        
        return {
            "ticker": ticker,
            "period": period,
            "cash_flows": statements
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_technical_indicators_tool(ticker: str, interval: str = "1D") -> Dict[str, Any]:
    """
    Get technical indicators for a stock.
    
    Args:
        ticker: Stock ticker symbol
        interval: Time interval ("1m", "5m", "15m", "1h", "4h", "1D", "1W")
    
    Returns:
        Technical indicators including RSI, MACD, moving averages, etc.
    """
    try:
        indicators = tradingview_client.get_technical_indicators(ticker, interval=interval)
        summary = tradingview_client.get_technical_summary(ticker, interval=interval)
        
        return {
            "ticker": ticker,
            "interval": interval,
            "indicators": indicators,
            "summary": summary
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_support_resistance_tool(ticker: str, interval: str = "1D") -> Dict[str, Any]:
    """
    Get support and resistance levels for a stock.
    
    Args:
        ticker: Stock ticker symbol
        interval: Time interval
    
    Returns:
        Support and resistance levels
    """
    try:
        levels = tradingview_client.get_support_resistance(ticker, interval=interval)
        
        return {
            "ticker": ticker,
            "interval": interval,
            "levels": levels
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def screen_stocks_tool(
    min_market_cap: Optional[float] = None,
    max_pe_ratio: Optional[float] = None,
    min_revenue_growth: Optional[float] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Screen stocks based on fundamental criteria.
    
    Args:
        min_market_cap: Minimum market capitalization
        max_pe_ratio: Maximum P/E ratio
        min_revenue_growth: Minimum revenue growth percentage
        limit: Maximum number of results
    
    Returns:
        List of stocks matching the criteria
    """
    try:
        criteria = {}
        
        if min_market_cap:
            criteria["market_cap"] = {"min": min_market_cap}
        if max_pe_ratio:
            criteria["pe_ratio"] = {"max": max_pe_ratio}
        if min_revenue_growth:
            criteria["revenue_growth"] = {"min": min_revenue_growth}
        
        stocks = stockscreen_client.screen_stocks(criteria, limit=limit)
        
        return {
            "criteria": criteria,
            "count": len(stocks),
            "stocks": stocks
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_volume_analysis_tool(ticker: str) -> Dict[str, Any]:
    """
    Get volume analysis for a stock.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Volume analysis including trends and unusual activity
    """
    try:
        volume_data = stockflow_client.get_volume_analysis(ticker)
        
        return {
            "ticker": ticker,
            "volume_analysis": volume_data
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_insider_trades_tool(ticker: str, limit: int = 20) -> Dict[str, Any]:
    """
    Get recent insider trading activity for a stock.
    
    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of trades to retrieve
    
    Returns:
        Recent insider trades
    """
    try:
        trades = financial_client.get_insider_trades(ticker, limit=limit)
        
        return {
            "ticker": ticker,
            "insider_trades": trades,
            "count": len(trades)
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_company_facts_tool(ticker: str) -> Dict[str, Any]:
    """
    Get company facts and overview information.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Company facts including name, sector, industry, description
    """
    try:
        facts = financial_client.get_company_facts(ticker)
        
        return {
            "ticker": ticker,
            "company_facts": facts
        }
    except Exception as e:
        return {"error": str(e)}
