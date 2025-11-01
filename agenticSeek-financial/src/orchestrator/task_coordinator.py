"""Task Coordinator for orchestrating multiple agents in parallel and aggregating results."""

import asyncio
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from ..agents import (
    StockAnalystAgent,
    CryptoAnalystAgent,
    TechnicalAgent,
    FundamentalAgent
)
from .multi_llm_router import MultiLLMRouter, TaskComplexity


class TaskCoordinator:
    """
    Coordinates multiple agents to perform comprehensive analysis.
    Handles parallel execution, result aggregation, and conflict resolution.
    """
    
    def __init__(
        self,
        llm_router: Optional[MultiLLMRouter] = None,
        max_workers: int = 4
    ):
        """
        Initialize Task Coordinator.
        
        Args:
            llm_router: Multi-LLM router for intelligent model selection
            max_workers: Maximum number of parallel workers
        """
        self.llm_router = llm_router or MultiLLMRouter()
        self.max_workers = max_workers
        self.agents = {}
    
    def _get_or_create_agent(
        self,
        agent_type: str,
        complexity: TaskComplexity = TaskComplexity.MODERATE
    ) -> Any:
        """Get or create an agent instance."""
        if agent_type in self.agents:
            return self.agents[agent_type]
        
        # Route to appropriate LLM
        llm, provider, model = self.llm_router.route_task(
            f"{agent_type} analysis",
            complexity=complexity
        )
        
        # Create agent
        if agent_type == "stock_analyst":
            agent = StockAnalystAgent(llm_provider=provider, model_name=model)
        elif agent_type == "crypto_analyst":
            agent = CryptoAnalystAgent(llm_provider=provider, model_name=model)
        elif agent_type == "technical":
            agent = TechnicalAgent(llm_provider=provider, model_name=model)
        elif agent_type == "fundamental":
            agent = FundamentalAgent(llm_provider=provider, model_name=model)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        self.agents[agent_type] = agent
        return agent
    
    def analyze_stock_comprehensive(
        self,
        ticker: str,
        include_fundamental: bool = True,
        include_technical: bool = True,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive stock analysis using multiple agents.
        
        Args:
            ticker: Stock ticker symbol
            include_fundamental: Include fundamental analysis
            include_technical: Include technical analysis
            parallel: Execute agents in parallel
            
        Returns:
            Aggregated analysis results
        """
        tasks = []
        
        # Define analysis tasks
        if include_fundamental:
            tasks.append(("fundamental", ticker))
        
        if include_technical:
            tasks.append(("technical", ticker))
        
        # Always include stock analyst for comprehensive view
        tasks.append(("stock_analyst", ticker))
        
        # Execute tasks
        if parallel:
            results = self._execute_parallel(tasks)
        else:
            results = self._execute_sequential(tasks)
        
        # Aggregate results
        aggregated = self._aggregate_stock_results(ticker, results)
        
        return aggregated
    
    def analyze_crypto_comprehensive(
        self,
        symbol: str,
        include_onchain: bool = True,
        include_technical: bool = True,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive cryptocurrency analysis.
        
        Args:
            symbol: Crypto symbol (e.g., "BTC", "ETH")
            include_onchain: Include on-chain metrics
            include_technical: Include technical analysis
            parallel: Execute agents in parallel
            
        Returns:
            Aggregated analysis results
        """
        tasks = []
        
        # Crypto analyst
        tasks.append(("crypto_analyst", symbol, {"include_onchain": include_onchain}))
        
        # Technical analysis
        if include_technical:
            tasks.append(("technical", symbol))
        
        # Execute tasks
        if parallel:
            results = self._execute_parallel(tasks)
        else:
            results = self._execute_sequential(tasks)
        
        # Aggregate results
        aggregated = self._aggregate_crypto_results(symbol, results)
        
        return aggregated
    
    def compare_assets(
        self,
        tickers: List[str],
        asset_type: str = "stock"
    ) -> Dict[str, Any]:
        """
        Compare multiple assets using appropriate agents.
        
        Args:
            tickers: List of ticker symbols
            asset_type: Type of asset ("stock" or "crypto")
            
        Returns:
            Comparison results
        """
        if asset_type == "stock":
            agent = self._get_or_create_agent("fundamental", TaskComplexity.MODERATE)
            return agent.compare_companies(tickers)
        elif asset_type == "crypto":
            # Analyze each crypto and compare
            results = {}
            agent = self._get_or_create_agent("crypto_analyst", TaskComplexity.MODERATE)
            
            for ticker in tickers:
                results[ticker] = agent.analyze_crypto(ticker)
            
            return {
                "comparison_type": "crypto",
                "assets": tickers,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise ValueError(f"Unsupported asset type: {asset_type}")
    
    def _execute_parallel(self, tasks: List[tuple]) -> Dict[str, Any]:
        """Execute tasks in parallel using ThreadPoolExecutor."""
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {}
            
            for task in tasks:
                agent_type = task[0]
                args = task[1:] if len(task) > 1 else ()
                
                future = executor.submit(self._execute_agent_task, agent_type, *args)
                future_to_task[future] = agent_type
            
            for future in as_completed(future_to_task):
                agent_type = future_to_task[future]
                try:
                    result = future.result()
                    results[agent_type] = result
                except Exception as e:
                    print(f"Agent {agent_type} failed: {e}")
                    results[agent_type] = {"error": str(e)}
        
        return results
    
    def _execute_sequential(self, tasks: List[tuple]) -> Dict[str, Any]:
        """Execute tasks sequentially."""
        results = {}
        
        for task in tasks:
            agent_type = task[0]
            args = task[1:] if len(task) > 1 else ()
            
            try:
                result = self._execute_agent_task(agent_type, *args)
                results[agent_type] = result
            except Exception as e:
                print(f"Agent {agent_type} failed: {e}")
                results[agent_type] = {"error": str(e)}
        
        return results
    
    def _execute_agent_task(self, agent_type: str, *args) -> Dict[str, Any]:
        """Execute a single agent task."""
        agent = self._get_or_create_agent(agent_type)
        
        # Extract kwargs if present
        kwargs = {}
        if args and isinstance(args[-1], dict):
            kwargs = args[-1]
            args = args[:-1]
        
        # Call appropriate method based on agent type
        if agent_type == "stock_analyst":
            return agent.analyze_stock(args[0])
        elif agent_type == "crypto_analyst":
            return agent.analyze_crypto(args[0], **kwargs)
        elif agent_type == "technical":
            return agent.analyze_technical(args[0])
        elif agent_type == "fundamental":
            return agent.analyze_fundamentals(args[0])
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    def _aggregate_stock_results(
        self,
        ticker: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aggregate results from multiple stock analysis agents."""
        aggregated = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "analyses": results,
            "summary": self._create_summary(results),
            "consensus": self._determine_consensus(results)
        }
        
        return aggregated
    
    def _aggregate_crypto_results(
        self,
        symbol: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aggregate results from multiple crypto analysis agents."""
        aggregated = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "analyses": results,
            "summary": self._create_summary(results),
            "consensus": self._determine_consensus(results)
        }
        
        return aggregated
    
    def _create_summary(self, results: Dict[str, Any]) -> str:
        """Create a summary from multiple agent results."""
        summaries = []
        
        for agent_type, result in results.items():
            if "error" in result:
                summaries.append(f"{agent_type}: Error - {result['error']}")
            elif "analysis" in result:
                # Extract first few sentences
                analysis = result["analysis"]
                first_sentence = analysis.split(".")[0] if analysis else "No analysis"
                summaries.append(f"{agent_type}: {first_sentence}")
        
        return "\n".join(summaries)
    
    def _determine_consensus(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Determine consensus recommendation from multiple agents."""
        recommendations = []
        confidence_scores = []
        
        for agent_type, result in results.items():
            if "error" in result:
                continue
            
            analysis = result.get("analysis", "")
            
            # Simple keyword extraction (in production, use more sophisticated NLP)
            if "BUY" in analysis.upper():
                recommendations.append("BUY")
            elif "SELL" in analysis.upper():
                recommendations.append("SELL")
            elif "HOLD" in analysis.upper():
                recommendations.append("HOLD")
            
            # Extract confidence if present
            if "confidence" in analysis.lower():
                # Try to extract number
                import re
                confidence_match = re.search(r'confidence[:\s]+(\d+)', analysis.lower())
                if confidence_match:
                    confidence_scores.append(int(confidence_match.group(1)))
        
        # Determine consensus
        if not recommendations:
            return {
                "recommendation": "INSUFFICIENT_DATA",
                "confidence": 0,
                "agreement": 0
            }
        
        # Count recommendations
        buy_count = recommendations.count("BUY")
        sell_count = recommendations.count("SELL")
        hold_count = recommendations.count("HOLD")
        
        total = len(recommendations)
        
        # Determine majority
        if buy_count > sell_count and buy_count > hold_count:
            consensus = "BUY"
            agreement = buy_count / total
        elif sell_count > buy_count and sell_count > hold_count:
            consensus = "SELL"
            agreement = sell_count / total
        elif hold_count > buy_count and hold_count > sell_count:
            consensus = "HOLD"
            agreement = hold_count / total
        else:
            consensus = "MIXED"
            agreement = max(buy_count, sell_count, hold_count) / total
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 5
        
        return {
            "recommendation": consensus,
            "confidence": round(avg_confidence, 1),
            "agreement": round(agreement * 100, 1),
            "breakdown": {
                "BUY": buy_count,
                "SELL": sell_count,
                "HOLD": hold_count
            }
        }
    
    def batch_analyze(
        self,
        tickers: List[str],
        asset_type: str = "stock",
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze multiple assets in batch.
        
        Args:
            tickers: List of ticker symbols
            asset_type: Type of asset ("stock" or "crypto")
            analysis_type: Type of analysis
            
        Returns:
            Batch analysis results
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_ticker = {}
            
            for ticker in tickers:
                if asset_type == "stock":
                    future = executor.submit(
                        self.analyze_stock_comprehensive,
                        ticker
                    )
                elif asset_type == "crypto":
                    future = executor.submit(
                        self.analyze_crypto_comprehensive,
                        ticker
                    )
                else:
                    continue
                
                future_to_ticker[future] = ticker
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    result = future.result()
                    results[ticker] = result
                except Exception as e:
                    print(f"Analysis failed for {ticker}: {e}")
                    results[ticker] = {"error": str(e)}
        
        return {
            "batch_analysis": True,
            "asset_type": asset_type,
            "total_analyzed": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
