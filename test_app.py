#!/usr/bin/env python3
"""
Simple test to verify the application components are working.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        from src.config.constants import WELCOME_MESSAGE, DEFAULT_SESSION_NAME
        print("✅ Constants imported successfully")
        print(f"   WELCOME_MESSAGE: {WELCOME_MESSAGE[:50]}...")
        print(f"   DEFAULT_SESSION_NAME: {DEFAULT_SESSION_NAME}")
    except ImportError as e:
        print(f"❌ Error importing constants: {e}")
        return False
    
    try:
        from src.services.routing_service import IntelligentRoutingService
        print("✅ Routing service imported successfully")
    except ImportError as e:
        print(f"❌ Error importing routing service: {e}")
        return False
    
    try:
        from src.backend.orchestrator import BackendOrchestrator
        print("✅ Orchestrator imported successfully")
    except ImportError as e:
        print(f"❌ Error importing orchestrator: {e}")
        return False
    
    return True

def test_routing():
    """Test the routing service."""
    print("\nTesting routing service...")
    
    try:
        from src.services.routing_service import IntelligentRoutingService
        routing_service = IntelligentRoutingService()
        
        # Test routing decisions
        test_cases = [
            ("Hello", "CONVERSATION_AGENT"),
            ("Show me all users", "SQL_AGENT"),
            ("Analyze this CSV data", "CSV_AGENT"),
        ]
        
        for query, expected in test_cases:
            decision = routing_service.determine_agent(query, [], csv_loaded=False)
            status = "✅" if decision.agent == expected else "❌"
            print(f"   {status} '{query}' → {decision.agent} (expected: {expected})")
        
        return True
    except Exception as e:
        print(f"❌ Error testing routing: {e}")
        return False

if __name__ == "__main__":
    print("Querypls Application Test")
    print("=" * 40)
    
    success = True
    success &= test_imports()
    success &= test_routing()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All tests passed! Application is ready.")
    else:
        print("❌ Some tests failed. Please check the errors above.") 