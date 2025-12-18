"""
White Agent Launcher

Entry point for running the white agent server.
"""

from .agent import WhiteAgent

if __name__ == '__main__':
    agent = WhiteAgent()
    agent.run()


