"""
Aurora Green Agent - A2A Server

Exposes Aurora green agent via A2A (Agent-to-Agent) protocol.
Makes it accessible over network to other remote agents.

Based on: https://a2a-protocol.org/latest/
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import uuid

# Add agents directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import core agent logic
from aurora_core import AuroraGreenAgentCore

# Create Flask app with CORS for A2A protocol
app = Flask(__name__)
CORS(app)  # Enable CORS for remote agent access

# Initialize Aurora green agent
green_agent = AuroraGreenAgentCore()

# ============================================================================
# A2A Protocol Endpoints
# Following: https://a2a-protocol.org/latest/
# ============================================================================

@app.route('/.well-known/agent-card.json', methods=['GET'])
@app.route('/.well-known/agent.json', methods=['GET'])  # AgentBeats uses this
def agent_card():
    """
    Agent Card Endpoint (A2A Protocol Standard)
    
    Returns agent metadata in JSON format following AgentBeats schema.
    """
    # Get the base URL from the request - preserve HTTPS if used
    base_url = request.url_root.rstrip('/')
    # ngrok and other tunnels use HTTPS, ensure we return the correct scheme
    if request.headers.get('X-Forwarded-Proto') == 'https' or request.scheme == 'https':
        base_url = base_url.replace('http://', 'https://')
    
    return jsonify({
        'name': 'Aurora Green Agent',
        'description': 'Orchestrator agent that evaluates white agents on context-aware travel playlist generation using AppWorld benchmark',
        'version': '1.0.0',
        'url': base_url,  # Required by AgentBeats
        'agent_type': 'green',
        'protocol': 'a2a',
        'protocol_version': '1.0',
        
        # Required by AgentBeats
        'defaultInputModes': ['text', 'json'],
        'defaultOutputModes': ['text', 'json'],
        'skills': [
            {
                'id': 'aurora-playlist-eval',
                'name': 'evaluate_playlist_generation',
                'description': 'Evaluate white agents on context-aware travel playlist generation',
                'tags': ['music', 'recommendation', 'evaluation', 'appworld']
            }
        ],
        
        'capabilities': {
            'evaluate_code': True,
            'provide_apis': True,
            'measure_quality': True,
            'task_listing': True,
            'task_evaluation': True,
            'appworld_execution': True
        },
        'benchmark': {
            'name': 'context-aware-travel-playlists',
            'domain': 'music_recommendation',
            'tasks': 3,
            'routes': ['LA → SF', 'NYC → Boston', 'Seattle → Portland']
        },
        'evaluation': {
            'metrics': ['context_alignment', 'creativity', 'ux_coherence'],
            'primary_metric': 'aurora_score',
            'weights': {
                'context_alignment': 0.4,
                'creativity': 0.3,
                'ux_coherence': 0.3
            }
        },
        'environment': {
            'available_apis': green_agent.available_apps,
            'primary_apis': ['spotify', 'phone', 'supervisor']
        },
        'endpoints': {
            'agent_card': '/.well-known/agent-card.json',
            'health': '/a2a/health',
            'tasks': '/a2a/tasks',
            'task': '/a2a/task/<id>',
            'evaluate': '/a2a/evaluate',
            'reset': '/a2a/reset'
        },
        'requirements': {
            'participant_type': 'white_agent',
            'participant_url_required': True,
            'timeout_seconds': 600
        }
    })

@app.route('/', methods=['POST'])
@app.route('/chat', methods=['POST'])
@app.route('/message', methods=['POST'])
def handle_message():
    """
    Handle incoming chat messages from AgentBeats.
    
    JSON-RPC 2.0 protocol message handling.
    """
    data = request.json or {}
    message = data.get('message', '')
    message_id = data.get('id', None)
    
    # Simple chat response for Aurora green agent
    response_text = f"""Hello! I'm the Aurora Green Agent - a benchmark orchestrator for context-aware travel playlist generation.

I evaluate white agents on their ability to generate playlists for road trips using:
• 3 routes: LA→SF, NYC→Boston, Seattle→Portland
• Real AppWorld APIs (Spotify, Phone, Weather)
• Metrics: Context Alignment (40%), Creativity (30%), UX Coherence (30%)

To run an evaluation, use the `/a2a/evaluate` endpoint with:
- white_agent_url: Your white agent's URL
- task_ids: ["aurora_001", "aurora_002", "aurora_003"] (optional)

Available endpoints:
• GET /a2a/health - Agent status
• GET /a2a/tasks - List all tasks
• GET /a2a/task/<id> - Get task details
• POST /a2a/evaluate - Run evaluation
• POST /a2a/reset - Reset agent

Ready to evaluate white agents! 🎵"""
    
    # Return JSON-RPC 2.0 success response with Message object (AgentBeats schema)
    import uuid
    response = {
        'jsonrpc': '2.0',
        'result': {
            'messageId': str(uuid.uuid4()),  # Unique message ID
            'role': 'agent',  # Must be 'agent' or 'user'
            'parts': [
                {
                    'type': 'text',
                    'text': response_text
                }
            ]
        },
        'id': message_id
    }
    
    return jsonify(response)

@app.route('/a2a/health', methods=['GET'])
def a2a_health():
    """
    A2A Health Check Endpoint
    
    Returns agent status and capabilities following A2A protocol.
    """
    return jsonify({
        'status': 'healthy',
        'protocol': 'a2a',
        'version': '1.0',
        'agent': {
            'name': 'Aurora Green Agent',
            'type': 'green',
            'benchmark': 'context-aware-travel-playlists',
            'capabilities': [
                'task_listing',
                'task_evaluation',
                'appworld_execution'
            ]
        },
        'endpoints': {
            'health': '/a2a/health',
            'tasks': '/a2a/tasks',
            'task': '/a2a/task/<id>',
            'evaluate': '/a2a/evaluate',
            'reset': '/a2a/reset'
        },
        'metadata': {
            'total_tasks': len(green_agent.tasks),
            'available_apps': green_agent.available_apps,
            'python_version': sys.version.split()[0]
        }
    })

@app.route('/a2a/tasks', methods=['GET'])
def a2a_list_tasks():
    """
    A2A List Tasks Endpoint
    
    Returns available benchmark tasks.
    """
    return jsonify({
        'protocol': 'a2a',
        'tasks': green_agent.list_tasks(),
        'total': len(green_agent.tasks)
    })

@app.route('/a2a/task/<task_id>', methods=['GET'])
def a2a_get_task(task_id: str):
    """
    A2A Get Task Details Endpoint
    
    Returns details for a specific task.
    """
    task = green_agent.get_task(task_id)
    if not task:
        return jsonify({
            'protocol': 'a2a',
            'error': f'Task {task_id} not found'
        }), 404
    
    return jsonify({
        'protocol': 'a2a',
        'task': task
    })

@app.route('/a2a/evaluate', methods=['POST'])
def a2a_evaluate():
    """
    A2A Evaluate Endpoint
    
    Evaluates a white agent on Aurora tasks.
    
    Request body:
    {
        "white_agent_url": "http://remote-white-agent:9000",
        "task_ids": ["aurora_001"]  // optional
    }
    """
    data = request.json or {}
    white_agent_url = data.get('white_agent_url')
    
    if not white_agent_url:
        return jsonify({
            'protocol': 'a2a',
            'error': 'white_agent_url is required'
        }), 400
    
    task_ids = data.get('task_ids')
    if task_ids is None:
        task_ids = [t['id'] for t in green_agent.tasks]
    
    # Run evaluation
    results = green_agent.execute_benchmark(task_ids, white_agent_url)
    
    return jsonify({
        'protocol': 'a2a',
        'status': 'completed',
        'results': results
    })

@app.route('/a2a/reset', methods=['POST'])
def a2a_reset():
    """A2A Reset Endpoint"""
    global green_agent
    green_agent = AuroraGreenAgent()
    return jsonify({
        'protocol': 'a2a',
        'status': 'reset'
    })

# ============================================================================
# Legacy Endpoints (backward compatibility)
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Legacy health endpoint - redirects to A2A"""
    return a2a_health()

@app.route('/tasks', methods=['GET'])
def tasks():
    """Legacy tasks endpoint - redirects to A2A"""
    return a2a_list_tasks()

@app.route('/task/<task_id>', methods=['GET'])
def task(task_id: str):
    """Legacy task endpoint - redirects to A2A"""
    return a2a_get_task(task_id)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    """Legacy evaluate endpoint - redirects to A2A"""
    return a2a_evaluate()

@app.route('/reset', methods=['POST'])
def reset():
    """Legacy reset endpoint - redirects to A2A"""
    return a2a_reset()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', default=8001, type=int, help='Port to listen on')
    args = parser.parse_args()
    
    print("=" * 70)
    print("🎵 Aurora Green Agent - A2A Server")
    print("=" * 70)
    print(f"✓ Protocol: A2A (Agent-to-Agent)")
    print(f"✓ Python: {sys.version.split()[0]}")
    print(f"✓ Aurora tasks: {len(green_agent.tasks)}")
    print(f"✓ AppWorld apps: {len(green_agent.available_apps)}")
    print()
    print("A2A Endpoints:")
    print("  GET  /a2a/health      - Agent health & capabilities")
    print("  GET  /a2a/tasks       - List benchmark tasks")
    print("  GET  /a2a/task/<id>   - Get task details")
    print("  POST /a2a/evaluate    - Run evaluation")
    print("  POST /a2a/reset       - Reset agent")
    print()
    print(f"✓ Listening on {args.host}:{args.port}")
    print(f"✓ Accessible from network (A2A protocol)")
    print("=" * 70)
    
    # Run server accessible from network
    app.run(host=args.host, port=args.port, debug=False)

