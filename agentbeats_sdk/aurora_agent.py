"""
Aurora Green Agent - SDK Version

Lightweight wrapper around core logic for AgentBeats SDK integration.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))

# Import shared core logic
from aurora_core import AuroraGreenAgentCore


# Alias for SDK compatibility
class AuroraGreenAgentSDK(AuroraGreenAgentCore):
    """SDK version of Aurora green agent - uses shared core logic."""
    pass


def create_agent():
    """Factory function for AgentBeats SDK."""
    return AuroraGreenAgentSDK()


if __name__ == "__main__":
    agent = create_agent()
    print(f"Aurora Green Agent SDK initialized")
    print(f"Tasks loaded: {len(agent.tasks)}")
    print(f"Available apps: {agent.available_apps}")
