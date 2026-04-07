"""
Graph visualization and analysis utilities.
Generates ASCII and HTML representations of the multi-agent graph.
"""

from typing import List, Dict
from utils.logging_config import get_logger

logger = get_logger(__name__)


class GraphVisualizer:
    """Generates visualizations of the multi-agent workflow."""
    
    @staticmethod
    def draw_ascii_graph(simplified: bool = False) -> str:
        """
        Draw ASCII representation of the graph.
        
        Args:
            simplified: If True, show minimal graph
            
        Returns:
            ASCII art representation
        """
        if simplified:
            graph = """
╔════════════════════════════════════════════════════════════════╗
║           SIMPLIFIED MULTI-AGENT PIPELINE                     ║
╚════════════════════════════════════════════════════════════════╝

                              START
                                │
                                ▼
                        ┌─────────────────┐
                        │   PLANNER       │  (Analyze & Plan)
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   SEARCH       │  (Find URLs)
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   SCRAPER      │  (Extract Content)
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   EVALUATOR    │  (Filter & Rank)
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   SUMMARIZER   │  (Generate Summary)
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   FORMATTER    │  (Multiple Formats)
                        └────────┬────────┘
                                 │
                                 ▼
                                END
"""
        else:
            graph = """
╔════════════════════════════════════════════════════════════════╗
║         FULL MULTI-AGENT EXECUTION GRAPH                       ║
╚════════════════════════════════════════════════════════════════╝

                              START
                                │
                    ┌───────────▼───────────┐
                    │                       │
                    ▼                       ▼
            ┌──────────────┐       ┌──────────────┐
            │   PLANNER    │◄──────┤ ROUTE AFTER  │
            │   DECISION   │       │    PLAN      │
            └──────┬───────┘       └──────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
    ┌─────────┐         ┌──────────┐
    │ SEARCH  │◄────────┤ DECISION │
    │ AGENTS  │         │  AFTER   │
    └────┬────┘         │ SEARCH   │
         │              └──────────┘
         │
    ┌────▼─────┐
    │  SCRAPER │  (URL Processing)
    └────┬─────┘
         │
    ┌────▼──────────────┐
    │                   │
    ▼                   ▼
┌─────────────┐    ┌──────────┐
│ EVALUATOR   │◄───┤ DECISION │
│    YES/NO   │    │  EVAL    │
└──────┬──────┘    └──────────┘
       │
       ├──► SKIP ──┐
       │           │
       ▼           │
    ┌──────────┐   │
    │SUMMARIZER│   │
    └────┬─────┘   │
         │         │
         ▼         ▼
    ┌──────────────┐
    │  FORMATTER   │
    │ (CSV/JSON)   │
    └──────┬───────┘
           │
           ▼
    ┌────────────┐
    │ ERROR HDL  │
    │(Graceful)  │
    └──────┬─────┘
           │
           ▼
         END
"""
        
        return graph
    
    @staticmethod
    def draw_mermaid_diagram() -> str:
        """
        Generate Mermaid diagram code for visualization.
        Can be pasted into mermaid.live
        
        Returns:
            Mermaid diagram code
        """
        diagram = """graph TD
    START([START]) --> PLANNER[Planner Agent<br/>Analyze Query]
    
    PLANNER --> ROUTE{Route Decision}
    
    ROUTE -->|Search Enabled| SEARCH[Search Agent<br/>Find URLs]
    ROUTE -->|Skip| SKIP1[Skip to End]
    
    SEARCH --> SEARCH_DECISION{URLs Found?}
    SEARCH_DECISION -->|Yes| SCRAPER[Scraper Agent<br/>Extract Content]
    SEARCH_DECISION -->|No| SKIP2[No Results]
    
    SCRAPER --> EVAL_CHECK{Evaluate?}
    
    EVAL_CHECK -->|Yes| EVALUATOR[Evaluator Agent<br/>Filter & Rank]
    EVAL_CHECK -->|No| SUMMARIZER[Summarizer Agent<br/>Generate Summary]
    
    EVALUATOR --> EVAL_RESULT{Content Relevant?}
    EVAL_RESULT -->|Yes| SUMMARIZER
    EVAL_RESULT -->|No| SKIP3[Content Filtered]
    
    SUMMARIZER --> FORMAT_CHECK{Format Output?}
    
    FORMAT_CHECK -->|Yes| FORMATTER[Formatter Agent<br/>CSV/JSON/Audio]
    FORMAT_CHECK -->|No| END1([END])
    
    FORMATTER --> END([SUCCESS])
    
    SKIP1 --> ERROR_HDL[Error Handler<br/>Graceful Degradation]
    SKIP2 --> ERROR_HDL
    SKIP3 --> ERROR_HDL
    ERROR_HDL --> END
    
    style PLANNER fill:#4CAF50,stroke:#2E7D32,color:#fff
    style SEARCH fill:#2196F3,stroke:#1565C0,color:#fff
    style SCRAPER fill:#FF9800,stroke:#E65100,color:#fff
    style EVALUATOR fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style SUMMARIZER fill:#F44336,stroke:#C62828,color:#fff
    style FORMATTER fill:#00BCD4,stroke:#00838F,color:#fff
    style ERROR_HDL fill:#757575,stroke:#424242,color:#fff
    style END fill:#4CAF50,stroke:#2E7D32,color:#fff
    style START fill:#8BC34A,stroke:#558B2F,color:#fff
"""
        return diagram
    
    @staticmethod
    def draw_json_graph() -> Dict:
        """
        Generate JSON representation of graph structure.
        
        Returns:
            Dictionary with graph structure
        """
        return {
            "name": "MultiAgentPipeline",
            "entry_point": "planner",
            "nodes": [
                {"id": "planner", "type": "agent", "name": "Planner", "description": "Analyze query and create plan"},
                {"id": "search", "type": "agent", "name": "Search", "description": "Find relevant URLs"},
                {"id": "scraper", "type": "agent", "name": "Scraper", "description": "Extract clean content"},
                {"id": "evaluator", "type": "agent", "name": "Evaluator", "description": "Filter by relevance"},
                {"id": "summarizer", "type": "agent", "name": "Summarizer", "description": "Generate summary"},
                {"id": "formatter", "type": "agent", "name": "Formatter", "description": "Format output"},
                {"id": "error_handler", "type": "router", "name": "Error Handler", "description": "Graceful failure handling"},
            ],
            "edges": [
                {"from": "planner", "to": "search", "condition": None},
                {"from": "search", "to": "scraper", "condition": "urls_found"},
                {"from": "scraper", "to": "evaluator", "condition": "content_exists"},
                {"from": "evaluator", "to": "summarizer", "condition": "content_relevant"},
                {"from": "summarizer", "to": "formatter", "condition": "summary_exists"},
                {"from": "formatter", "to": "END", "condition": None},
            ],
            "conditional_edges": [
                {"from": "search", "to": ["scraper", "error_handler"], "condition": "urls_found"},
                {"from": "evaluator", "to": ["summarizer", "error_handler"], "condition": "is_relevant"},
            ]
        }
    
    @staticmethod
    def print_execution_trace(agent_history: List[str], routing_decisions: List[str]) -> str:
        """
        Print execution trace from a completed run.
        
        Args:
            agent_history: List of agents executed
            routing_decisions: List of routing decisions made
            
        Returns:
            Formatted trace string
        """
        trace = "\n╔════════════════════════════════════════════════════════════════╗"
        trace += "\n║           EXECUTION TRACE                                     ║"
        trace += "\n╚════════════════════════════════════════════════════════════════╝\n"
        
        trace += "Agent Execution Path:\n"
        for i, agent in enumerate(agent_history, 1):
            prefix = "└──>" if i == len(agent_history) else "├──>"
            trace += f"{prefix} {i}. {agent.upper()}\n"
        
        trace += "\nRouting Decisions:\n"
        for i, decision in enumerate(routing_decisions, 1):
            trace += f"└──> {i}. {decision.upper()}\n"
        
        trace += "\n"
        return trace
    
    @staticmethod
    def generate_html_visualization() -> str:
        """
        Generate HTML file for visualization (requires graphviz).
        
        Returns:
            HTML code for embedding
        """
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Agent Pipeline Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .mermaid {
            display: flex;
            justify-content: center;
            background: white;
            padding: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .legend {
            margin-top: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-left: 4px solid #2196F3;
        }
        .legend-item {
            margin: 10px 0;
        }
        .legend-color {
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Multi-Agent Pipeline Visualization</h1>
        
        <div class="mermaid">
            graph TD
                START([START]) --> PLANNER[🎯 Planner]
                PLANNER --> SEARCH[🔍 Search]
                SEARCH --> SCRAPER[🪄 Scraper]
                SCRAPER --> EVALUATOR[⭐ Evaluator]
                EVALUATOR --> SUMMARIZER[📝 Summarizer]
                SUMMARIZER --> FORMATTER[💾 Formatter]
                FORMATTER --> END([SUCCESS])
        </div>
        
        <div class="legend">
            <h3>Agent Types</h3>
            <div class="legend-item">
                <span class="legend-color" style="background: #4CAF50;"></span>
                <strong>Planner:</strong> Analyzes query and creates execution plan
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #2196F3;"></span>
                <strong>Search:</strong> Fetches URLs from Serper API
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #FF9800;"></span>
                <strong>Scraper:</strong> Extracts and cleans content from URLs
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #9C27B0;"></span>
                <strong>Evaluator:</strong> Filters content by relevance
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #F44336;"></span>
                <strong>Summarizer:</strong> Generates bullet-point summary
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #00BCD4;"></span>
                <strong>Formatter:</strong> Converts to CSV, JSON, Markdown
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
