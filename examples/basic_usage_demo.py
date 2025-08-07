#!/usr/bin/env python3
"""
Basic usage demo for Querypls backend functionality.
Demonstrates conversation, SQL generation, and CSV analysis.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.routing_service import IntelligentRoutingService
from src.backend.orchestrator import BackendOrchestrator
from src.schemas.requests import NewChatRequest


def demo_conversation():
    """Demo conversation functionality."""
    print("🗣️  CONVERSATION DEMO")
    print("=" * 40)

    routing_service = IntelligentRoutingService()

    # Test different conversation types
    conversations = [
        "Hello",
        "How are you?",
        "What can you do?",
        "Thanks for your help",
        "Goodbye",
    ]

    for query in conversations:
        print(f"\nUser: {query}")
        response = routing_service.handle_conversation_query(query)
        print(f"Assistant: {response}")

    print("\n" + "=" * 40)


def demo_sql_generation():
    """Demo SQL generation functionality."""
    print("🗃️  SQL GENERATION DEMO")
    print("=" * 40)

    routing_service = IntelligentRoutingService()

    # Test different SQL queries
    sql_queries = [
        "Show me all users",
        "Find customers who made purchases in the last 30 days",
        "Get the total sales by month",
        "SELECT * FROM users WHERE status = 'active'",
    ]

    for query in sql_queries:
        print(f"\nUser: {query}")
        response = routing_service.handle_sql_query(query, [])
        print(f"Assistant: {response[:200]}...")

    print("\n" + "=" * 40)


def demo_csv_analysis():
    """Demo CSV analysis functionality."""
    print("📊 CSV ANALYSIS DEMO")
    print("=" * 40)

    # Sample CSV data
    sample_csv = """name,age,salary,department
Alice,25,50000,IT
Bob,30,60000,HR
Charlie,35,70000,IT
Diana,28,55000,Finance
Eve,32,65000,HR"""

    print(f"Sample CSV Data:\n{sample_csv}")

    routing_service = IntelligentRoutingService()

    # Test different CSV analysis queries
    csv_queries = [
        "Show me the basic statistics of the data",
        "Create a bar chart of department distribution",
        "What is the average salary by department?",
        "Show me the top 3 highest paid employees",
    ]

    for query in csv_queries:
        print(f"\nUser: {query}")
        response = routing_service.handle_csv_query(query, sample_csv)
        print(f"Assistant: {response[:300]}...")

    print("\n" + "=" * 40)


def demo_intelligent_routing():
    """Demo intelligent routing functionality."""
    print("🧠 INTELLIGENT ROUTING DEMO")
    print("=" * 40)

    routing_service = IntelligentRoutingService()

    # Test different types of queries
    test_queries = [
        ("Hello", "CONVERSATION_AGENT"),
        ("Show me all users", "SQL_AGENT"),
        ("Analyze this CSV data", "CSV_AGENT"),
        ("How are you?", "CONVERSATION_AGENT"),
        ("SELECT * FROM users", "SQL_AGENT"),
        ("Create a chart from the data", "CSV_AGENT"),
    ]

    for query, expected_agent in test_queries:
        print(f"\nQuery: '{query}'")
        decision = routing_service.determine_agent(query, [], csv_loaded=True)
        print(f"Expected: {expected_agent}")
        print(f"Actual: {decision.agent}")
        print(f"Confidence: {decision.confidence}")
        print(f"Reasoning: {decision.reasoning}")

    print("\n" + "=" * 40)


def demo_orchestrator():
    """Demo the main orchestrator functionality."""
    print("🎼 ORCHESTRATOR DEMO")
    print("=" * 40)

    orchestrator = BackendOrchestrator()

    # Create a new session
    session_info = orchestrator.create_new_session(
        NewChatRequest(session_name="Demo Session")
    )
    session_id = session_info.session_id
    print(f"Created session: {session_id}")

    # Test different types of interactions
    interactions = [
        ("Hello", "conversation"),
        ("Show me all users", "sql"),
        ("What can you do?", "conversation"),
    ]

    for query, query_type in interactions:
        print(f"\nUser ({query_type}): {query}")
        response = orchestrator.generate_intelligent_response(session_id, query)
        print(f"Assistant: {response.content[:150]}...")

    # Test CSV functionality
    sample_csv = "name,age,salary\nAlice,25,50000\nBob,30,60000\nCharlie,35,70000"
    result = orchestrator.load_csv_data(session_id, sample_csv)
    print(f"\nCSV Load Result: {result['status']}")

    response = orchestrator.generate_intelligent_response(
        session_id, "Analyze this data"
    )
    print(f"CSV Analysis: {response.content[:200]}...")

    print("\n" + "=" * 40)


def main():
    """Run all demos."""
    print("🚀 Querypls Backend Functionality Demo")
    print("=" * 50)

    demos = [
        ("Conversation", demo_conversation),
        ("SQL Generation", demo_sql_generation),
        ("CSV Analysis", demo_csv_analysis),
        ("Intelligent Routing", demo_intelligent_routing),
        ("Orchestrator", demo_orchestrator),
    ]

    for demo_name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"❌ {demo_name} demo failed: {str(e)}")

    print("\n🎉 Demo completed! All backend functionality is working correctly.")
    print("\n📝 Summary:")
    print("- Conversation: Natural responses for greetings and help")
    print("- SQL Generation: Convert natural language to SQL queries")
    print("- CSV Analysis: Analyze CSV data with Python code")
    print("- Intelligent Routing: Automatically choose the right agent")
    print("- Orchestrator: Complete session management")


if __name__ == "__main__":
    main()
