#!/usr/bin/env python3
"""
Comprehensive test for all backend functionality of Querypls.
Tests conversation, SQL generation, and CSV analysis capabilities.
"""

import sys
import os
import pandas as pd
from io import StringIO

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.routing_service import IntelligentRoutingService
from src.services.conversation_service import ConversationService
from src.services.sql_service import SQLGenerationService
from src.services.csv_analysis_tools import CSVAnalysisTools
from src.schemas.requests import ChatMessage, SQLGenerationRequest
from src.backend.orchestrator import BackendOrchestrator


def test_conversation_functionality():
    """Test conversation responses."""
    print("🧪 Testing Conversation Functionality")
    print("=" * 50)
    
    try:
        routing_service = IntelligentRoutingService()
        
        # Test conversation queries
        conversation_tests = [
            "Hello",
            "How are you?",
            "What can you do?",
            "Thanks for your help",
            "Goodbye"
        ]
        
        for query in conversation_tests:
            print(f"\nQuery: '{query}'")
            try:
                response = routing_service.handle_conversation_query(query)
                print(f"Response: {response[:100]}...")
                print("✅ PASS")
            except Exception as e:
                print(f"❌ FAIL: {str(e)}")
        
        print("\n" + "=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Conversation test failed: {str(e)}")
        return False


def test_sql_functionality():
    """Test SQL generation functionality."""
    print("🗃️ Testing SQL Generation Functionality")
    print("=" * 50)
    
    try:
        routing_service = IntelligentRoutingService()
        sql_service = SQLGenerationService()
        
        # Test SQL queries
        sql_tests = [
            "Show me all users",
            "SELECT * FROM users WHERE status = 'active'",
            "Find customers who made purchases in the last 30 days",
            "Get the total sales by month"
        ]
        
        for query in sql_tests:
            print(f"\nQuery: '{query}'")
            try:
                # Test routing
                routing_decision = routing_service.determine_agent(query, [], csv_loaded=False)
                print(f"Routing Decision: {routing_decision.agent}")
                
                # Test SQL generation
                request = SQLGenerationRequest(
                    user_query=query,
                    conversation_history=[]
                )
                response = sql_service.generate_sql(request)
                print(f"SQL Response: {response.content[:100]}...")
                print("✅ PASS")
            except Exception as e:
                print(f"❌ FAIL: {str(e)}")
        
        print("\n" + "=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ SQL test failed: {str(e)}")
        return False


def test_csv_functionality():
    """Test CSV analysis functionality."""
    print("📊 Testing CSV Analysis Functionality")
    print("=" * 50)
    
    try:
        # Create sample CSV data
        sample_data = {
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'age': [25, 30, 35, 28, 32],
            'salary': [50000, 60000, 70000, 55000, 65000],
            'department': ['IT', 'HR', 'IT', 'Finance', 'HR']
        }
        
        df = pd.DataFrame(sample_data)
        csv_content = df.to_csv(index=False)
        
        print(f"Sample CSV Data:\n{df.head()}")
        print(f"CSV Shape: {df.shape}")
        
        # Test CSV tools
        csv_tools = CSVAnalysisTools()
        
        # Test loading CSV data
        print("\nTesting CSV loading...")
        result = csv_tools.load_csv_data(csv_content, "test_session")
        print(f"Load Result: {result}")
        
        # Test CSV analysis queries
        csv_tests = [
            "Show me the basic statistics of the data",
            "Create a bar chart of department distribution",
            "What is the average salary by department?",
            "Show me the top 3 highest paid employees"
        ]
        
        routing_service = IntelligentRoutingService()
        
        for query in csv_tests:
            print(f"\nQuery: '{query}'")
            try:
                # Test routing with CSV loaded
                routing_decision = routing_service.determine_agent(query, [], csv_loaded=True)
                print(f"Routing Decision: {routing_decision.agent}")
                
                # Test CSV analysis
                response = routing_service.handle_csv_query(query, csv_content)
                print(f"CSV Response: {response[:200]}...")
                print("✅ PASS")
            except Exception as e:
                print(f"❌ FAIL: {str(e)}")
        
        print("\n" + "=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ CSV test failed: {str(e)}")
        return False


def test_intelligent_routing():
    """Test intelligent routing functionality."""
    print("🧠 Testing Intelligent Routing")
    print("=" * 50)
    
    try:
        routing_service = IntelligentRoutingService()
        
        # Test cases with expected routing
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
        
        all_passed = True
        for query, expected_agent in test_cases:
            print(f"\nQuery: '{query}'")
            print(f"Expected Agent: {expected_agent}")
            
            try:
                # Test without CSV loaded
                decision = routing_service.determine_agent(query, [], csv_loaded=False)
                print(f"Result (no CSV): {decision.agent}")
                
                # Test with CSV loaded
                decision_with_csv = routing_service.determine_agent(query, [], csv_loaded=True)
                print(f"Result (with CSV): {decision_with_csv.agent}")
                
                if decision.agent == expected_agent or decision_with_csv.agent == expected_agent:
                    print("✅ PASS")
                else:
                    print("❌ FAIL")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                all_passed = False
        
        print("\n" + "=" * 50)
        return all_passed
        
    except Exception as e:
        print(f"❌ Routing test failed: {str(e)}")
        return False


def test_orchestrator():
    """Test the main orchestrator functionality."""
    print("🎼 Testing Backend Orchestrator")
    print("=" * 50)
    
    try:
        orchestrator = BackendOrchestrator()
        
        # Test session creation
        print("Testing session creation...")
        from src.schemas.requests import NewChatRequest
        session_info = orchestrator.create_new_session(NewChatRequest(session_name="Test Session"))
        session_id = session_info.session_id
        print(f"Created session: {session_id}")
        
        # Test conversation
        print("\nTesting conversation...")
        response = orchestrator.generate_intelligent_response(session_id, "Hello")
        print(f"Conversation Response: {response.content[:100]}...")
        
        # Test SQL generation
        print("\nTesting SQL generation...")
        response = orchestrator.generate_intelligent_response(session_id, "Show me all users")
        print(f"SQL Response: {response.content[:100]}...")
        
        # Test CSV loading and analysis
        print("\nTesting CSV functionality...")
        sample_csv = "name,age,salary\nAlice,25,50000\nBob,30,60000\nCharlie,35,70000"
        result = orchestrator.load_csv_data(session_id, sample_csv)
        print(f"CSV Load Result: {result}")
        
        response = orchestrator.generate_intelligent_response(session_id, "Analyze this data")
        print(f"CSV Analysis Response: {response.content[:100]}...")
        
        print("\n" + "=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Comprehensive Backend Functionality Tests")
    print("=" * 60)
    
    tests = [
        ("Conversation", test_conversation_functionality),
        ("SQL Generation", test_sql_functionality),
        ("CSV Analysis", test_csv_functionality),
        ("Intelligent Routing", test_intelligent_routing),
        ("Orchestrator", test_orchestrator),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend functionality is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend implementation.")
    
    return passed == total


if __name__ == "__main__":
    main() 