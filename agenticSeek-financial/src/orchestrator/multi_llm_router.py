"""Multi-LLM Router for intelligent task routing based on complexity and cost."""

import os
from typing import Dict, Any, Optional, List
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI


class TaskComplexity(Enum):
    """Task complexity levels."""
    SIMPLE = "simple"  # Quick lookups, simple queries
    MODERATE = "moderate"  # Standard analysis
    COMPLEX = "complex"  # Deep analysis, reasoning
    CRITICAL = "critical"  # High-stakes decisions


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    GOOGLE = "google"


class MultiLLMRouter:
    """
    Intelligent router that selects the best LLM for a given task based on:
    - Task complexity
    - Cost optimization
    - Provider availability
    - Performance requirements
    """
    
    # Cost per 1M tokens (approximate, in USD)
    COST_MAP = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
        "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
        "gemini-2.0-flash-exp": {"input": 0.00, "output": 0.00},  # Free tier
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    }
    
    # Model recommendations by complexity
    COMPLEXITY_MODELS = {
        TaskComplexity.SIMPLE: [
            ("groq", "llama-3.1-8b-instant"),
            ("google", "gemini-2.0-flash-exp"),
            ("openai", "gpt-4o-mini"),
        ],
        TaskComplexity.MODERATE: [
            ("openai", "gpt-4o-mini"),
            ("google", "gemini-2.0-flash-exp"),
            ("anthropic", "claude-3-5-haiku-20241022"),
            ("groq", "llama-3.3-70b-versatile"),
        ],
        TaskComplexity.COMPLEX: [
            ("openai", "gpt-4o"),
            ("anthropic", "claude-3-5-sonnet-20241022"),
            ("google", "gemini-1.5-pro"),
        ],
        TaskComplexity.CRITICAL: [
            ("anthropic", "claude-3-opus-20240229"),
            ("openai", "gpt-4o"),
            ("anthropic", "claude-3-5-sonnet-20241022"),
        ],
    }
    
    def __init__(
        self,
        default_provider: Optional[str] = None,
        default_model: Optional[str] = None,
        cost_optimization: bool = True,
        temperature: float = 0.1
    ):
        """
        Initialize Multi-LLM Router.
        
        Args:
            default_provider: Default LLM provider to use
            default_model: Default model name
            cost_optimization: Enable cost-based routing
            temperature: Default temperature for LLMs
        """
        self.default_provider = default_provider
        self.default_model = default_model
        self.cost_optimization = cost_optimization
        self.temperature = temperature
        self.available_providers = self._check_available_providers()
    
    def _check_available_providers(self) -> Dict[str, bool]:
        """Check which LLM providers have API keys configured."""
        return {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "groq": bool(os.getenv("GROQ_API_KEY")),
            "google": bool(os.getenv("GOOGLE_API_KEY")),
        }
    
    def route_task(
        self,
        task_description: str,
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        max_cost: Optional[float] = None
    ) -> tuple[Any, str, str]:
        """
        Route a task to the most appropriate LLM.
        
        Args:
            task_description: Description of the task
            complexity: Task complexity level
            max_cost: Maximum acceptable cost per 1M tokens
            
        Returns:
            Tuple of (LLM instance, provider name, model name)
        """
        # If default provider/model specified, use it
        if self.default_provider and self.default_model:
            if self.available_providers.get(self.default_provider, False):
                llm = self._create_llm(self.default_provider, self.default_model)
                return llm, self.default_provider, self.default_model
        
        # Get recommended models for this complexity
        recommended_models = self.COMPLEXITY_MODELS.get(complexity, [])
        
        # Filter by availability and cost
        for provider, model in recommended_models:
            if not self.available_providers.get(provider, False):
                continue
            
            # Check cost constraint
            if max_cost and self.cost_optimization:
                model_cost = self.COST_MAP.get(model, {})
                avg_cost = (model_cost.get("input", 0) + model_cost.get("output", 0)) / 2
                if avg_cost > max_cost:
                    continue
            
            # Create and return LLM
            try:
                llm = self._create_llm(provider, model)
                return llm, provider, model
            except Exception as e:
                print(f"Failed to create LLM {provider}/{model}: {e}")
                continue
        
        # Fallback: try any available provider
        for provider, available in self.available_providers.items():
            if available:
                fallback_model = self._get_fallback_model(provider)
                try:
                    llm = self._create_llm(provider, fallback_model)
                    return llm, provider, fallback_model
                except Exception as e:
                    print(f"Failed to create fallback LLM {provider}/{fallback_model}: {e}")
                    continue
        
        raise RuntimeError("No LLM providers available. Please configure API keys.")
    
    def _create_llm(self, provider: str, model: str) -> Any:
        """Create an LLM instance."""
        if provider == "openai":
            return ChatOpenAI(model=model, temperature=self.temperature)
        elif provider == "anthropic":
            return ChatAnthropic(model=model, temperature=self.temperature)
        elif provider == "groq":
            return ChatGroq(model=model, temperature=self.temperature)
        elif provider == "google":
            return ChatGoogleGenerativeAI(model=model, temperature=self.temperature)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _get_fallback_model(self, provider: str) -> str:
        """Get a fallback model for a provider."""
        fallback_map = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-haiku-20241022",
            "groq": "llama-3.1-8b-instant",
            "google": "gemini-2.0-flash-exp",
        }
        return fallback_map.get(provider, "gpt-4o-mini")
    
    def estimate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Estimate cost for a task.
        
        Args:
            provider: LLM provider
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        costs = self.COST_MAP.get(model, {"input": 0, "output": 0})
        input_cost = (input_tokens / 1_000_000) * costs["input"]
        output_cost = (output_tokens / 1_000_000) * costs["output"]
        return input_cost + output_cost
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models by provider."""
        available = {}
        for provider, is_available in self.available_providers.items():
            if is_available:
                models = [
                    model for p, model in sum(self.COMPLEXITY_MODELS.values(), [])
                    if p == provider
                ]
                available[provider] = list(set(models))
        return available
    
    def recommend_model(
        self,
        task_type: str,
        budget: Optional[float] = None
    ) -> tuple[str, str]:
        """
        Recommend a model for a specific task type.
        
        Args:
            task_type: Type of task ("analysis", "screening", "comparison", "quick_lookup")
            budget: Budget constraint in USD per 1M tokens
            
        Returns:
            Tuple of (provider, model)
        """
        # Map task types to complexity
        task_complexity_map = {
            "quick_lookup": TaskComplexity.SIMPLE,
            "screening": TaskComplexity.SIMPLE,
            "comparison": TaskComplexity.MODERATE,
            "analysis": TaskComplexity.COMPLEX,
            "deep_analysis": TaskComplexity.CRITICAL,
        }
        
        complexity = task_complexity_map.get(task_type, TaskComplexity.MODERATE)
        
        # Get recommended models
        recommended = self.COMPLEXITY_MODELS.get(complexity, [])
        
        # Filter by budget and availability
        for provider, model in recommended:
            if not self.available_providers.get(provider, False):
                continue
            
            if budget:
                costs = self.COST_MAP.get(model, {})
                avg_cost = (costs.get("input", 0) + costs.get("output", 0)) / 2
                if avg_cost > budget:
                    continue
            
            return provider, model
        
        # Fallback
        for provider, available in self.available_providers.items():
            if available:
                return provider, self._get_fallback_model(provider)
        
        raise RuntimeError("No suitable model found")
