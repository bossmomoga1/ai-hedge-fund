"""Stock Analyst Agent for comprehensive stock analysis."""

from typing import Dict, List, Optional, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

from ..mcp_clients import (
    StockScreenClient,
    StockFlowClient,
    FinancialDatasetsClient,
    TradingViewClient
)


class StockAnalystAgent:
    """Agent for analyzing stocks using fundamental and technical data."""
    
    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.1
    ):
        """
        Initialize Stock Analyst Agent.
        
        Args:
            llm_provider: LLM provider ("openai", "anthropic", "groq")
            model_name: Model name
            temperature: Temperature for LLM
        """
        self.llm = self._initialize_llm(llm_provider, model_name, temperature)
        self.stockscreen_client = StockScreenClient()
        self.stockflow_client = StockFlowClient()
        self.financial_client = FinancialDatasetsClient()
        self.tradingview_client = TradingViewClient()
        
        self.system_prompt = """You are an expert stock analyst with deep knowledge of fundamental and technical analysis.
Your role is to analyze stocks comprehensively using multiple data sources and provide actionable investment insights.

You should consider:
1. Fundamental metrics (P/E ratio, revenue growth, profit margins, debt levels)
2. Technical indicators (RSI, MACD, moving averages, support/resistance)
3. Volume and flow patterns (unusual volume, institutional flow, dark pool activity)
4. Market sentiment and news
5. Valuation relative to peers and historical averages

Provide clear, concise analysis with specific recommendations (BUY, HOLD, SELL) and confidence levels."""
    
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
    
    def analyze_stock(
        self,
        ticker: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze a stock comprehensively.
        
        Args:
            ticker: Stock ticker symbol
            analysis_type: Type of analysis ("comprehensive", "fundamental", "technical")
            
        Returns:
            Analysis results with recommendation
        """
        # Gather data from multiple sources
        data = self._gather_stock_data(ticker, analysis_type)
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(ticker, data, analysis_type)
        
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
    
    def _gather_stock_data(
        self,
        ticker: str,
        analysis_type: str
    ) -> Dict[str, Any]:
        """Gather data from multiple sources."""
        data = {}
        
        # Always get basic company info
        data["company_facts"] = self.financial_client.get_company_facts(ticker)
        
        if analysis_type in ["comprehensive", "fundamental"]:
            # Fundamental data
            data["financial_metrics"] = self.financial_client.get_financial_metrics(ticker, limit=4)
            data["income_statement"] = self.financial_client.get_income_statement(ticker, limit=2)
            data["balance_sheet"] = self.financial_client.get_balance_sheet(ticker, limit=2)
            data["cash_flow"] = self.financial_client.get_cash_flow_statement(ticker, limit=2)
        
        if analysis_type in ["comprehensive", "technical"]:
            # Technical data
            data["technical_indicators"] = self.tradingview_client.get_technical_indicators(ticker)
            data["technical_summary"] = self.tradingview_client.get_technical_summary(ticker)
            data["chart_patterns"] = self.tradingview_client.get_chart_patterns(ticker)
            data["support_resistance"] = self.tradingview_client.get_support_resistance(ticker)
        
        if analysis_type == "comprehensive":
            # Volume and flow data
            data["volume_analysis"] = self.stockflow_client.get_volume_analysis(ticker)
            data["order_flow"] = self.stockflow_client.get_order_flow(ticker)
            data["institutional_flow"] = self.stockflow_client.get_institutional_flow(ticker)
            
            # Additional insights
            data["insider_trades"] = self.financial_client.get_insider_trades(ticker, limit=20)
        
        return data
    
    def _create_analysis_prompt(
        self,
        ticker: str,
        data: Dict[str, Any],
        analysis_type: str
    ) -> str:
        """Create analysis prompt for LLM."""
        prompt = f"Analyze {ticker} stock based on the following data:\n\n"
        
        # Add company overview
        if data.get("company_facts"):
            facts = data["company_facts"]
            prompt += f"Company: {facts.get('name', ticker)}\n"
            prompt += f"Sector: {facts.get('sector', 'N/A')}\n"
            prompt += f"Industry: {facts.get('industry', 'N/A')}\n"
            prompt += f"Market Cap: ${facts.get('market_cap', 0):,.0f}\n\n"
        
        # Add fundamental data
        if data.get("financial_metrics"):
            prompt += "FUNDAMENTAL METRICS:\n"
            metrics = data["financial_metrics"][0] if data["financial_metrics"] else {}
            prompt += f"P/E Ratio: {metrics.get('price_to_earnings_ratio', 'N/A')}\n"
            prompt += f"Revenue Growth: {metrics.get('revenue_growth', 'N/A')}\n"
            prompt += f"Profit Margin: {metrics.get('net_profit_margin', 'N/A')}\n"
            prompt += f"ROE: {metrics.get('return_on_equity', 'N/A')}\n"
            prompt += f"Debt/Equity: {metrics.get('debt_to_equity', 'N/A')}\n\n"
        
        # Add technical data
        if data.get("technical_summary"):
            prompt += "TECHNICAL ANALYSIS:\n"
            tech = data["technical_summary"]
            prompt += f"Overall Signal: {tech.get('summary', 'N/A')}\n"
            prompt += f"RSI: {tech.get('rsi', 'N/A')}\n"
            prompt += f"MACD: {tech.get('macd_signal', 'N/A')}\n\n"
        
        # Add volume insights
        if data.get("volume_analysis"):
            prompt += "VOLUME ANALYSIS:\n"
            vol = data["volume_analysis"]
            prompt += f"Average Volume: {vol.get('avg_volume', 'N/A')}\n"
            prompt += f"Volume Trend: {vol.get('trend', 'N/A')}\n\n"
        
        prompt += f"\nProvide a {analysis_type} analysis with:\n"
        prompt += "1. Key strengths and weaknesses\n"
        prompt += "2. Investment recommendation (BUY/HOLD/SELL)\n"
        prompt += "3. Confidence level (1-10)\n"
        prompt += "4. Key risks and catalysts\n"
        prompt += "5. Price target (if applicable)\n"
        
        return prompt
    
    def screen_stocks(
        self,
        criteria: Dict[str, Any],
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Screen stocks based on criteria.
        
        Args:
            criteria: Screening criteria
            limit: Maximum number of results
            
        Returns:
            List of stocks matching criteria
        """
        return self.stockscreen_client.screen_stocks(criteria, limit=limit)
    
    def compare_stocks(
        self,
        tickers: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple stocks.
        
        Args:
            tickers: List of stock tickers
            
        Returns:
            Comparative analysis
        """
        analyses = []
        for ticker in tickers:
            analysis = self.analyze_stock(ticker, analysis_type="fundamental")
            analyses.append(analysis)
        
        # Create comparison prompt
        prompt = "Compare the following stocks and rank them:\n\n"
        for analysis in analyses:
            prompt += f"{analysis['ticker']}:\n{analysis['analysis']}\n\n"
        
        prompt += "\nProvide a ranking with rationale for each position."
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "comparison": response.content,
            "stocks": analyses,
            "timestamp": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
