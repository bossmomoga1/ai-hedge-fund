"""Crypto Analyst Agent for cryptocurrency analysis."""

from typing import Dict, List, Optional, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

from ..mcp_clients import CryptoClient


class CryptoAnalystAgent:
    """Agent specialized in cryptocurrency analysis."""
    
    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.1
    ):
        """
        Initialize Crypto Analyst Agent.
        
        Args:
            llm_provider: LLM provider ("openai", "anthropic", "groq")
            model_name: Model name
            temperature: Temperature for LLM
        """
        self.llm = self._initialize_llm(llm_provider, model_name, temperature)
        self.crypto_client = CryptoClient()
        
        self.system_prompt = """You are an expert cryptocurrency analyst with deep knowledge of blockchain technology, DeFi, and crypto markets.
Your role is to analyze cryptocurrencies comprehensively and provide actionable investment insights.

You should consider:
1. Market metrics (market cap, volume, price trends)
2. On-chain metrics (active addresses, transaction volume, network activity)
3. Technical indicators (RSI, MACD, support/resistance)
4. DeFi metrics (TVL, protocol revenue, token utility)
5. Market sentiment and fear/greed index
6. Fundamental factors (tokenomics, team, technology, adoption)
7. Regulatory environment and risks

Provide clear, concise analysis with specific recommendations (BUY, HOLD, SELL) and confidence levels.
Always emphasize the high-risk nature of cryptocurrency investments."""
    
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
    
    def analyze_crypto(
        self,
        symbol: str,
        include_onchain: bool = True,
        include_defi: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze a cryptocurrency comprehensively.
        
        Args:
            symbol: Crypto symbol (e.g., "BTC", "ETH")
            include_onchain: Include on-chain metrics
            include_defi: Include DeFi metrics (if applicable)
            
        Returns:
            Analysis results with recommendation
        """
        # Gather crypto data
        data = self._gather_crypto_data(symbol, include_onchain, include_defi)
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(symbol, data)
        
        # Get LLM analysis
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "symbol": symbol,
            "analysis": response.content,
            "data": data,
            "timestamp": self._get_timestamp()
        }
    
    def _gather_crypto_data(
        self,
        symbol: str,
        include_onchain: bool,
        include_defi: bool
    ) -> Dict[str, Any]:
        """Gather cryptocurrency data from multiple sources."""
        data = {}
        
        # Basic price and market data
        data["price"] = self.crypto_client.get_crypto_price(symbol)
        data["market_data"] = self.crypto_client.get_market_data(symbol)
        data["ohlcv"] = self.crypto_client.get_crypto_ohlcv(symbol)
        
        # On-chain metrics
        if include_onchain:
            data["onchain_metrics"] = self.crypto_client.get_on_chain_metrics(symbol)
        
        # DeFi metrics
        if include_defi:
            # Try to get DeFi metrics (may not be available for all cryptos)
            protocol_name = symbol.lower()
            data["defi_metrics"] = self.crypto_client.get_defi_metrics(protocol_name)
        
        # Market sentiment
        data["fear_greed"] = self.crypto_client.get_fear_greed_index()
        
        # News
        data["news"] = self.crypto_client.get_crypto_news(symbol, limit=10)
        
        # Exchange listings
        data["exchanges"] = self.crypto_client.get_crypto_exchanges(symbol)
        
        return data
    
    def _create_analysis_prompt(
        self,
        symbol: str,
        data: Dict[str, Any]
    ) -> str:
        """Create analysis prompt for LLM."""
        prompt = f"Analyze {symbol} cryptocurrency based on the following data:\n\n"
        
        # Price and market data
        if data.get("price"):
            price_data = data["price"]
            prompt += f"Current Price: ${price_data.get('price', 'N/A')}\n"
            prompt += f"24h Change: {price_data.get('price_change_24h', 'N/A')}%\n"
            prompt += f"7d Change: {price_data.get('price_change_7d', 'N/A')}%\n\n"
        
        if data.get("market_data"):
            market = data["market_data"]
            prompt += "MARKET METRICS:\n"
            prompt += f"Market Cap: ${market.get('market_cap', 'N/A'):,.0f}\n"
            prompt += f"24h Volume: ${market.get('volume_24h', 'N/A'):,.0f}\n"
            prompt += f"Circulating Supply: {market.get('circulating_supply', 'N/A'):,.0f}\n"
            prompt += f"Max Supply: {market.get('max_supply', 'N/A')}\n"
            prompt += f"Market Cap Rank: #{market.get('market_cap_rank', 'N/A')}\n\n"
        
        # On-chain metrics
        if data.get("onchain_metrics"):
            onchain = data["onchain_metrics"]
            prompt += "ON-CHAIN METRICS:\n"
            prompt += f"Active Addresses: {onchain.get('active_addresses', 'N/A')}\n"
            prompt += f"Transaction Count: {onchain.get('transaction_count', 'N/A')}\n"
            prompt += f"Network Activity: {onchain.get('network_activity', 'N/A')}\n\n"
        
        # DeFi metrics
        if data.get("defi_metrics"):
            defi = data["defi_metrics"]
            prompt += "DEFI METRICS:\n"
            prompt += f"TVL: ${defi.get('tvl', 'N/A'):,.0f}\n"
            prompt += f"24h Volume: ${defi.get('volume_24h', 'N/A'):,.0f}\n"
            prompt += f"Protocol Revenue: ${defi.get('revenue', 'N/A'):,.0f}\n\n"
        
        # Market sentiment
        if data.get("fear_greed"):
            fg = data["fear_greed"]
            prompt += f"Fear & Greed Index: {fg.get('value', 'N/A')} ({fg.get('classification', 'N/A')})\n\n"
        
        # Recent news
        if data.get("news"):
            prompt += "RECENT NEWS:\n"
            for i, news_item in enumerate(data["news"][:3], 1):
                prompt += f"{i}. {news_item.get('title', 'N/A')}\n"
            prompt += "\n"
        
        prompt += "\nProvide a comprehensive analysis with:\n"
        prompt += "1. Current market position and trends\n"
        prompt += "2. Key strengths and weaknesses\n"
        prompt += "3. Investment recommendation (BUY/HOLD/SELL)\n"
        prompt += "4. Confidence level (1-10)\n"
        prompt += "5. Key risks and catalysts\n"
        prompt += "6. Price targets (short-term and long-term)\n"
        prompt += "7. Risk assessment (emphasize volatility)\n"
        
        return prompt
    
    def get_top_cryptos(
        self,
        limit: int = 20,
        sort_by: str = "market_cap"
    ) -> List[Dict[str, Any]]:
        """
        Get top cryptocurrencies.
        
        Args:
            limit: Maximum number of results
            sort_by: Sort criteria
            
        Returns:
            List of top cryptocurrencies
        """
        return self.crypto_client.get_top_cryptocurrencies(limit=limit, sort_by=sort_by)
    
    def get_trending_cryptos(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get trending cryptocurrencies.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of trending cryptocurrencies
        """
        return self.crypto_client.get_trending_cryptos(limit=limit)
    
    def compare_cryptos(
        self,
        symbols: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple cryptocurrencies.
        
        Args:
            symbols: List of crypto symbols
            
        Returns:
            Comparative analysis
        """
        analyses = []
        for symbol in symbols:
            analysis = self.analyze_crypto(symbol, include_onchain=False)
            analyses.append(analysis)
        
        # Create comparison prompt
        prompt = "Compare the following cryptocurrencies and rank them:\n\n"
        for analysis in analyses:
            prompt += f"{analysis['symbol']}:\n{analysis['analysis']}\n\n"
        
        prompt += "\nProvide a ranking with rationale for each position, considering risk/reward profiles."
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "comparison": response.content,
            "cryptos": analyses,
            "timestamp": self._get_timestamp()
        }
    
    def analyze_defi_protocol(
        self,
        protocol: str
    ) -> Dict[str, Any]:
        """
        Analyze a DeFi protocol.
        
        Args:
            protocol: Protocol name
            
        Returns:
            DeFi protocol analysis
        """
        # Get DeFi metrics
        defi_data = self.crypto_client.get_defi_metrics(protocol)
        
        if not defi_data:
            return {
                "protocol": protocol,
                "error": "Unable to fetch DeFi metrics",
                "timestamp": self._get_timestamp()
            }
        
        # Create analysis prompt
        prompt = f"Analyze {protocol} DeFi protocol based on the following metrics:\n\n"
        prompt += f"TVL: ${defi_data.get('tvl', 'N/A'):,.0f}\n"
        prompt += f"24h Volume: ${defi_data.get('volume_24h', 'N/A'):,.0f}\n"
        prompt += f"Protocol Revenue: ${defi_data.get('revenue', 'N/A'):,.0f}\n"
        prompt += f"Number of Users: {defi_data.get('users', 'N/A')}\n\n"
        prompt += "Provide analysis of:\n"
        prompt += "1. Protocol health and sustainability\n"
        prompt += "2. Competitive position\n"
        prompt += "3. Revenue model and tokenomics\n"
        prompt += "4. Risks and opportunities\n"
        prompt += "5. Investment recommendation\n"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "protocol": protocol,
            "analysis": response.content,
            "data": defi_data,
            "timestamp": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
