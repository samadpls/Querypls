#!/usr/bin/env python3
"""
Simple test script to verify the routing logic works correctly.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.routing_service import IntelligentRoutingService
from src.schemas.requests import ChatMessage


def test_routing():
    """Test the routing service with different types of queries."""
    routing_service = IntelligentRoutingService()

    # Test cases
    test_cases = [
        ("Hello", "CONVERSATION_AGENT"),
        ("How are you?", "CONVERSATION_AGENT"),
        ("Show me all users", "SQL_AGENT"),
        ("SELECT * FROM users", "SQL_AGENT"),
        ("Analyze this CSV data", "CSV_AGENT"),
        ("Create a chart from the data", "CSV_AGENT"),
        ("What can you do?", "CONVERSATION_AGENT"),
        ("Thanks for your help", "CONVERSATION_AGENT"),
    ]

    print("Testing Intelligent Routing Service...")
    print("=" * 50)

    for query, expected_agent in test_cases:
        print(f"\nQuery: '{query}'")
        print(f"Expected Agent: {expected_agent}")

        try:
            decision = routing_service.determine_agent(query, [], csv_loaded=False)
            print(f"Actual Agent: {decision.agent}")
            print(f"Confidence: {decision.confidence}")
            print(f"Reasoning: {decision.reasoning}")

            if decision.agent == expected_agent:
                print("✅ PASS")
            else:
                print("❌ FAIL")

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

    print("\n" + "=" * 50)
    print("Testing conversation responses...")

    conversation_tests = [
        "Hello",
        "How are you?",
        "What can you do?",
        "Thanks",
        "Goodbye",
    ]

    for query in conversation_tests:
        print(f"\nQuery: '{query}'")
        try:
            response = routing_service.handle_conversation_query(query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")


if __name__ == "__main__":
    test_routing()
