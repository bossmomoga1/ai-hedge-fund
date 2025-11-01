# AgenticSeek Financial - AI-Powered Financial Analysis System

A comprehensive AI-powered financial analysis system that leverages multiple specialized agents and LLM providers to analyze stocks and cryptocurrencies. The system uses intelligent routing to optimize cost and performance while providing deep, multi-faceted analysis.

## 🌟 Features

- **Multi-Agent Architecture**: Specialized agents for different types of analysis
  - Stock Analyst Agent - Comprehensive stock analysis
  - Crypto Analyst Agent - Cryptocurrency and DeFi analysis
  - Technical Agent - Technical indicators and chart patterns
  - Fundamental Agent - Financial statements and valuation

- **Intelligent LLM Routing**: Automatically selects the best LLM based on:
  - Task complexity
  - Cost optimization
  - Provider availability
  - Performance requirements

- **Multiple Data Sources**: Integrates with various financial data APIs
  - Financial Datasets API - Financial statements and metrics
  - TradingView - Technical indicators and charts
  - StockScreen - Stock screening and filtering
  - StockFlow - Volume and order flow analysis
  - Crypto APIs - Cryptocurrency and on-chain data

- **Flexible Analysis Modes**:
  - Comprehensive analysis (all agents)
  - Fundamental-only analysis
  - Technical-only analysis
  - Batch analysis for multiple assets
  - Comparative analysis

- **Beautiful CLI Interface**: Rich terminal output with formatted tables, panels, and markdown

## 📋 Prerequisites

- Python 3.11 or higher
- API keys for at least one LLM provider (OpenAI, Anthropic, Groq, or Google)
- Optional: API keys for financial data sources

## 🚀 Installation

1. **Clone the repository**:
```bash
cd agenticSeek-financial
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
Create a `.env` file in the root directory:
```bash
# LLM Provider API Keys (at least one required)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GROQ_API_KEY=your-groq-api-key
GOOGLE_API_KEY=your-google-api-key

# Financial Data API Keys (optional)
FINANCIAL_DATASETS_API_KEY=your-financial-datasets-key
TRADINGVIEW_API_KEY=your-tradingview-key
STOCKSCREEN_API_KEY=your-stockscreen-key
STOCKFLOW_API_KEY=your-stockflow-key
CRYPTO_API_KEY=your-crypto-api-key
```

## 📖 Usage

### Command Line Interface

The system provides a comprehensive CLI with multiple commands:

#### 1. Analyze a Stock

```bash
# Comprehensive analysis (all agents)
python main.py stock AAPL

# Fundamental analysis only
python main.py stock AAPL --type fundamental

# Technical analysis only
python main.py stock AAPL --type technical

# Output as JSON
python main.py stock AAPL --format json
```

#### 2. Analyze a Cryptocurrency

```bash
# Full crypto analysis with on-chain metrics
python main.py crypto BTC

# Without on-chain metrics
python main.py crypto ETH --no-onchain

# Output as JSON
python main.py crypto BTC --format json
```

#### 3. Compare Multiple Assets

```bash
# Compare stocks
python main.py compare AAPL MSFT GOOGL

# Compare cryptocurrencies
python main.py compare BTC ETH SOL --type crypto

# Output as JSON
python main.py compare AAPL MSFT --format json
```

#### 4. Batch Analysis

```bash
# Analyze multiple stocks
python main.py batch AAPL MSFT GOOGL NVDA TSLA

# Analyze multiple cryptos
python main.py batch BTC ETH SOL ADA DOT --type crypto
```

#### 5. List Available Models

```bash
python main.py models
```

### Python API

You can also use the system programmatically:

```python
from src.orchestrator import TaskCoordinator, MultiLLMRouter
from src.agents import StockAnalystAgent, CryptoAnalystAgent

# Initialize coordinator
coordinator = TaskCoordinator()

# Analyze a stock
result = coordinator.analyze_stock_comprehensive("AAPL")
print(result)

# Analyze a cryptocurrency
result = coordinator.analyze_crypto_comprehensive("BTC")
print(result)

# Compare assets
result = coordinator.compare_assets(["AAPL", "MSFT", "GOOGL"])
print(result)

# Batch analysis
result = coordinator.batch_analyze(["AAPL", "MSFT", "GOOGL"])
print(result)
```

### Using Individual Agents

```python
from src.agents import FundamentalAgent, TechnicalAgent

# Fundamental analysis
fundamental_agent = FundamentalAgent(
    llm_provider="openai",
    model_name="gpt-4o"
)
result = fundamental_agent.analyze_fundamentals("AAPL")

# Technical analysis
technical_agent = TechnicalAgent(
    llm_provider="anthropic",
    model_name="claude-3-5-sonnet-20241022"
)
result = technical_agent.analyze_technical("AAPL", interval="1D")
```

### Using LLM Router

```python
from src.orchestrator import MultiLLMRouter, TaskComplexity

# Initialize router
router = MultiLLMRouter(cost_optimization=True)

# Route a task
llm, provider, model = router.route_task(
    "Analyze AAPL stock",
    complexity=TaskComplexity.COMPLEX
)

# Get model recommendations
provider, model = router.recommend_model("analysis", budget=5.0)

# Estimate costs
cost = router.estimate_cost("openai", "gpt-4o", 1000, 500)
```

## 🏗️ Architecture

### Project Structure

```
agenticSeek-financial/
├── src/
│   ├── agents/                 # Specialized analysis agents
│   │   ├── stock_analyst_agent.py
│   │   ├── crypto_analyst_agent.py
│   │   ├── technical_agent.py
│   │   └── fundamental_agent.py
│   ├── mcp_clients/           # Data source clients
│   │   ├── stockscreen_client.py
│   │   ├── stockflow_client.py
│   │   ├── financial_datasets_client.py
│   │   ├── tradingview_client.py
│   │   └── crypto_clients.py
│   ├── orchestrator/          # Multi-agent coordination
│   │   ├── multi_llm_router.py
│   │   └── task_coordinator.py
│   ├── tools/                 # LangChain-compatible tools
│   │   ├── stock_tools.py
│   │   └── crypto_tools.py
│   └── config/                # Configuration files
│       ├── mcp_config.yaml
│       └── llm_config.yaml
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

### Agent Descriptions

#### Stock Analyst Agent
Provides comprehensive stock analysis using multiple data sources including fundamental metrics, technical indicators, volume analysis, and market sentiment.

#### Crypto Analyst Agent
Specializes in cryptocurrency analysis with support for on-chain metrics, DeFi protocols, market data, and crypto-specific indicators.

#### Technical Agent
Focuses on technical analysis using indicators like RSI, MACD, moving averages, Bollinger Bands, support/resistance levels, and chart patterns.

#### Fundamental Agent
Analyzes financial statements (income statement, balance sheet, cash flow), calculates financial ratios, and performs valuation analysis.

### Multi-LLM Router

The router intelligently selects LLMs based on:

- **Task Complexity Levels**:
  - Simple: Quick lookups, basic queries
  - Moderate: Standard analysis, comparisons
  - Complex: Deep analysis, detailed reports
  - Critical: High-stakes decisions

- **Cost Optimization**: Automatically selects cheaper models for simpler tasks

- **Provider Fallback**: Falls back to available providers if preferred one is unavailable

## ⚙️ Configuration

### LLM Configuration (`src/config/llm_config.yaml`)

Configure LLM providers, models, routing rules, and cost optimization settings.

Key sections:
- `providers`: LLM provider configurations
- `routing`: Task complexity routing rules
- `agents`: Agent-specific LLM preferences
- `cost_optimization`: Budget and cost tracking

### MCP Configuration (`src/config/mcp_config.yaml`)

Configure financial data source clients, API endpoints, rate limiting, and caching.

Key sections:
- `financial_datasets`: Financial data API settings
- `tradingview`: Technical analysis API settings
- `crypto`: Cryptocurrency data API settings
- `rate_limiting`: Request rate limits
- `caching`: Data caching configuration

## 🔧 Advanced Features

### Parallel Execution

The Task Coordinator can execute multiple agents in parallel for faster analysis:

```python
coordinator = TaskCoordinator(max_workers=4)
result = coordinator.analyze_stock_comprehensive("AAPL", parallel=True)
```

### Custom Agent Configuration

```python
from src.agents import StockAnalystAgent

agent = StockAnalystAgent(
    llm_provider="anthropic",
    model_name="claude-3-5-sonnet-20241022",
    temperature=0.2
)
```

### Cost Tracking

```python
router = MultiLLMRouter(cost_optimization=True)
cost = router.estimate_cost("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
print(f"Estimated cost: ${cost:.4f}")
```

## 📊 Output Examples

### Stock Analysis Output

```
╔═══════════════════════════════════════════════════════════╗
║          AgenticSeek Financial Analysis System            ║
╚═══════════════════════════════════════════════════════════╝

Analyzing AAPL...

┌─────────────────────────────────────────────────────────┐
│           Analysis Report for AAPL                      │
└─────────────────────────────────────────────────────────┘

Consensus Recommendation: BUY
Confidence: 8.5/10
Agreement: 85.0%

Agent Breakdown:
  BUY: 3
  HOLD: 1
  SELL: 0

═══ Detailed Analyses ═══

▶ Fundamental Agent
[Detailed fundamental analysis...]

▶ Technical Agent
[Detailed technical analysis...]

▶ Stock Analyst
[Comprehensive analysis...]
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This software is for educational and research purposes only. It is not intended for real trading or investment decisions. Always consult with a qualified financial advisor before making investment decisions.

## 🐛 Troubleshooting

### Common Issues

1. **No LLM providers available**
   - Ensure at least one LLM API key is set in `.env`
   - Check that the API key is valid

2. **Financial data not available**
   - Some data sources require API keys
   - Check rate limits on your API keys
   - Verify ticker symbols are correct

3. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.11+ required)

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

## 🙏 Acknowledgments

- LangChain for the agent framework
- OpenAI, Anthropic, Groq, and Google for LLM APIs
- Financial data providers for market data
- Rich library for beautiful terminal output
