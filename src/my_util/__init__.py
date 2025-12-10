"""Utility modules for Aurora agents"""

from .my_a2a import parse_tags
from .appworld_api import create_api_provider

__all__ = ['parse_tags', 'create_api_provider']

# A2A client functions (if available)
try:
    from .my_a2a import get_agent_card, wait_agent_ready, send_message
    __all__.extend(['get_agent_card', 'wait_agent_ready', 'send_message'])
except ImportError:
    pass

# Export as my_a2a for compatibility
from . import my_a2a

