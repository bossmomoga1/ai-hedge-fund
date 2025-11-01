"""Fundamental Agent for fundamental analysis of stocks."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

from ..mcp_clients import FinancialDatasetsClient


class FundamentalAgent:
    """Agent specialized in fundamental analysis using financial statements and metrics."""
    
    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.1
    ):
        """
        Initialize Fundamental Agent.
        
        Args:
            llm_provider: LLM provider ("openai", "anthropic", "groq")
            model_name: Model name
            temperature: Temperature for LLM
        """
        self.llm = self._initialize_llm(llm_provider, model_name, temperature)
        self.financial_client = FinancialDatasetsClient()
        
        self.system_prompt = """You are an expert fundamental analyst with deep knowledge of financial statements, valuation, and company analysis.
Your role is to analyze companies using fundamental data and provide investment insights based on intrinsic value.

You should consider:
1. Financial statements (income statement, balance sheet, cash flow)
2. Key financial ratios (P/E, P/B, ROE, ROA, debt ratios, margins)
3. Revenue and earnings growth trends
4. Profitability and efficiency metrics
5. Financial health and solvency
6. Competitive position and moat
7. Management quality and capital allocation
8. Valuation relative to intrinsic value and peers

Provide clear, data-driven analysis with specific recommendations (BUY, HOLD, SELL) based on fundamental value.
Always include margin of safety considerations and key risks."""
    
    def _initialize_llm(self, provider: str, model_name: str, temperature: float):
        """Initialize the appropriate LLM based on provider."""
        if provider.lower() == "openai":
            return ChatOpenAI(model=model_name, temperature=temperature)
        elif provider.lower() == "anthropic":
            return ChatAnthropic(model=model_name, temperature=temperature)
        elif provider.lower() == "groq":
            return ChatGroq(model=model_name, temperature=temperature)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def analyze_fundamentals(
        self,
        ticker: str,
        periods: int = 4,
        include_ratios: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive fundamental analysis on a stock.
        
        Args:
            ticker: Stock ticker symbol
            periods: Number of periods to analyze
            include_ratios: Include detailed ratio analysis
            
        Returns:
            Fundamental analysis results with recommendation
        """
        # Gather fundamental data
        data = self._gather_fundamental_data(ticker, periods, include_ratios)
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(ticker, data)
        
        # Get LLM analysis
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "ticker": ticker,
            "analysis": response.content,
            "data": data,
            "timestamp": self._get_timestamp()
        }
    
    def _gather_fundamental_data(
        self,
        ticker: str,
        periods: int,
        include_ratios: bool
    ) -> Dict[str, Any]:
        """Gather fundamental data from Financial Datasets client."""
        data = {}
        
        # Company facts
        data["company_facts"] = self.financial_client.get_company_facts(ticker)
        
        # Financial statements
        data["income_statements"] = self.financial_client.get_income_statement(
            ticker, period="annual", limit=periods
        )
        data["balance_sheets"] = self.financial_client.get_balance_sheet(
            ticker, period="annual", limit=periods
        )
        data["cash_flows"] = self.financial_client.get_cash_flow_statement(
            ticker, period="annual", limit=periods
        )
        
        # Financial metrics and ratios
        if include_ratios:
            data["financial_metrics"] = self.financial_client.get_financial_metrics(
                ticker, period="ttm", limit=periods
            )
        
        # Insider trades
        data["insider_trades"] = self.financial_client.get_insider_trades(ticker, limit=20)
        
        # Price data for valuation
        data["prices"] = self.financial_client.get_prices(ticker, interval="day")
        
        return data
    
    def _create_analysis_prompt(
        self,
        ticker: str,
        data: Dict[str, Any]
    ) -> str:
        """Create fundamental analysis prompt for LLM."""
        prompt = f"Perform fundamental analysis on {ticker} based on the following data:\n\n"
        
        # Company overview
        if data.get("company_facts"):
            facts = data["company_facts"]
            prompt += f"COMPANY OVERVIEW:\n"
            prompt += f"Name: {facts.get('name', ticker)}\n"
            prompt += f"Sector: {facts.get('sector', 'N/A')}\n"
            prompt += f"Industry: {facts.get('industry', 'N/A')}\n"
            prompt += f"Market Cap: ${facts.get('market_cap', 0):,.0f}\n"
            prompt += f"Description: {facts.get('description', 'N/A')[:200]}...\n\n"
        
        # Income statement analysis
        if data.get("income_statements") and len(data["income_statements"]) > 0:
            prompt += "INCOME STATEMENT TRENDS:\n"
            for i, stmt in enumerate(data["income_statements"][:3]):
                year = stmt.get('fiscal_year', f'Period {i+1}')
                revenue = stmt.get('revenue', 0)
                net_income = stmt.get('net_income', 0)
                gross_profit = stmt.get('gross_profit', 0)
                operating_income = stmt.get('operating_income', 0)
                
                prompt += f"\n{year}:\n"
                prompt += f"  Revenue: ${revenue:,.0f}\n"
                prompt += f"  Gross Profit: ${gross_profit:,.0f}\n"
                prompt += f"  Operating Income: ${operating_income:,.0f}\n"
                prompt += f"  Net Income: ${net_income:,.0f}\n"
                
                if revenue > 0:
                    prompt += f"  Gross Margin: {(gross_profit/revenue)*100:.2f}%\n"
                    prompt += f"  Operating Margin: {(operating_income/revenue)*100:.2f}%\n"
                    prompt += f"  Net Margin: {(net_income/revenue)*100:.2f}%\n"
            prompt += "\n"
        
        # Balance sheet analysis
        if data.get("balance_sheets") and len(data["balance_sheets"]) > 0:
            prompt += "BALANCE SHEET HIGHLIGHTS:\n"
            bs = data["balance_sheets"][0]
            total_assets = bs.get('total_assets', 0)
            total_liabilities = bs.get('total_liabilities', 0)
            total_equity = bs.get('total_equity', 0)
            cash = bs.get('cash_and_equivalents', 0)
            total_debt = bs.get('total_debt', 0)
            
            prompt += f"Total Assets: ${total_assets:,.0f}\n"
            prompt += f"Total Liabilities: ${total_liabilities:,.0f}\n"
            prompt += f"Total Equity: ${total_equity:,.0f}\n"
            prompt += f"Cash & Equivalents: ${cash:,.0f}\n"
            prompt += f"Total Debt: ${total_debt:,.0f}\n"
            
            if total_equity > 0:
                prompt += f"Debt-to-Equity: {total_debt/total_equity:.2f}\n"
            prompt += "\n"
        
        # Cash flow analysis
        if data.get("cash_flows") and len(data["cash_flows"]) > 0:
            prompt += "CASH FLOW ANALYSIS:\n"
            cf = data["cash_flows"][0]
            operating_cf = cf.get('operating_cash_flow', 0)
            investing_cf = cf.get('investing_cash_flow', 0)
            financing_cf = cf.get('financing_cash_flow', 0)
            free_cf = cf.get('free_cash_flow', 0)
            
            prompt += f"Operating Cash Flow: ${operating_cf:,.0f}\n"
            prompt += f"Investing Cash Flow: ${investing_cf:,.0f}\n"
            prompt += f"Financing Cash Flow: ${financing_cf:,.0f}\n"
            prompt += f"Free Cash Flow: ${free_cf:,.0f}\n\n"
        
        # Financial metrics and ratios
        if data.get("financial_metrics") and len(data["financial_metrics"]) > 0:
            prompt += "KEY FINANCIAL RATIOS:\n"
            metrics = data["financial_metrics"][0]
            
            prompt += f"P/E Ratio: {metrics.get('price_to_earnings_ratio', 'N/A')}\n"
            prompt += f"P/B Ratio: {metrics.get('price_to_book_ratio', 'N/A')}\n"
            prompt += f"P/S Ratio: {metrics.get('price_to_sales_ratio', 'N/A')}\n"
            prompt += f"ROE: {metrics.get('return_on_equity', 'N/A')}\n"
            prompt += f"ROA: {metrics.get('return_on_assets', 'N/A')}\n"
            prompt += f"Current Ratio: {metrics.get('current_ratio', 'N/A')}\n"
            prompt += f"Quick Ratio: {metrics.get('quick_ratio', 'N/A')}\n"
            prompt += f"Debt/Equity: {metrics.get('debt_to_equity', 'N/A')}\n\n"
        
        # Insider trading activity
        if data.get("insider_trades") and len(data["insider_trades"]) > 0:
            prompt += "RECENT INSIDER TRADING:\n"
            buys = sum(1 for t in data["insider_trades"] if t.get('transaction_type') == 'BUY')
            sells = sum(1 for t in data["insider_trades"] if t.get('transaction_type') == 'SELL')
            prompt += f"Recent Insider Buys: {buys}\n"
            prompt += f"Recent Insider Sells: {sells}\n\n"
        
        prompt += "\nProvide a comprehensive fundamental analysis with:\n"
        prompt += "1. Financial health assessment (profitability, liquidity, solvency)\n"
        prompt += "2. Growth trajectory and sustainability\n"
        prompt += "3. Competitive advantages and moat strength\n"
        prompt += "4. Valuation assessment (overvalued, fairly valued, undervalued)\n"
        prompt += "5. Investment recommendation (BUY/HOLD/SELL) with confidence level (1-10)\n"
        prompt += "6. Margin of safety analysis\n"
        prompt += "7. Key risks and catalysts\n"
        prompt += "8. Fair value estimate and target price\n"
        
        return prompt
    
    def compare_companies(
        self,
        tickers: List[str],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare fundamental metrics across multiple companies.
        
        Args:
            tickers: List of stock ticker symbols
            metrics: Specific metrics to compare
            
        Returns:
            Comparison analysis
        """
        if metrics is None:
            metrics = [
                "price_to_earnings_ratio",
                "price_to_book_ratio",
                "return_on_equity",
                "debt_to_equity",
                "revenue_growth"
            ]
        
        comparison_data = {}
        
        for ticker in tickers:
            financial_metrics = self.financial_client.get_financial_metrics(ticker, limit=1)
            if financial_metrics:
                comparison_data[ticker] = financial_metrics[0]
        
        # Create comparison prompt
        prompt = f"Compare the following companies based on fundamental metrics:\n\n"
        
        for metric in metrics:
            prompt += f"\n{metric.replace('_', ' ').title()}:\n"
            for ticker, data in comparison_data.items():
                value = data.get(metric, 'N/A')
                prompt += f"  {ticker}: {value}\n"
        
        prompt += "\nProvide a comparative analysis highlighting:\n"
        prompt += "1. Which company has the strongest fundamentals\n"
        prompt += "2. Relative valuation (which is cheapest/most expensive)\n"
        prompt += "3. Growth prospects comparison\n"
        prompt += "4. Risk profile comparison\n"
        prompt += "5. Investment ranking (best to worst)\n"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "tickers": tickers,
            "comparison": response.content,
            "data": comparison_data,
            "timestamp": self._get_timestamp()
        }
    
    def screen_undervalued_stocks(
        self,
        max_pe: float = 15,
        min_roe: float = 15,
        max_debt_equity: float = 0.5
    ) -> List[str]:
        """
        Screen for potentially undervalued stocks based on fundamental criteria.
        
        Args:
            max_pe: Maximum P/E ratio
            min_roe: Minimum ROE percentage
            max_debt_equity: Maximum debt-to-equity ratio
            
        Returns:
            List of ticker symbols meeting criteria
        """
        # This would integrate with a screening service
        # For now, return placeholder
        return []
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        return datetime.now().isoformat()
