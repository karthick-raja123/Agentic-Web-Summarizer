"""
Test Queries for Benchmarking
=============================

Diverse set of test queries covering different categories and complexity levels.
"""

TEST_QUERIES = [
    # 1. Technical Documentation
    {
        "query": """
        FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.6+ 
        based on standard Python type hints. The key features are:
        - Fast: Very high performance, on par with NodeJS and Go
        - Fast to code: Increase the speed to develop features by about 200% to 300%
        - Fewer bugs: About 40% fewer human (developer) induced errors
        - Intuitive: Great editor support
        - Easy: Designed to be easy to use and learn
        - Standards-based: Based on (and fully compatible with) the open standards for APIs: OpenAPI and JSON Schema
        
        FastAPI features automatic interactive API documentation via Swagger UI and ReDoc. 
        The framework automatically generates the OpenAPI schema from your code.
        """,
        "category": "technical",
        "description": "Technical framework documentation"
    },
    
    # 2. News Article
    {
        "query": """
        Artificial Intelligence research has advanced dramatically in recent years. Large language models 
        like GPT-4 and Claude have demonstrated capabilities that were previously thought impossible. 
        These models can now perform complex reasoning tasks, write code, answer questions across virtually 
        any domain, and even engage in creative writing. The implications for the future of work, education, 
        and society are profound. Companies are racing to integrate AI into their products and services. 
        Governments are beginning to develop regulatory frameworks to ensure AI is developed and deployed 
        responsibly. At the same time, concerns about job displacement, bias, and misuse of AI technology 
        remain important considerations as the field continues to evolve.
        """,
        "category": "news",
        "description": "News article about AI advances"
    },
    
    # 3. Short Snippet
    {
        "query": "Python is a high-level programming language known for its simplicity and readability.",
        "category": "snippet",
        "description": "Short technical snippet"
    },
    
    # 4. Scientific Paper Abstract
    {
        "query": """
        Abstract: We present a novel approach to transformer optimization that reduces inference latency 
        by 40% while maintaining accuracy. Our method combines quantization with attention pattern pruning 
        and knowledge distillation. We evaluate on BERT, RoBERTa, and GPT-2 models across 8 downstream tasks. 
        Results show consistent improvements with minimal accuracy loss. This approach is particularly effective 
        for mobile and edge deployment scenarios where computational resources are limited. Our implementation 
        is available as an open-source library compatible with HuggingFace transformers. We discuss implications 
        for deployment of large language models and provide detailed performance benchmarks.
        """,
        "category": "scientific",
        "description": "Scientific paper abstract"
    },
    
    # 5. Business Report
    {
        "query": """
        Q3 Performance Report: Our company achieved record revenue of $2.3B, representing a 15% year-over-year 
        growth. Operating margin improved to 22% from 19% in Q2, driven by operational efficiencies and cost 
        optimization initiatives. Customer acquisition cost decreased by 18% due to improved marketing targeting. 
        Gross margin expanded to 68% from 65%. Market share increased in all three key segments. Cloud services 
        division showed the strongest growth at 35% YoY. However, challenges include increased competition from 
        new market entrants and supply chain disruptions affecting hardware components. We expect Q4 to be equally 
        strong with anticipated revenue between $2.1-2.5B.
        """,
        "category": "business",
        "description": "Quarterly business report"
    },
    
    # 6. Legal Document
    {
        "query": """
        Terms of Service - Updated January 2024: By accessing this website and using our services, you agree to 
        be bound by these Terms of Service. You may not use our services for any illegal purposes or in violation 
        of any applicable laws. We reserve the right to terminate or suspend access to our services at any time, 
        with or without cause, and with or without notice. Our liability is limited to the amount paid in the last 
        12 months. User-generated content remains the property of the user, but you grant us a non-exclusive, 
        royalty-free license to use, distribute, and display such content. We are not responsible for third-party 
        content or links. These terms are governed by the laws of the jurisdiction where we are incorporated.
        """,
        "category": "legal",
        "description": "Legal terms of service"
    },
    
    # 7. Product Description
    {
        "query": """
        ProductX Pro - The ultimate productivity suite for modern teams. Features include real-time collaboration,
        AI-powered scheduling, integrated communication, and advanced analytics. Supports 100+ integrations with 
        popular business tools. Available on web, desktop (Windows/Mac/Linux), and mobile (iOS/Android). Enterprise 
        plans include SSO, advanced permissions, audit logs, and dedicated support. Pricing starts at $10/user/month. 
        On average, teams report 30% improvement in productivity and 25% reduction in communication overhead. 
        Used by over 50,000 companies worldwide across 120+ countries.
        """,
        "category": "product",
        "description": "Product description and features"
    },
    
    # 8. Research Findings
    {
        "query": """
        Our research team conducted a study with 5,000 participants over 12 months to evaluate the effectiveness 
        of the new training program. Key findings include: 78% of participants showed significant improvement in 
        performance metrics within 3 months. Retention rate improved from 85% to 92%. Employee satisfaction scores 
        increased by 34% on average. Training completion rate was 96%, indicating high engagement. Return on investment 
        was calculated at 2.8x within the first year. Participants cited improved confidence, better skill development, 
        and increased career growth opportunities as primary benefits. These results suggest the program is highly 
        effective and could be expanded to additional departments.
        """,
        "category": "research",
        "description": "Research study findings"
    },
    
    # 9. Tutorial Content
    {
        "query": """
        Getting Started with Docker: Docker is a containerization platform that simplifies application deployment. 
        First, install Docker from the official website. Then, create a Dockerfile in your project directory that 
        specifies the base image, copies your application code, installs dependencies, and sets the startup command. 
        Build the image using 'docker build -t myapp:1.0 .'. Test it locally with 'docker run -p 8080:8080 myapp:1.0'. 
        Push to Docker Hub using 'docker push username/myapp:1.0'. For production, use Docker Compose to orchestrate 
        multiple containers or Kubernetes for larger deployments. Best practices include using official base images, 
        minimizing layer sizes, and implementing health checks.
        """,
        "category": "tutorial",
        "description": "Tutorial walkthrough"
    },
    
    # 10. Customer Feedback
    {
        "query": """
        Customer Review Summary: Out of 1,000 reviews, average rating is 4.6/5 stars. Positive feedback highlights 
        include excellent customer service (mentioned in 78% of positive reviews), intuitive user interface (72%), 
        and reliable performance (81%). Common suggestions for improvement include more customization options (15% of 
        reviews), faster implementation time (12%), and better documentation (8%). Negative reviews (8% of total) 
        primarily cite occasional technical issues (50% of negative reviews) and pricing concerns (35%). Overall, 
        customers express high satisfaction and would recommend the product to others (87% likelihood).
        """,
        "category": "feedback",
        "description": "Customer review summary"
    },
    
    # 11. Competitive Analysis
    {
        "query": """
        Market Analysis - Competitor Comparison: Our product offers superior performance compared to alternatives. 
        Speed: 3-5x faster than competitor A, on par with competitor B. Price: 40% more affordable than competitor B, 
        15% cheaper than competitor C. Features: We have 25 more features than competitor A, 10 more than competitor B. 
        Support: Available 24/7 (vs 12 hours for competitors). Scalability: Supports up to 1M concurrent users (vs 100K 
        for competitor A). Data shows our market share has increased from 8% to 15% in the last year. Customer satisfaction 
        scores are highest in the industry at 4.6/5.
        """,
        "category": "analysis",
        "description": "Competitive market analysis"
    },
    
    # 12. Medical Information
    {
        "query": """
        Health Benefits of Regular Exercise: Research shows that regular physical activity provides numerous health benefits. 
        Cardiovascular health: Reduces risk of heart disease by up to 35%. Weight management: Helps maintain healthy body weight 
        through calorie burn and metabolism increase. Mental health: Reduces symptoms of depression and anxiety by 30% on average. 
        Bone strength: Increases bone density, reducing osteoporosis risk. Cognitive function: Improves memory and reduces risk 
        of cognitive decline in elderly. Recommended: 150 minutes of moderate aerobic activity or 75 minutes of vigorous activity 
        per week. Types of exercise include walking, running, swimming, cycling, and strength training. Consult healthcare provider 
        before starting new exercise program, especially if you have pre-existing conditions.
        """,
        "category": "medical",
        "description": "Medical and health information"
    }
]

# Additional metadata
QUERY_METADATA = {
    "categories": ["technical", "news", "snippet", "scientific", "business", "legal", 
                  "product", "research", "tutorial", "feedback", "analysis", "medical"],
    "complexity_levels": {
        "snippet": "simple",
        "technical": "medium", 
        "news": "medium",
        "scientific": "complex",
        "business": "complex",
        "legal": "complex",
        "product": "medium",
        "research": "complex",
        "tutorial": "medium",
        "feedback": "simple",
        "analysis": "complex",
        "medical": "medium"
    },
    "expected_lengths": {
        "snippet": "short",
        "product": "medium",
        "technical": "medium",
        "news": "long",
        "scientific": "long",
        "business": "long",
        "legal": "long",
        "research": "long",
        "tutorial": "long",
        "feedback": "medium",
        "analysis": "long",
        "medical": "long"
    }
}

def get_queries_by_category(category: str):
    """Get queries for specific category."""
    return [q for q in TEST_QUERIES if q.get("category") == category]

def get_all_queries():
    """Get all test queries."""
    return TEST_QUERIES

def get_query_stats():
    """Get statistics about test queries."""
    stats = {
        "total_queries": len(TEST_QUERIES),
        "by_category": {},
        "avg_length": 0,
        "total_chars": 0
    }
    
    for query in TEST_QUERIES:
        cat = query.get("category", "unknown")
        if cat not in stats["by_category"]:
            stats["by_category"][cat] = 0
        stats["by_category"][cat] += 1
        stats["total_chars"] += len(query["query"])
    
    stats["avg_length"] = stats["total_chars"] // len(TEST_QUERIES)
    
    return stats
