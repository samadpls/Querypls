"""
Command-line interface for Querypls SQL generation.
"""

from src.config.constants import DEFAULT_SESSION_NAME
from src.schemas.requests import NewChatRequest
from src.backend.orchestrator import BackendOrchestrator
import sys
import os
import json
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class QueryplsCLI:
    def __init__(self):
        self.orchestrator = BackendOrchestrator()
        self.current_session_id = None

    def create_session(self, name: Optional[str] = None) -> str:
        request = NewChatRequest(session_name=name)
        session_info = self.orchestrator.create_new_session(request)
        self.current_session_id = session_info.session_id
        print(
            f"""Session created: {
                session_info.session_name} (ID: {
                session_info.session_id})"""
        )
        return session_info.session_id

    def list_sessions(self):
        sessions = self.orchestrator.list_sessions()
        if not sessions:
            print("No sessions found.")
            return
        print("Available sessions:")
        for i, session in enumerate(sessions, 1):
            print(f"{i}. {session.session_name}")
            print(f"   ID: {session.session_id}")
            print(f"   Messages: {session.message_count}")
            print(f"   Last activity: {session.last_activity}")
            print()

    def switch_session(self, session_id: str):
        session = self.orchestrator.get_session(session_id)
        if not session:
            print(f"Session not found: {session_id}")
            return
        self.current_session_id = session_id
        print(f"Switched to session: {session.session_name}")

    def chat(self, query: str):
        if not self.current_session_id:
            print("No active session. Please create or switch to a session.")
            return

        try:
            response = self.orchestrator.generate_sql_response(
                self.current_session_id, query
            )
            print("\nResponse generated:")
            print(response.content)

            if response.sql_response:
                print("\nSQL Details:")
                print(f"  Query Type: {response.sql_response.query_type}")
                print(f"  Complexity: {response.sql_response.complexity}")
                print(f"  Tables Used: {', '.join(response.sql_response.tables_used)}")
                print(f"  Columns: {', '.join(response.sql_response.columns_selected)}")
                print(f"  Estimated Rows: {response.sql_response.estimated_rows}")
                if response.sql_response.warnings:
                    print(f"  Warnings: {', '.join(response.sql_response.warnings)}")

        except Exception as e:
            print(f"Error: {str(e)}")

    def show_history(self):
        if not self.current_session_id:
            print("No session selected.")
            return

        try:
            conversation = self.orchestrator.get_conversation_history(
                self.current_session_id
            )
            print("\nConversation history:")
            for message in conversation.messages:
                print(f"  {message.role.upper()}: {message.content}")
        except Exception as e:
            print(f"Error: {str(e)}")

    def health_check(self):
        try:
            health = self.orchestrator.health_check()
            print("Health check successful.")
            print(f"  Status: {health.status}")
            print(f"  Version: {health.version}")
            print(f"  Services: {json.dumps(health.services, indent=2)}")
        except Exception as e:
            print(f"Health check failed: {str(e)}")

    def run_interactive(self):
        print("Welcome to Querypls CLI!")
        print("Commands: new, list, switch <id>, chat <query>, history, health, quit")
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
                    print("Goodbye!")
                    break
                elif cmd == "new":
                    name = " ".join(parts[1:]) if len(parts) > 1 else None
                    self.create_session(name)
                elif cmd == "list":
                    self.list_sessions()
                parts = command.split()
                cmd = parts[0].lower()

                if cmd == "quit" or cmd == "exit":
                    print("Goodbye!")
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
                    print("Unknown command.")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")


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
