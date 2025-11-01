#!/usr/bin/env python3
"""
AgenticSeek Financial - AI-Powered Financial Analysis System
Main CLI entry point for the application.
"""

import argparse
import sys
import json
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv

from src.orchestrator import TaskCoordinator, MultiLLMRouter
from src.agents import (
    StockAnalystAgent,
    CryptoAnalystAgent,
    TechnicalAgent,
    FundamentalAgent
)

# Load environment variables
load_dotenv()

# Initialize Rich console for beautiful output
console = Console()


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          AgenticSeek Financial Analysis System            ║
    ║                                                           ║
    ║     AI-Powered Stock & Crypto Analysis with Multi-LLM     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def analyze_stock(
    ticker: str,
    analysis_type: str = "comprehensive",
    output_format: str = "text"
):
    """Analyze a stock."""
    console.print(f"\n[bold green]Analyzing {ticker}...[/bold green]\n")
    
    try:
        coordinator = TaskCoordinator()
        
        if analysis_type == "comprehensive":
            result = coordinator.analyze_stock_comprehensive(ticker)
        elif analysis_type == "fundamental":
            agent = FundamentalAgent()
            result = agent.analyze_fundamentals(ticker)
        elif analysis_type == "technical":
            agent = TechnicalAgent()
            result = agent.analyze_technical(ticker)
        else:
            console.print(f"[red]Unknown analysis type: {analysis_type}[/red]")
            return
        
        # Display results
        if output_format == "json":
            console.print_json(data=result)
        else:
            display_analysis_result(result, ticker)
    
    except Exception as e:
        console.print(f"[red]Error analyzing {ticker}: {e}[/red]")
        import traceback
        traceback.print_exc()


def analyze_crypto(
    symbol: str,
    include_onchain: bool = True,
    output_format: str = "text"
):
    """Analyze a cryptocurrency."""
    console.print(f"\n[bold green]Analyzing {symbol}...[/bold green]\n")
    
    try:
        coordinator = TaskCoordinator()
        result = coordinator.analyze_crypto_comprehensive(
            symbol,
            include_onchain=include_onchain
        )
        
        # Display results
        if output_format == "json":
            console.print_json(data=result)
        else:
            display_analysis_result(result, symbol)
    
    except Exception as e:
        console.print(f"[red]Error analyzing {symbol}: {e}[/red]")
        import traceback
        traceback.print_exc()


def compare_assets(
    tickers: list,
    asset_type: str = "stock",
    output_format: str = "text"
):
    """Compare multiple assets."""
    console.print(f"\n[bold green]Comparing {', '.join(tickers)}...[/bold green]\n")
    
    try:
        coordinator = TaskCoordinator()
        result = coordinator.compare_assets(tickers, asset_type=asset_type)
        
        # Display results
        if output_format == "json":
            console.print_json(data=result)
        else:
            display_comparison_result(result, tickers)
    
    except Exception as e:
        console.print(f"[red]Error comparing assets: {e}[/red]")
        import traceback
        traceback.print_exc()


def batch_analyze(
    tickers: list,
    asset_type: str = "stock",
    output_format: str = "text"
):
    """Batch analyze multiple assets."""
    console.print(f"\n[bold green]Batch analyzing {len(tickers)} {asset_type}s...[/bold green]\n")
    
    try:
        coordinator = TaskCoordinator()
        result = coordinator.batch_analyze(tickers, asset_type=asset_type)
        
        # Display results
        if output_format == "json":
            console.print_json(data=result)
        else:
            display_batch_result(result)
    
    except Exception as e:
        console.print(f"[red]Error in batch analysis: {e}[/red]")
        import traceback
        traceback.print_exc()


def display_analysis_result(result: dict, ticker: str):
    """Display analysis result in a formatted way."""
    # Title
    console.print(Panel(
        f"[bold cyan]Analysis Report for {ticker}[/bold cyan]",
        expand=False
    ))
    
    # Consensus (if available)
    if "consensus" in result:
        consensus = result["consensus"]
        recommendation = consensus.get("recommendation", "N/A")
        confidence = consensus.get("confidence", 0)
        agreement = consensus.get("agreement", 0)
        
        # Color code recommendation
        rec_color = "green" if recommendation == "BUY" else "red" if recommendation == "SELL" else "yellow"
        
        console.print(f"\n[bold]Consensus Recommendation:[/bold] [{rec_color}]{recommendation}[/{rec_color}]")
        console.print(f"[bold]Confidence:[/bold] {confidence}/10")
        console.print(f"[bold]Agreement:[/bold] {agreement}%")
        
        if "breakdown" in consensus:
            breakdown = consensus["breakdown"]
            console.print(f"\n[bold]Agent Breakdown:[/bold]")
            console.print(f"  BUY: {breakdown.get('BUY', 0)}")
            console.print(f"  HOLD: {breakdown.get('HOLD', 0)}")
            console.print(f"  SELL: {breakdown.get('SELL', 0)}")
    
    # Individual analyses
    if "analyses" in result:
        console.print("\n[bold cyan]═══ Detailed Analyses ═══[/bold cyan]\n")
        
        for agent_type, analysis_data in result["analyses"].items():
            if "error" in analysis_data:
                console.print(f"[red]{agent_type}: Error - {analysis_data['error']}[/red]\n")
                continue
            
            console.print(f"[bold yellow]▶ {agent_type.replace('_', ' ').title()}[/bold yellow]")
            
            if "analysis" in analysis_data:
                # Display as markdown for better formatting
                md = Markdown(analysis_data["analysis"])
                console.print(md)
            
            console.print("\n" + "─" * 80 + "\n")
    
    # Single analysis (non-comprehensive)
    elif "analysis" in result:
        md = Markdown(result["analysis"])
        console.print(md)


def display_comparison_result(result: dict, tickers: list):
    """Display comparison result."""
    console.print(Panel(
        f"[bold cyan]Comparison: {', '.join(tickers)}[/bold cyan]",
        expand=False
    ))
    
    if "comparison" in result:
        md = Markdown(result["comparison"])
        console.print(md)
    elif "results" in result:
        for ticker, data in result["results"].items():
            console.print(f"\n[bold yellow]▶ {ticker}[/bold yellow]")
            if "analysis" in data:
                console.print(data["analysis"][:500] + "...")


def display_batch_result(result: dict):
    """Display batch analysis result."""
    console.print(Panel(
        f"[bold cyan]Batch Analysis Results[/bold cyan]",
        expand=False
    ))
    
    total = result.get("total_analyzed", 0)
    console.print(f"\n[bold]Total Analyzed:[/bold] {total}")
    
    if "results" in result:
        # Create summary table
        table = Table(title="Analysis Summary")
        table.add_column("Ticker", style="cyan")
        table.add_column("Recommendation", style="green")
        table.add_column("Confidence", style="yellow")
        table.add_column("Status", style="white")
        
        for ticker, data in result["results"].items():
            if "error" in data:
                table.add_row(ticker, "ERROR", "N/A", "Failed")
            elif "consensus" in data:
                consensus = data["consensus"]
                rec = consensus.get("recommendation", "N/A")
                conf = str(consensus.get("confidence", "N/A"))
                table.add_row(ticker, rec, conf, "Complete")
            else:
                table.add_row(ticker, "N/A", "N/A", "Incomplete")
        
        console.print(table)


def list_models():
    """List available LLM models."""
    console.print("\n[bold cyan]Available LLM Models[/bold cyan]\n")
    
    router = MultiLLMRouter()
    available = router.get_available_models()
    
    if not available:
        console.print("[red]No LLM providers configured. Please set API keys in .env file.[/red]")
        return
    
    for provider, models in available.items():
        console.print(f"\n[bold yellow]{provider.upper()}[/bold yellow]")
        for model in models:
            cost = router.COST_MAP.get(model, {})
            input_cost = cost.get("input", 0)
            output_cost = cost.get("output", 0)
            console.print(f"  • {model}")
            console.print(f"    Cost: ${input_cost:.2f}/${output_cost:.2f} per 1M tokens (input/output)")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AgenticSeek Financial - AI-Powered Financial Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Stock analysis command
    stock_parser = subparsers.add_parser("stock", help="Analyze a stock")
    stock_parser.add_argument("ticker", help="Stock ticker symbol (e.g., AAPL)")
    stock_parser.add_argument(
        "--type",
        choices=["comprehensive", "fundamental", "technical"],
        default="comprehensive",
        help="Type of analysis"
    )
    stock_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    # Crypto analysis command
    crypto_parser = subparsers.add_parser("crypto", help="Analyze a cryptocurrency")
    crypto_parser.add_argument("symbol", help="Crypto symbol (e.g., BTC, ETH)")
    crypto_parser.add_argument(
        "--no-onchain",
        action="store_true",
        help="Exclude on-chain metrics"
    )
    crypto_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare multiple assets")
    compare_parser.add_argument("tickers", nargs="+", help="Ticker symbols to compare")
    compare_parser.add_argument(
        "--type",
        choices=["stock", "crypto"],
        default="stock",
        help="Asset type"
    )
    compare_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    # Batch analysis command
    batch_parser = subparsers.add_parser("batch", help="Batch analyze multiple assets")
    batch_parser.add_argument("tickers", nargs="+", help="Ticker symbols to analyze")
    batch_parser.add_argument(
        "--type",
        choices=["stock", "crypto"],
        default="stock",
        help="Asset type"
    )
    batch_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    # List models command
    subparsers.add_parser("models", help="List available LLM models")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Execute command
    if args.command == "stock":
        analyze_stock(args.ticker, args.type, args.format)
    elif args.command == "crypto":
        analyze_crypto(args.symbol, not args.no_onchain, args.format)
    elif args.command == "compare":
        compare_assets(args.tickers, args.type, args.format)
    elif args.command == "batch":
        batch_analyze(args.tickers, args.type, args.format)
    elif args.command == "models":
        list_models()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
