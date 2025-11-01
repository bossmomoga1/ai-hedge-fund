#!/usr/bin/env python3
"""Basic test script to verify imports and basic functionality."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test agent imports
        from src.agents import (
            StockAnalystAgent,
            CryptoAnalystAgent,
            TechnicalAgent,
            FundamentalAgent
        )
        print("✓ Agents imported successfully")
        
        # Test MCP client imports
        from src.mcp_clients import (
            StockScreenClient,
            StockFlowClient,
            FinancialDatasetsClient,
            TradingViewClient,
            CryptoClient
        )
        print("✓ MCP clients imported successfully")
        
        # Test orchestrator imports
        from src.orchestrator import (
            MultiLLMRouter,
            TaskCoordinator
        )
        print("✓ Orchestrator imported successfully")
        
        # Test tools imports
        from src.tools import (
            get_stock_price_tool,
            get_financial_metrics_tool,
            get_crypto_price_tool
        )
        print("✓ Tools imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_router():
    """Test the Multi-LLM Router."""
    print("\nTesting Multi-LLM Router...")
    
    try:
        from src.orchestrator import MultiLLMRouter, TaskComplexity
        
        router = MultiLLMRouter()
        print("✓ Router initialized")
        
        # Check available providers
        available = router.available_providers
        print(f"  Available providers: {[k for k, v in available.items() if v]}")
        
        # Get available models
        models = router.get_available_models()
        print(f"  Available models: {len(sum(models.values(), []))} total")
        
        return True
    except Exception as e:
        print(f"✗ Router test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_clients():
    """Test MCP clients initialization."""
    print("\nTesting MCP Clients...")
    
    try:
        from src.mcp_clients import (
            FinancialDatasetsClient,
            TradingViewClient,
            CryptoClient
        )
        
        # Initialize clients (without making API calls)
        financial_client = FinancialDatasetsClient()
        print("✓ FinancialDatasetsClient initialized")
        
        tradingview_client = TradingViewClient()
        print("✓ TradingViewClient initialized")
        
        crypto_client = CryptoClient()
        print("✓ CryptoClient initialized")
        
        return True
    except Exception as e:
        print(f"✗ Client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AgenticSeek Financial - Basic Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Router", test_router()))
    results.append(("Clients", test_clients()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
