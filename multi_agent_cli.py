#!/usr/bin/env python3
"""
Multi-Agent Pipeline CLI - Command-line interface for the TRUE multi-agent system
Supports dynamic routing, visualization, and multiple output formats
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from multi_agent_pipeline import MultiAgentPipeline
from utils.graph_visualizer import GraphVisualizer


class MultiAgentCLI:
    """CLI interface for multi-agent pipeline"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging"""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    def print_header(self, title: str):
        """Print formatted header"""
        width = 80
        print("\n" + "=" * width)
        print(f"  {title}".ljust(width))
        print("=" * width)
        
    def print_separator(self):
        """Print separator line"""
        print("-" * 80)
        
    def print_section(self, title: str):
        """Print section header"""
        print(f"\n▶ {title}")
        print("  " + "-" * 70)
        
    def visualize_graph(self, simple: bool = True):
        """Display graph visualization"""
        print("\n📊 GRAPH VISUALIZATION:")
        print()
        
        viz = GraphVisualizer()
        graph_text = viz.draw_ascii_graph(simplified=simple)
        print(graph_text)
        
        print("\n   Key:")
        print("   ● = Node")
        print("   → = Edge")
        print("   ⓡ = Conditional routing")
        
    def display_plan(self, plan: dict):
        """Display execution plan"""
        self.print_section("EXECUTION PLAN")
        
        print(f"  Query Type: {plan.get('query_type', 'unknown')}")
        print(f"  Complexity: {plan.get('complexity', 'unknown')}")
        print(f"  Estimated Sources: {plan.get('estimated_sources', 0)}")
        print(f"  Summary Depth: {plan.get('summary_depth', 'brief')}")
        
        if 'priority_agents' in plan:
            print(f"  Enabled Agents: {', '.join(plan['priority_agents'])}")
        
        print(f"  Content Evaluation: {'YES' if plan.get('needs_evaluation') else 'NO'}")
        print(f"  Multi-Format Output: {'YES' if plan.get('needs_formatting') else 'NO'}")
        
    def display_routing_path(self, routing_decisions: list, agent_history: list):
        """Display agent routing path"""
        self.print_section("AGENT EXECUTION PATH")
        
        print("  Routing Order:")
        for i, agent in enumerate(agent_history, 1):
            agent_emoji = {
                'planner': '🎯',
                'search': '🔍',
                'scraper': '🪄',
                'evaluator': '⭐',
                'summarizer': '📝',
                'formatter': '💾',
                'error_handler': '⚠️'
            }.get(agent, '●')
            
            print(f"    {i}. {agent_emoji} {agent.upper()}")
            
        if routing_decisions:
            print("\n  Routing Decisions:")
            for decision in routing_decisions:
                print(f"    • {decision}")
        
    def display_search_results(self, search_results: dict):
        """Display search results"""
        self.print_section("SEARCH RESULTS")
        
        results = search_results.get('results', [])
        if not results:
            print("  No search results found")
            return
        
        print(f"  Found {len(results)} URLs:\n")
        for i, result in enumerate(results[:5], 1):  # Show top 5
            url = result.get('url', 'N/A')
            title = result.get('title', 'No title')
            print(f"    {i}. {title}")
            print(f"       {url}\n")
        
        if len(results) > 5:
            print(f"    ... and {len(results) - 5} more URLs")
        
    def display_evaluation(self, evaluation_results: dict):
        """Display evaluation results"""
        self.print_section("CONTENT EVALUATION")
        
        if not evaluation_results:
            print("  No evaluation performed")
            return
        
        relevant_count = evaluation_results.get('relevant_count', 0)
        filtered_count = evaluation_results.get('filtered_count', 0)
        
        print(f"  🟢 Relevant Content: {relevant_count}")
        print(f"  🔴 Filtered Out: {filtered_count}")
        print(f"  📊 Average Relevance Score: {evaluation_results.get('avg_relevance', 0):.2f}")
        print(f"  ✅ Recommendation: {evaluation_results.get('recommendation', 'N/A')}")
        
    def display_summary(self, summary: str, max_length: int = 300):
        """Display summary"""
        self.print_section("SUMMARY")
        
        if not summary:
            print("  No summary generated")
            return
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length] + "...\n\n[Summary truncated]"
        
        print(f"  {summary}")
        
    def display_formatted_output(self, formatted_output: dict):
        """Display formatted output info"""
        self.print_section("FORMATTED OUTPUT")
        
        if not formatted_output:
            print("  No formatted output generated")
            return
        
        formats = formatted_output.get('formats', {})
        if not formats:
            print("  No formats available")
            return
        
        print(f"  Generated formats:")
        for format_name, file_info in formats.items():
            if file_info:
                file_path = file_info.get('file_path', 'N/A')
                size = file_info.get('size', 0)
                print(f"    ✓ {format_name.upper()}")
                print(f"      Path: {file_path}")
                print(f"      Size: {size:,} bytes\n")
        
    def display_results(self, result: dict, show_plan: bool = False, show_routing: bool = True):
        """Display pipeline results"""
        status = result.get('status', 'unknown')
        status_emoji = {
            'success': '✅',
            'partial_success': '⚠️',
            'failed': '❌'
        }.get(status, '❓')
        
        self.print_header(f"PIPELINE RESULTS {status_emoji}")
        
        # Status
        self.print_section("STATUS")
        print(f"  Status: {status.upper()}")
        if result.get('error_message'):
            print(f"  Error: {result['error_message']}")
        
        # Plan
        if show_plan and result.get('plan'):
            self.display_plan(result['plan'])
        
        # Routing
        if show_routing:
            self.display_routing_path(
                result.get('routing_decisions', []),
                result.get('agent_history', [])
            )
        
        # Search results
        if result.get('search_results'):
            self.display_search_results(result['search_results'])
        
        # Evaluation
        if result.get('evaluation_results'):
            self.display_evaluation(result['evaluation_results'])
        
        # Summary
        if result.get('summary'):
            self.display_summary(result['summary'])
        
        # Formatted output
        if result.get('formatted_output'):
            self.display_formatted_output(result['formatted_output'])
        
        self.print_footer(result)
        
    def print_footer(self, result: dict):
        """Print execution footer"""
        self.print_separator()
        
        timestamp = result.get('timestamp', datetime.now().isoformat())
        agent_count = len(result.get('agent_history', []))
        
        print(f"\n  📊 Statistics:")
        print(f"    • Agents Executed: {agent_count}")
        print(f"    • Timestamp: {timestamp}")
        print(f"    • Status: {result.get('status', 'unknown').upper()}")
        
        print("\n" + "=" * 80)
        
    def run(self, 
            query: str,
            enable_eval: bool = True,
            enable_format: bool = True,
            show_graph: bool = False,
            show_plan: bool = False,
            output_file: Optional[str] = None):
        """Run pipeline with query"""
        
        self.print_header(f"MULTI-AGENT PIPELINE")
        print(f"\nQuery: {query}\n")
        print(f"Configuration:")
        print(f"  • Evaluation: {'ENABLED' if enable_eval else 'DISABLED'}")
        print(f"  • Formatting: {'ENABLED' if enable_format else 'DISABLED'}")
        
        # Show graph if requested
        if show_graph:
            self.visualize_graph(simple=not show_graph)
        
        # Initialize and run pipeline
        try:
            print("\n" + "=" * 80)
            print("  STARTING EXECUTION...")
            print("=" * 80)
            
            pipeline = MultiAgentPipeline(
                enable_evaluation=enable_eval,
                enable_formatting=enable_format
            )
            
            result = pipeline.run(query)
            
            # Display results
            self.display_results(result, show_plan=show_plan, show_routing=True)
            
            # Save to file if requested
            if output_file:
                self.save_results(result, output_file)
                print(f"\n💾 Results saved to: {output_file}")
            
            return result
            
        except Exception as e:
            self.print_header("ERROR")
            print(f"❌ Pipeline execution failed:")
            print(f"   {str(e)}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    def save_results(self, result: dict, filepath: str):
        """Save results to JSON file"""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert non-serializable objects
        result_copy = result.copy()
        if isinstance(result_copy.get('plan'), dict):
            result_copy['plan'] = str(result_copy['plan'])
        
        with open(output_path, 'w') as f:
            json.dump(result_copy, f, indent=2, default=str)
        
        logging.info(f"Results saved to: {output_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Multi-Agent Pipeline CLI - TRUE multi-agent system with dynamic routing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python multi_agent_cli.py "What is machine learning?"
  
  # With evaluation disabled
  python multi_agent_cli.py "quick news" --no-eval
  
  # With formatting enabled
  python multi_agent_cli.py "topic" --enable-format
  
  # Show execution graph
  python multi_agent_cli.py "query" --show-graph
  
  # Show detailed plan
  python multi_agent_cli.py "query" --show-plan
  
  # Save results to file
  python multi_agent_cli.py "query" --output results.json
  
  # Verbose logging
  python multi_agent_cli.py "query" --verbose
        """
    )
    
    parser.add_argument(
        'query',
        help='Search query to process'
    )
    
    parser.add_argument(
        '--enable-eval',
        action='store_true',
        default=True,
        help='Enable content evaluation (default: True)'
    )
    
    parser.add_argument(
        '--no-eval',
        action='store_true',
        help='Disable content evaluation'
    )
    
    parser.add_argument(
        '--enable-format',
        action='store_true',
        default=False,
        help='Enable multi-format output'
    )
    
    parser.add_argument(
        '--disable-format',
        action='store_true',
        help='Disable multi-format output'
    )
    
    parser.add_argument(
        '--show-graph',
        action='store_true',
        help='Display agent graph visualization'
    )
    
    parser.add_argument(
        '--show-plan',
        action='store_true',
        help='Display execution plan details'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Save results to JSON file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Determine flags
    enable_eval = True
    if args.no_eval:
        enable_eval = False
    elif args.enable_eval is not None:
        enable_eval = args.enable_eval
    
    enable_format = False
    if args.enable_format:
        enable_format = True
    elif args.disable_format:
        enable_format = False
    
    # Run CLI
    cli = MultiAgentCLI(verbose=args.verbose)
    cli.run(
        query=args.query,
        enable_eval=enable_eval,
        enable_format=enable_format,
        show_graph=args.show_graph,
        show_plan=args.show_plan,
        output_file=args.output
    )


if __name__ == '__main__':
    main()
