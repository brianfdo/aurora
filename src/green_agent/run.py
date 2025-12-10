"""
Entry point for Aurora Green Agent (tau-bench format)

Run this when a2a-server is available.
Otherwise, use main.py for Flask version.
"""

from .agent import start_green_agent

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Aurora Green Agent (A2A Starlette)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", default=8001, type=int, help="Port to listen on")
    parser.add_argument("--agent-name", default="tau_green_agent", help="Agent config name")
    args = parser.parse_args()
    
    start_green_agent(agent_name=args.agent_name, host=args.host, port=args.port)

