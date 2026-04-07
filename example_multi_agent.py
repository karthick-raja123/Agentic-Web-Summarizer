#!/usr/bin/env python3
"""
Example Usage - Multi-Agent Pipeline
Demonstrates the TRUE multi-agent system with dynamic routing
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from multi_agent_pipeline import MultiAgentPipeline
from utils.graph_visualizer import GraphVisualizer


def example_basic():
    """Example 1: Basic usage with default settings"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Query Processing")
    print("="*80)
    
    pipeline = MultiAgentPipeline()
    
    query = "What are the benefits of machine learning in healthcare?"
    print(f"\nQuery: {query}\n")
    
    result = pipeline.run(query)
    
    print(f"\nResults:")
    print(f"  Status: {result['status']}")
    print(f"  Agents executed: {len(result['agent_history'])}")
    print(f"  Routing path: {' → '.join(result['agent_history'])}")
    print(f"\nSummary (first 200 chars):")
    print(f"  {result.get('summary', 'N/A')[:200]}...")


def example_news():
    """Example 2: Quick news query (simpler routing)"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Fast News Processing")
    print("="*80)
    
    pipeline = MultiAgentPipeline(
        enable_evaluation=False,  # Skip evaluation for news
        enable_formatting=False
    )
    
    query = "Latest AI investments"
    print(f"\nQuery: {query}")
    print(f"Configuration: No evaluation (faster), No formatting\n")
    
    result = pipeline.run(query)
    
    print(f"\nResults:")
    print(f"  Status: {result['status']}")
    print(f"  Agents executed: {' → '.join(result['agent_history'])}")
    print(f"  Agents SKIPPED: ", end="")
    
    all_agents = {'planner', 'search', 'scraper', 'evaluator', 'summarizer', 'formatter'}
    executed = set(result['agent_history'])
    skipped = all_agents - executed
    print(', '.join(skipped) if skipped else "None")


def example_academic():
    """Example 3: Academic query (requires evaluation)"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Academic Research Query")
    print("="*80)
    
    pipeline = MultiAgentPipeline(
        enable_evaluation=True,   # Strict content filtering
        enable_formatting=True    # Export in multiple formats
    )
    
    query = "Deep learning architectures for image recognition"
    print(f"\nQuery: {query}")
    print(f"Configuration: Evaluation ENABLED (strict), Formatting ENABLED\n")
    
    result = pipeline.run(query)
    
    print(f"\nResults:")
    print(f"  Status: {result['status']}")
    print(f"  Agents executed: {' → '.join(result['agent_history'])}")
    
    if result.get('evaluation_results'):
        eval_results = result['evaluation_results']
        print(f"\nContent Evaluation:")
        print(f"  Relevant items: {eval_results.get('relevant_count', 0)}")
        print(f"  Filtered out: {eval_results.get('filtered_count', 0)}")
        print(f"  Avg relevance: {eval_results.get('avg_relevance', 0):.2f}")
    
    if result.get('formatted_output'):
        formats = result['formatted_output'].get('formats', {})
        print(f"\nGenerated Formats: {', '.join(formats.keys())}")


def example_product_review():
    """Example 4: Product review query"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Product Review Query")
    print("="*80)
    
    pipeline = MultiAgentPipeline(
        enable_evaluation=True,   # Filter spam/bias
        enable_formatting=True    # Export as comparison table
    )
    
    query = "best electric cars under 40000 dollars"
    print(f"\nQuery: {query}")
    print(f"Configuration: Evaluation ENABLED, Formatting ENABLED\n")
    
    result = pipeline.run(query)
    
    print(f"\nResults:")
    print(f"  Status: {result['status']}")
    print(f"  Agents path: {' → '.join(result['agent_history'])}")


def example_routing_visualization():
    """Example 5: Visualize the routing graph"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Graph Visualization")
    print("="*80)
    
    print("\nSimplified Agent Flow:")
    print("="*60)
    
    viz = GraphVisualizer()
    graph_text = viz.draw_ascii_graph(simplified=True)
    print(graph_text)
    
    print("\n\nDetailed Agent Flow with Routing Decisions:")
    print("="*60)
    
    graph_text_full = viz.draw_ascii_graph(simplified=False)
    print(graph_text_full)


def example_decision_making():
    """Example 6: Show decision-making process"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Agent Decision-Making")
    print("="*80)
    
    pipeline = MultiAgentPipeline(enable_evaluation=True)
    
    # Different query types show different routing
    queries = [
        "quick update on AI news",           # Simple → skip evaluation
        "academic paper on quantum computing", # Academic → strict evaluation
        "reviews for coffee makers",         # Product → filter bias
    ]
    
    for query in queries:
        print(f"\nQuery Type: '{query}'")
        print("-" * 60)
        
        result = pipeline.run(query)
        
        print(f"Planner Decision:")
        if result.get('plan'):
            plan = result['plan']
            print(f"  • Query Type: {plan.get('query_type', 'unknown')}")
            print(f"  • Complexity: {plan.get('complexity', 'unknown')}")
            print(f"  • Needs Evaluation: {plan.get('needs_evaluation', False)}")
            print(f"  • Needs Formatting: {plan.get('needs_formatting', False)}")
        
        print(f"\nAgent Routing:")
        print(f"  Path: {' → '.join(result['agent_history'])}")
        
        if result.get('routing_decisions'):
            print(f"  Decisions: {', '.join(result['routing_decisions'])}")


def example_error_handling():
    """Example 7: Error handling and graceful degradation"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Error Handling")
    print("="*80)
    
    pipeline = MultiAgentPipeline()
    
    # Various edge cases
    cases = [
        ("Very obscure topic with no results", "Tests no-search handling"),
        ("@#$%^&*()", "Tests special characters"),
        ("a", "Tests very short query"),
    ]
    
    for query, description in cases:
        print(f"\nTest: {description}")
        print(f"Query: '{query}'")
        print("-" * 60)
        
        try:
            result = pipeline.run(query)
            print(f"Status: {result['status']}")
            
            if result['status'] in ['failed', 'partial_success']:
                print(f"Error: {result.get('error_message', 'Unknown error')}")
            
            print(f"Agents executed: {len(result['agent_history'])}")
            
        except Exception as e:
            print(f"Exception: {str(e)}")


def example_batch_processing():
    """Example 8: Batch processing multiple queries"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Batch Processing")
    print("="*80)
    
    pipeline = MultiAgentPipeline()
    
    queries = [
        "What is blockchain?",
        "Latest in renewable energy",
        "Best practices for cybersecurity",
        "AI trends in 2024",
    ]
    
    print(f"\nProcessing {len(queries)} queries...\n")
    
    results = []
    for i, query in enumerate(queries, 1):
        print(f"{i}. Processing: '{query}'")
        result = pipeline.run(query)
        results.append(result)
        print(f"   Status: {result['status']} | Agents: {len(result['agent_history'])}\n")
    
    # Summary statistics
    print("\nBatch Summary:")
    print("-" * 60)
    successful = sum(1 for r in results if r['status'] == 'success')
    partial = sum(1 for r in results if r['status'] == 'partial_success')
    failed = sum(1 for r in results if r['status'] == 'failed')
    
    print(f"Total queries: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Partial success: {partial}")
    print(f"Failed: {failed}")


def example_compare_configurations():
    """Example 9: Compare different pipeline configurations"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Configuration Comparison")
    print("="*80)
    
    query = "Machine learning applications in business"
    
    configs = [
        ("Minimal Pipeline", {"enable_evaluation": False, "enable_formatting": False}),
        ("Standard Pipeline", {"enable_evaluation": True, "enable_formatting": False}),
        ("Full Pipeline", {"enable_evaluation": True, "enable_formatting": True}),
    ]
    
    print(f"\nQuery: '{query}'\n")
    
    for config_name, config_params in configs:
        print(f"\n{config_name}:")
        print(f"  Config: {config_params}")
        print("-" * 60)
        
        pipeline = MultiAgentPipeline(**config_params)
        result = pipeline.run(query)
        
        print(f"  Status: {result['status']}")
        print(f"  Agents: {' → '.join(result['agent_history'])}")
        print(f"  Agents count: {len(result['agent_history'])}")
        
        has_formats = 'formatted_output' in result and result['formatted_output']
        print(f"  Formats generated: {'Yes' if has_formats else 'No'}")


def example_state_flow():
    """Example 10: Show state evolution during execution"""
    print("\n" + "="*80)
    print("EXAMPLE 10: State Evolution")
    print("="*80)
    
    print("\nAs agents execute, the shared state evolves:\n")
    
    print("START:")
    print("  state = {")
    print("    'query': 'What is AI?',")
    print("    'status': None")
    print("  }")
    
    print("\nAFTER PLANNER:")
    print("  state = {")
    print("    'query': 'What is AI?',")
    print("    'plan': {query_type: 'general', complexity: 'simple', ...},")
    print("    'status': 'running'")
    print("  }")
    
    print("\nAFTER SEARCH:")
    print("  state = {")
    print("    ...,")
    print("    'search_results': {results: [...]},")
    print("    'status': 'running'")
    print("  }")
    
    print("\nAFTER SCRAPER:")
    print("  state = {")
    print("    ...,")
    print("    'scraped_content': '...',")
    print("    'scraped_urls': [...]")
    print("  }")
    
    print("\nAFTER EVALUATOR:")
    print("  state = {")
    print("    ...,")
    print("    'evaluation_results': {relevant_count: 5, ...},")
    print("    'relevant_content': [...]")
    print("  }")
    
    print("\nAFTER SUMMARIZER:")
    print("  state = {")
    print("    ...,")
    print("    'summary': '...',")
    print("    'status': 'success'")
    print("  }")


def print_menu():
    """Print example menu"""
    print("\n" + "="*80)
    print("MULTI-AGENT PIPELINE - EXAMPLE USAGE")
    print("="*80)
    print("\nAvailable Examples:")
    print("  1. Basic query processing")
    print("  2. Fast news processing (simpler routing)")
    print("  3. Academic research query (strict evaluation)")
    print("  4. Product review query")
    print("  5. Graph visualization")
    print("  6. Decision-making process")
    print("  7. Error handling and graceful degradation")
    print("  8. Batch processing multiple queries")
    print("  9. Configuration comparison")
    print("  10. State evolution through agents")
    print("  0. Run all examples")
    print("\nUsage:")
    print("  python example_multi_agent.py [EXAMPLE_NUMBER]")
    print("  Example: python example_multi_agent.py 1")


def main():
    """Main entry point"""
    examples = {
        '1': ('Basic Query Processing', example_basic),
        '2': ('Fast News Processing', example_news),
        '3': ('Academic Research Query', example_academic),
        '4': ('Product Review Query', example_product_review),
        '5': ('Graph Visualization', example_routing_visualization),
        '6': ('Decision-Making Process', example_decision_making),
        '7': ('Error Handling', example_error_handling),
        '8': ('Batch Processing', example_batch_processing),
        '9': ('Configuration Comparison', example_compare_configurations),
        '10': ('State Evolution', example_state_flow),
    }
    
    print_menu()
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
    else:
        example_num = input("\nEnter example number (or 0 for all): ").strip()
    
    print("\n")
    
    if example_num == '0':
        # Run all examples
        for num, (name, func) in examples.items():
            try:
                func()
            except Exception as e:
                print(f"\n❌ Example {num} failed: {str(e)}")
    elif example_num in examples:
        # Run specific example
        name, func = examples[example_num]
        print(f"Running: {name}\n")
        func()
    else:
        print("❌ Invalid example number")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("✅ Examples completed!")
    print("="*80)


if __name__ == '__main__':
    main()
