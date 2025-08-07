"""
Command-line interface for Querypls SQL generation.
"""

import sys
import os
import json
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.orchestrator import BackendOrchestrator
from schemas.requests import NewChatRequest
from config.constants import (
    CLI_WELCOME, CLI_COMMANDS, CLI_GOODBYE, CLI_UNKNOWN_COMMAND, CLI_ERROR,
    SESSION_CREATED, SESSION_SWITCHED, SESSION_NOT_FOUND, NO_ACTIVE_SESSION,
    NO_SESSION, RESPONSE_GENERATED, SQL_DETAILS, QUERY_TYPE, COMPLEXITY,
    TABLES_USED, COLUMNS, ESTIMATED_ROWS, WARNINGS, CONVERSATION_HISTORY,
    HEALTH_CHECK_FAILED, NO_SESSIONS, AVAILABLE_SESSIONS, SESSION_INFO,
    SESSION_ID, SESSION_MESSAGES, SESSION_ACTIVITY, HEALTH_CHECK_SUCCESS,
    HEALTH_STATUS, HEALTH_VERSION, HEALTH_SERVICES, DEFAULT_SESSION_NAME
)


class QueryplsCLI:
    def __init__(self):
        self.orchestrator = BackendOrchestrator()
        self.current_session_id = None
    
    def create_session(self, name: Optional[str] = None) -> str:
        request = NewChatRequest(session_name=name)
        session_info = self.orchestrator.create_new_session(request)
        self.current_session_id = session_info.session_id
        print(SESSION_CREATED.format(name=session_info.session_name, id=session_info.session_id))
        return session_info.session_id
    
    def list_sessions(self):
        sessions = self.orchestrator.list_sessions()
        if not sessions:
            print(NO_SESSIONS)
            return
        
        print(AVAILABLE_SESSIONS)
        for i, session in enumerate(sessions, 1):
            print(SESSION_INFO.format(num=i, name=session.session_name))
            print(SESSION_ID.format(id=session.session_id))
            print(SESSION_MESSAGES.format(count=session.message_count))
            print(SESSION_ACTIVITY.format(activity=session.last_activity))
            print()
    
    def switch_session(self, session_id: str):
        session = self.orchestrator.get_session(session_id)
        if not session:
            print(SESSION_NOT_FOUND.format(id=session_id))
            return
        
        self.current_session_id = session_id
        print(SESSION_SWITCHED.format(name=session.session_name))
    
    def chat(self, query: str):
        if not self.current_session_id:
            print(NO_ACTIVE_SESSION)
            return
        
        try:
            response = self.orchestrator.generate_sql_response(self.current_session_id, query)
            print(f"\n{RESPONSE_GENERATED}")
            print(response.content)
            
            if response.sql_response:
                print(f"\n{SQL_DETAILS}")
                print(f"  {QUERY_TYPE}: {response.sql_response.query_type}")
                print(f"  {COMPLEXITY}: {response.sql_response.complexity}")
                print(f"  {TABLES_USED}: {', '.join(response.sql_response.tables_used)}")
                print(f"  {COLUMNS}: {', '.join(response.sql_response.columns_selected)}")
                print(f"  {ESTIMATED_ROWS}: {response.sql_response.estimated_rows}")
                if response.sql_response.warnings:
                    print(f"  {WARNINGS}: {', '.join(response.sql_response.warnings)}")
        
        except Exception as e:
            print(CLI_ERROR.format(error=str(e)))
    
    def show_history(self):
        if not self.current_session_id:
            print(NO_SESSION)
            return
        
        try:
            conversation = self.orchestrator.get_conversation_history(self.current_session_id)
            print(f"\n{CONVERSATION_HISTORY}")
            for message in conversation.messages:
                print(f"  {message.role.upper()}: {message.content}")
        except Exception as e:
            print(CLI_ERROR.format(error=str(e)))
    
    def health_check(self):
        try:
            health = self.orchestrator.health_check()
            print(f"{HEALTH_CHECK_SUCCESS}")
            print(f"  {HEALTH_STATUS.format(status=health.status)}")
            print(f"  {HEALTH_VERSION.format(version=health.version)}")
            print(f"  {HEALTH_SERVICES.format(services=json.dumps(health.services, indent=2))}")
        except Exception as e:
            print(HEALTH_CHECK_FAILED.format(error=str(e)))
    
    def run_interactive(self):
        print(CLI_WELCOME)
        print(CLI_COMMANDS)
        print()
        
        self.create_session("CLI Session")
        
        while True:
            try:
                command = input("querypls> ").strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == "quit" or cmd == "exit":
                    print(CLI_GOODBYE)
                    break
                elif cmd == "new":
                    name = " ".join(parts[1:]) if len(parts) > 1 else None
                    self.create_session(name)
                elif cmd == "list":
                    self.list_sessions()
                elif cmd == "switch" and len(parts) > 1:
                    self.switch_session(parts[1])
                elif cmd == "chat" and len(parts) > 1:
                    query = " ".join(parts[1:])
                    self.chat(query)
                elif cmd == "history":
                    self.show_history()
                elif cmd == "health":
                    self.health_check()
                else:
                    print(CLI_UNKNOWN_COMMAND)
            
            except KeyboardInterrupt:
                print(f"\n{CLI_GOODBYE}")
                break
            except Exception as e:
                print(CLI_ERROR.format(error=str(e)))


def main():
    cli = QueryplsCLI()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "new":
            name = sys.argv[2] if len(sys.argv) > 2 else None
            cli.create_session(name)
        elif command == "list":
            cli.list_sessions()
        elif command == "chat" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            cli.create_session("CLI Session")
            cli.chat(query)
        elif command == "health":
            cli.health_check()
        else:
            print("Usage: python cli.py [new|list|chat <query>|health]")
    else:
        cli.run_interactive()


if __name__ == "__main__":
    main() 