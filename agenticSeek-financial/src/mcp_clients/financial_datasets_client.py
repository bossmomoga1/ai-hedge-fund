"""Financial Datasets MCP Client for comprehensive financial data."""

import os
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime, timedelta


class FinancialDatasetsClient:
    """Client for accessing comprehensive financial datasets via MCP protocol."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize Financial Datasets client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
        """
        self.api_key = api_key or os.getenv("FINANCIAL_DATASETS_API_KEY")
        self.base_url = base_url or "https://api.financialdatasets.ai"
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-API-KEY": self.api_key})
    
    def get_financial_metrics(
        self,
        ticker: str,
        end_date: Optional[str] = None,
        period: str = "ttm",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get financial metrics for a stock.
        
        Args:
            ticker: Stock ticker symbol
            end_date: End date (YYYY-MM-DD)
            period: Period type ("ttm", "quarterly", "annual")
            limit: Maximum number of results
            
        Returns:
            List of financial metrics
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            response = self.session.get(
                f"{self.base_url}/financial-metrics/",
                params={
                    "ticker": ticker,
                    "report_period_lte": end_date,
                    "period": period,
                    "limit": limit
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("financial_metrics", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching financial metrics for {ticker}: {e}")
            return []
    
    def get_income_statement(
        self,
        ticker: str,
        end_date: Optional[str] = None,
        period: str = "annual",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get income statement data.
        
        Args:
            ticker: Stock ticker symbol
            end_date: End date (YYYY-MM-DD)
            period: Period type ("quarterly", "annual")
            limit: Maximum number of results
            
        Returns:
            List of income statements
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            response = self.session.get(
                f"{self.base_url}/financials/income-statements/",
                params={
                    "ticker": ticker,
                    "end_date": end_date,
                    "period": period,
                    "limit": limit
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("income_statements", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching income statement for {ticker}: {e}")
            return []
    
    def get_balance_sheet(
        self,
        ticker: str,
        end_date: Optional[str] = None,
        period: str = "annual",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get balance sheet data.
        
        Args:
            ticker: Stock ticker symbol
            end_date: End date (YYYY-MM-DD)
            period: Period type ("quarterly", "annual")
            limit: Maximum number of results
            
        Returns:
            List of balance sheets
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            response = self.session.get(
                f"{self.base_url}/financials/balance-sheets/",
                params={
                    "ticker": ticker,
                    "end_date": end_date,
                    "period": period,
                    "limit": limit
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("balance_sheets", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching balance sheet for {ticker}: {e}")
            return []
    
    def get_cash_flow_statement(
        self,
        ticker: str,
        end_date: Optional[str] = None,
        period: str = "annual",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get cash flow statement data.
        
        Args:
            ticker: Stock ticker symbol
            end_date: End date (YYYY-MM-DD)
            period: Period type ("quarterly", "annual")
            limit: Maximum number of results
            
        Returns:
            List of cash flow statements
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            response = self.session.get(
                f"{self.base_url}/financials/cash-flow-statements/",
                params={
                    "ticker": ticker,
                    "end_date": end_date,
                    "period": period,
                    "limit": limit
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("cash_flow_statements", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching cash flow statement for {ticker}: {e}")
            return []
    
    def get_prices(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        Get price data for a stock.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Time interval ("minute", "hour", "day", "week", "month")
            
        Returns:
            List of price data
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        try:
            response = self.session.get(
                f"{self.base_url}/prices/",
                params={
                    "ticker": ticker,
                    "start_date": start_date,
                    "end_date": end_date,
                    "interval": interval,
                    "interval_multiplier": 1
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("prices", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching prices for {ticker}: {e}")
            return []
    
    def get_company_facts(
        self,
        ticker: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get company facts and overview.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Company facts data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/company/facts/",
                params={"ticker": ticker},
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("company_facts")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching company facts for {ticker}: {e}")
            return None
    
    def get_insider_trades(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get insider trading data.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of results
            
        Returns:
            List of insider trades
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        try:
            response = self.session.get(
                f"{self.base_url}/insider-trades/",
                params={
                    "ticker": ticker,
                    "filing_date_gte": start_date,
                    "filing_date_lte": end_date,
                    "limit": limit
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("insider_trades", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching insider trades for {ticker}: {e}")
            return []
    
    def search_line_items(
        self,
        ticker: str,
        line_items: List[str],
        end_date: Optional[str] = None,
        period: str = "ttm",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for specific line items in financial statements.
        
        Args:
            ticker: Stock ticker symbol
            line_items: List of line item names to search for
            end_date: End date (YYYY-MM-DD)
            period: Period type ("ttm", "quarterly", "annual")
            limit: Maximum number of results
            
        Returns:
            List of line item data
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            response = self.session.post(
                f"{self.base_url}/financials/search/line-items",
                json={
                    "tickers": [ticker],
                    "line_items": line_items,
                    "end_date": end_date,
                    "period": period,
                    "limit": limit
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("search_results", [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching line items for {ticker}: {e}")
            return []
