"""Technical Agent for technical analysis of stocks and cryptocurrencies."""

from typing import Dict, List, Optional, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

from ..mcp_clients import TradingViewClient


class TechnicalAgent:
    """Agent specialized in technical analysis using charts and indicators."""
    
    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.1
    ):
        """
        Initialize Technical Agent.
        
        Args:
            llm_provider: LLM provider ("openai", "anthropic", "groq")
            model_name: Model name
            temperature: Temperature for LLM
        """
        self.llm = self._initialize_llm(llm_provider, model_name, temperature)
        self.tradingview_client = TradingViewClient()
        
        self.system_prompt = """You are an expert technical analyst with deep knowledge of chart patterns, indicators, and price action.
Your role is to analyze price charts and technical indicators to identify trading opportunities.

You should consider:
1. Trend analysis (uptrend, downtrend, sideways)
2. Support and resistance levels
3. Technical indicators (RSI, MACD, Moving Averages, Bollinger Bands, Stochastic)
4. Chart patterns (head and shoulders, triangles, flags, wedges)
5. Volume analysis
6. Momentum and volatility
7. Entry and exit points

Provide clear, actionable trading signals with specific price levels and risk management recommendations.
Always include stop-loss and take-profit levels."""
    
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
    
    def analyze_technical(
        self,
        ticker: str,
        interval: str = "1D",
        include_patterns: bool = True
    ) -> Dict[str, Any]:
        """
        Perform technical analysis on a ticker.
        
        Args:
            ticker: Stock or crypto ticker symbol
            interval: Time interval ("1m", "5m", "1h", "1D", "1W")
            include_patterns: Include chart pattern detection
            
        Returns:
            Technical analysis results
        """
        # Gather technical data
        data = self._gather_technical_data(ticker, interval, include_patterns)
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(ticker, interval, data)
        
        # Get LLM analysis
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "ticker": ticker,
            "interval": interval,
            "analysis": response.content,
            "data": data,
            "timestamp": self._get_timestamp()
        }
    
    def _gather_technical_data(
        self,
        ticker: str,
        interval: str,
        include_patterns: bool
    ) -> Dict[str, Any]:
        """Gather technical data from TradingView."""
        data = {}
        
        # Get comprehensive technical indicators
        data["indicators"] = self.tradingview_client.get_technical_indicators(ticker, interval)
        
        # Get technical summary
        data["summary"] = self.tradingview_client.get_technical_summary(ticker, interval)
        
        # Get specific indicators
        data["rsi"] = self.tradingview_client.get_rsi(ticker, interval)
        data["macd"] = self.tradingview_client.get_macd(ticker, interval)
        data["moving_averages"] = self.tradingview_client.get_moving_averages(ticker, interval)
        data["bollinger_bands"] = self.tradingview_client.get_bollinger_bands(ticker, interval)
        data["stochastic"] = self.tradingview_client.get_stochastic(ticker, interval)
        
        # Get support and resistance levels
        data["support_resistance"] = self.tradingview_client.get_support_resistance(ticker, interval)
        
        # Get pivot points
        data["pivot_points"] = self.tradingview_client.get_pivot_points(ticker, interval)
        
        # Get chart patterns if requested
        if include_patterns:
            data["patterns"] = self.tradingview_client.get_chart_patterns(ticker, interval)
        
        return data
    
    def _create_analysis_prompt(
        self,
        ticker: str,
        interval: str,
        data: Dict[str, Any]
    ) -> str:
        """Create technical analysis prompt for LLM."""
        prompt = f"Perform technical analysis on {ticker} ({interval} timeframe):\n\n"
        
        # Technical summary
        if data.get("summary"):
            summary = data["summary"]
            prompt += "TECHNICAL SUMMARY:\n"
            prompt += f"Overall Signal: {summary.get('summary', 'N/A')}\n"
            prompt += f"Trend: {summary.get('trend', 'N/A')}\n"
            prompt += f"Momentum: {summary.get('momentum', 'N/A')}\n\n"
        
        # RSI
        if data.get("rsi"):
            rsi = data["rsi"]
            prompt += f"RSI(14): {rsi.get('value', 'N/A')}\n"
            prompt += f"RSI Signal: {rsi.get('signal', 'N/A')}\n\n"
        
        # MACD
        if data.get("macd"):
            macd = data["macd"]
            prompt += "MACD:\n"
            prompt += f"MACD Line: {macd.get('macd', 'N/A')}\n"
            prompt += f"Signal Line: {macd.get('signal', 'N/A')}\n"
            prompt += f"Histogram: {macd.get('histogram', 'N/A')}\n"
            prompt += f"Signal: {macd.get('macd_signal', 'N/A')}\n\n"
        
        # Moving Averages
        if data.get("moving_averages"):
            ma = data["moving_averages"]
            prompt += "MOVING AVERAGES:\n"
            for period, value in ma.items():
                if isinstance(value, (int, float)):
                    prompt += f"MA{period}: {value:.2f}\n"
            prompt += "\n"
        
        # Bollinger Bands
        if data.get("bollinger_bands"):
            bb = data["bollinger_bands"]
            prompt += "BOLLINGER BANDS:\n"
            prompt += f"Upper Band: {bb.get('upper', 'N/A')}\n"
            prompt += f"Middle Band: {bb.get('middle', 'N/A')}\n"
            prompt += f"Lower Band: {bb.get('lower', 'N/A')}\n"
            prompt += f"Current Price Position: {bb.get('position', 'N/A')}\n\n"
        
        # Stochastic
        if data.get("stochastic"):
            stoch = data["stochastic"]
            prompt += "STOCHASTIC OSCILLATOR:\n"
            prompt += f"%K: {stoch.get('k', 'N/A')}\n"
            prompt += f"%D: {stoch.get('d', 'N/A')}\n"
            prompt += f"Signal: {stoch.get('signal', 'N/A')}\n\n"
        
        # Support and Resistance
        if data.get("support_resistance"):
            sr = data["support_resistance"]
            prompt += "SUPPORT & RESISTANCE LEVELS:\n"
            if sr.get("resistance"):
                prompt += f"Resistance: {', '.join(map(str, sr['resistance']))}\n"
            if sr.get("support"):
                prompt += f"Support: {', '.join(map(str, sr['support']))}\n"
            prompt += "\n"
        
        # Pivot Points
        if data.get("pivot_points"):
            pivot = data["pivot_points"]
            prompt += "PIVOT POINTS:\n"
            prompt += f"Pivot: {pivot.get('pivot', 'N/A')}\n"
            prompt += f"R1: {pivot.get('r1', 'N/A')}, R2: {pivot.get('r2', 'N/A')}, R3: {pivot.get('r3', 'N/A')}\n"
            prompt += f"S1: {pivot.get('s1', 'N/A')}, S2: {pivot.get('s2', 'N/A')}, S3: {pivot.get('s3', 'N/A')}\n\n"
        
        # Chart Patterns
        if data.get("patterns"):
            patterns = data["patterns"]
            if patterns:
                prompt += "DETECTED CHART PATTERNS:\n"
                for pattern in patterns[:5]:
                    prompt += f"- {pattern.get('name', 'N/A')}: {pattern.get('signal', 'N/A')}\n"
                prompt += "\n"
        
        prompt += "\nProvide technical analysis with:\n"
        prompt += "1. Current trend and momentum assessment\n"
        prompt += "2. Key support and resistance levels\n"
        prompt += "3. Trading signal (BUY/SELL/HOLD)\n"
        prompt += "4. Entry point (specific price)\n"
        prompt += "5. Stop-loss level\n"
        prompt += "6. Take-profit targets (multiple levels)\n"
        prompt += "7. Risk/reward ratio\n"
        prompt += "8. Timeframe for the trade\n"
        
        return prompt
    
    def get_trading_signals(
        self,
        tickers: List[str],
        interval: str = "1D"
    ) -> List[Dict[str, Any]]:
        """
        Get trading signals for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            interval: Time interval
            
        Returns:
            List of trading signals
        """
        signals = []
        
        for ticker in tickers:
            analysis = self.analyze_technical(ticker, interval, include_patterns=False)
            signals.append({
                "ticker": ticker,
                "signal": self._extract_signal(analysis["analysis"]),
                "analysis": analysis["analysis"]
            })
        
        return signals
    
    def _extract_signal(self, analysis_text: str) -> str:
        """Extract trading signal from analysis text."""
        analysis_lower = analysis_text.lower()
        
        if "buy" in analysis_lower and "strong buy" in analysis_lower:
            return "STRONG_BUY"
        elif "buy" in analysis_lower:
            return "BUY"
        elif "sell" in analysis_lower and "strong sell" in analysis_lower:
            return "STRONG_SELL"
        elif "sell" in analysis_lower:
            return "SELL"
        else:
            return "HOLD"
    
    def compare_technical_strength(
        self,
        tickers: List[str],
        interval: str = "1D"
    ) -> Dict[str, Any]:
        """
        Compare technical strength of multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            interval: Time interval
            
        Returns:
            Comparative technical analysis
        """
        analyses = []
        for ticker in tickers:
            analysis = self.analyze_technical(ticker, interval, include_patterns=False)
            analyses.append(analysis)
        
        # Create comparison prompt
        prompt = "Compare the technical strength of the following assets and rank them:\n\n"
        for analysis in analyses:
            prompt += f"{analysis['ticker']} ({interval}):\n{analysis['analysis']}\n\n"
        
        prompt += "\nRank them from strongest to weakest technical setup with rationale."
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "comparison": response.content,
            "analyses": analyses,
            "timestamp": self._get_timestamp()
        }
    
    def identify_breakout_opportunities(
        self,
        tickers: List[str],
        interval: str = "1D"
    ) -> List[Dict[str, Any]]:
        """
        Identify potential breakout opportunities.
        
        Args:
            tickers: List of ticker symbols
            interval: Time interval
            
        Returns:
            List of breakout opportunities
        """
        opportunities = []
        
        for ticker in tickers:
            data = self._gather_technical_data(ticker, interval, include_patterns=True)
            
            # Check for breakout conditions
            is_breakout = self._check_breakout_conditions(data)
            
            if is_breakout:
                analysis = self.analyze_technical(ticker, interval, include_patterns=True)
                opportunities.append({
                    "ticker": ticker,
                    "breakout_type": is_breakout,
                    "analysis": analysis
                })
        
        return opportunities
    
    def _check_breakout_conditions(self, data: Dict[str, Any]) -> Optional[str]:
        """Check if technical data indicates a breakout."""
        # Simple breakout detection logic
        # In production, this would be more sophisticated
        
        summary = data.get("summary", {})
        rsi = data.get("rsi", {})
        
        if summary.get("summary") == "STRONG_BUY" and rsi.get("value", 0) > 60:
            return "bullish_breakout"
        elif summary.get("summary") == "STRONG_SELL" and rsi.get("value", 100) < 40:
            return "bearish_breakout"
        
        return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
