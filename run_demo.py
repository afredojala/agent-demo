# ABOUTME: Demo runner script to initialize database and test the agent system
# ABOUTME: Sets up the database with seed data and runs a sample task
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))


def setup_demo():
    print("=== Agentic Demo Setup ===")

    # Initialize database
    print("1. Initializing database...")
    from backend.seed import init_database

    init_database()
    print("✓ Database initialized")

    # Test agent system (if OpenAI API key is available)
    if os.getenv("OPENAI_API_KEY"):
        print("2. Testing agent system...")
        try:

            # result = run_task("Show Acme's open tickets in a triage view")
            print(f"✓ Agent test completed: {result}...")
        except Exception as e:
            print(f"⚠ Agent test failed: {e}")
    else:
        print("⚠ OPENAI_API_KEY not set, skipping agent test")

    print("\n=== Demo Ready ===")
    print("To run the full demo:")
    print("1. Terminal 1: uv run uvicorn backend.app:app --reload")
    print("2. Terminal 2: uv run python agent/websocket_server.py")
    print("3. Terminal 3: cd frontend && npm install && npm run dev")
    print("4. Terminal 4: uv run python agent/crew.py")


if __name__ == "__main__":
    setup_demo()
