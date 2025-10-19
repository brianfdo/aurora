"""
Aurora Green Agent - Full A2A Server with AgentBeats SDK utilities

For green agents, we need to implement our own A2A server since the SDK's
`agentbeats run` command is designed for white agents (LLM-powered).

This version uses SDK utilities where helpful but implements the full green agent logic.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

# Import core Aurora logic
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
from aurora_core import AuroraGreenAgentCore

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize Aurora green agent
green_agent = AuroraGreenAgentCore()

# ============================================================================
# A2A Protocol Endpoints for AgentBeats
# ============================================================================

@app.route('/.well-known/agent-card.json', methods=['GET'])
@app.route('/.well-known/agent.json', methods=['GET'])
def agent_card():
    """Agent Card Endpoint (A2A Protocol)"""
    base_url = request.url_root.rstrip('/')
    if request.headers.get('X-Forwarded-Proto') == 'https' or request.scheme == 'https':
        base_url = base_url.replace('http://', 'https://')
    
    return jsonify({
        'name': 'Aurora Green Agent (SDK)',
        'description': 'Green agent for evaluating white agents on context-aware travel playlist generation',
        'version': '1.0.0',
        'url': base_url,
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
                'tags': ['music', 'recommendation', 'evaluation', 'appworld', 'sdk']
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
            'name': 'Aurora',
            'domain': 'music_recommendation',
            'tasks': len(green_agent.tasks),
            'routes': [f"{t['route']['start']} → {t['route']['end']}" for t in green_agent.tasks]
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
            'primary_apis': ['spotify', 'phone']
        }
    })

@app.route('/', methods=['POST'])
@app.route('/chat', methods=['POST'])
@app.route('/message', methods=['POST'])
def handle_message():
    """Handle incoming chat messages (JSON-RPC 2.0)"""
    data = request.json or {}
    message_id = data.get('id', None)
    
    response_text = f"""🎵 Aurora Green Agent (SDK Version)

I'm a benchmark orchestrator for evaluating white agents on context-aware travel playlist generation.

📊 Benchmark: Aurora
• 3 routes: LA→SF, NYC→Boston, Seattle→Portland
• Real AppWorld APIs (Spotify, Phone)
• Metrics: Context (40%), Creativity (30%), UX (30%)

🔧 Built with:
• AgentBeats SDK utilities
• Custom green agent orchestration
• AppWorld environment simulation

📡 Endpoints:
• GET /a2a/health - Status check
• GET /a2a/tasks - List all tasks
• GET /a2a/task/<id> - Task details
• POST /a2a/evaluate - Run evaluation
• POST /a2a/reset - Reset state

To evaluate a white agent:
POST /a2a/evaluate
{{"white_agent_url": "http://your-white-agent:9000"}}

Ready to evaluate! ✨"""
    
    return jsonify({
        'jsonrpc': '2.0',
        'result': {
            'messageId': str(uuid.uuid4()),
            'role': 'agent',
            'parts': [{'type': 'text', 'text': response_text}]
        },
        'id': message_id
    })

@app.route('/a2a/health', methods=['GET'])
def a2a_health():
    """A2A Health Check"""
    return jsonify({
        'protocol': 'a2a',
        'status': 'healthy',
        'version': '1.0-sdk',
        'agent': {
            'name': 'Aurora Green Agent (SDK)',
            'type': 'green',
            'benchmark': 'Aurora',
            'sdk_version': 'agentbeats-1.2.5'
        },
        'metadata': {
            'total_tasks': len(green_agent.tasks),
            'available_apps': green_agent.available_apps,
            'python_version': sys.version.split()[0]
        }
    })

@app.route('/a2a/tasks', methods=['GET'])
def a2a_list_tasks():
    """List all Aurora tasks"""
    return jsonify({
        'protocol': 'a2a',
        'tasks': green_agent.list_tasks(),
        'total': len(green_agent.tasks)
    })

@app.route('/a2a/task/<task_id>', methods=['GET'])
def a2a_get_task(task_id: str):
    """Get specific task details"""
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
    Main evaluation endpoint.
    
    Request body:
    {
        "white_agent_url": "http://white-agent:9000",
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
    
    # Use the green agent's evaluation logic
    results = green_agent.evaluate_white_agent(white_agent_url, task_ids)
    
    return jsonify({
        'protocol': 'a2a',
        'status': 'completed',
        'results': results
    })

@app.route('/a2a/reset', methods=['POST'])
def a2a_reset():
    """Reset agent state"""
    return jsonify({
        'protocol': 'a2a',
        'status': 'reset',
        'message': 'Aurora Green Agent (SDK) state reset.'
    })

# ============================================================================
# Launcher Endpoints (for AgentBeats platform integration)
# ============================================================================

@app.route('/launcher/reset', methods=['POST'])
def launcher_reset():
    """Launcher reset endpoint for AgentBeats"""
    return jsonify({
        'status': 'ready',
        'agent': 'Aurora Green Agent (SDK)',
        'message': 'Launcher reset complete'
    })

@app.route('/launcher/health', methods=['GET'])
def launcher_health():
    """Launcher health check"""
    return jsonify({
        'status': 'healthy',
        'launcher': 'Aurora SDK Launcher',
        'agent_url': request.host_url.rstrip('/')
    })

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Aurora Green Agent (SDK Version)")
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=8001, type=int)
    args = parser.parse_args()
    
    print("=" * 70)
    print("🎵 Aurora Green Agent - AgentBeats SDK Version")
    print("=" * 70)
    print(f"✓ Protocol: A2A (Agent-to-Agent)")
    print(f"✓ Python: {sys.version.split()[0]}")
    print(f"✓ AgentBeats SDK: 1.2.5")
    print(f"✓ Aurora tasks: {len(green_agent.tasks)}")
    print(f"✓ AppWorld apps: {len(green_agent.available_apps)}")
    print("\nA2A Endpoints:")
    print("  GET  /.well-known/agent.json")
    print("  GET  /a2a/health")
    print("  GET  /a2a/tasks")
    print("  GET  /a2a/task/<id>")
    print("  POST /a2a/evaluate")
    print("  POST /a2a/reset")
    print("  POST /chat")
    print("\nLauncher Endpoints:")
    print("  GET  /launcher/health")
    print("  POST /launcher/reset")
    print(f"\n✓ Listening on {args.host}:{args.port}")
    print(f"✓ Accessible from network (A2A protocol)")
    print("=" * 70)
    
    app.run(host=args.host, port=args.port, debug=False)

