#!/usr/bin/env python3
"""Test script to verify the routing fix is working."""

import sys
import os
import tempfile
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.routing_service import IntelligentRoutingService
from src.backend.orchestrator import BackendOrchestrator
from src.schemas.requests import NewChatRequest


def test_routing_only():
    """Test just the routing mechanism."""
    print("🧠 Testing Routing Mechanism")
    print("=" * 40)
    
    routing_service = IntelligentRoutingService()
    
    test_cases = [
        ("Hello", False, "CONVERSATION_AGENT"),
        ("What is the average salary?", True, "CSV_AGENT"),
        ("Show me all users", False, "SQL_AGENT"),
        ("Create a chart", True, "CSV_AGENT"),
        ("SELECT * FROM users", False, "SQL_AGENT"),
    ]
    
    for query, csv_loaded, expected in test_cases:
        print(f"\nQuery: '{query}' (CSV loaded: {csv_loaded})")
        decision = routing_service.determine_agent(query, [], csv_loaded=csv_loaded)
        print(f"Expected: {expected}")
        print(f"Actual: {decision.agent}")
        print(f"Confidence: {decision.confidence}")
        print(f"Reasoning: {decision.reasoning}")
        
        status = "✅ PASS" if decision.agent == expected else "❌ FAIL"
        print(f"Status: {status}")


def test_csv_analysis_with_real_data():
    """Test CSV analysis with actual CSV data."""
    print("\n📊 Testing CSV Analysis with Real Data")
    print("=" * 40)
    
    # Create a temporary CSV file
    data = {
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000, 60000, 70000, 55000, 65000],
        'department': ['IT', 'HR', 'IT', 'Finance', 'HR']
    }
    
    df = pd.DataFrame(data)
    
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        csv_path = f.name
    
    print(f"Created test CSV: {csv_path}")
    print("CSV Content:")
    print(df.to_string(index=False))
    
    # Create orchestrator and test CSV analysis
    orchestrator = BackendOrchestrator()
    
    # Create session
    session_info = orchestrator.create_new_session(
        NewChatRequest(session_name="Test Session")
    )
    session_id = session_info.session_id
    print(f"\nCreated session: {session_id}")
    
    # Load CSV data
    with open(csv_path, 'r') as f:
        csv_content = f.read()
    
    result = orchestrator.load_csv_data(session_id, csv_content)
    print(f"CSV Load Result: {result['status']}")
    
    # Test CSV analysis queries
    test_queries = [
        "What is the average salary?",
        "How many people are in each department?",
        "Who has the highest salary?",
    ]
    
    for query in test_queries:
        print(f"\n--- Testing Query: '{query}' ---")
        try:
            response = orchestrator.generate_intelligent_response(session_id, query)
            print(f"Response: {response.content}")
            print(f"Response Type: {type(response.content)}")
            
            # Check if this is raw Python code (the old problem)
            if "import" in response.content or "pd.read_csv" in response.content:
                print("❌ ISSUE: Response contains raw Python code!")
            else:
                print("✅ SUCCESS: Response is clean human-readable text!")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    # Cleanup
    os.unlink(csv_path)


def main():
    """Run all tests."""
    print("🚀 Testing Routing Fix")
    print("=" * 50)
    
    # Test 1: Routing mechanism
    test_routing_only()
    
    # Test 2: CSV analysis with real data
    test_csv_analysis_with_real_data()
    
    print("\n🎉 Testing completed!")


if __name__ == "__main__":
    main()
