"""
Aurora Green Agent - Basic Server

Simple Flask server for local testing.
For A2A protocol compliance, use green_agent_a2a.py instead.
"""

import sys
from pathlib import Path
from flask import Flask, request, jsonify

# Add agents directory to path
sys.path.insert(0, str(Path(__file__).parent))
from aurora_core import AuroraGreenAgentCore

app = Flask(__name__)
green_agent = AuroraGreenAgentCore()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'agent': 'Aurora Green Agent',
        'benchmark': 'context-aware-travel-playlists',
        'total_tasks': len(green_agent.tasks),
        'python_version': sys.version.split()[0]
    })


@app.route('/tasks', methods=['GET'])
def list_tasks():
    """List all available Aurora tasks."""
    return jsonify({
        'tasks': green_agent.list_tasks(),
        'total': len(green_agent.tasks)
    })


@app.route('/task/<task_id>', methods=['GET'])
def get_task(task_id: str):
    """Get details for a specific task."""
    task = green_agent.get_task(task_id)
    if not task:
        return jsonify({'error': f'Task {task_id} not found'}), 404
    return jsonify(task)


@app.route('/evaluate', methods=['POST'])
def evaluate():
    """
    Evaluate a white agent on Aurora tasks.
    
    Body:
    {
        "white_agent_url": "http://localhost:9000",
        "task_ids": ["aurora_001"]  // optional
    }
    """
    data = request.get_json(silent=True) or {}
    white_agent_url = data.get('white_agent_url', 'http://localhost:9000')
    if not white_agent_url:
        return jsonify({'error': 'white_agent_url is required'}), 400
    
    task_ids = data.get('task_ids')
    if task_ids is None:
        task_ids = [t['id'] for t in green_agent.tasks]
    else:
        known = {t['id'] for t in green_agent.tasks}
        unknown = [tid for tid in task_ids if tid not in known]
        if unknown:
            return jsonify({'error': f'unknown task_ids: {unknown}'}), 404
        
    try:
        results = green_agent.execute_benchmark(task_ids, white_agent_url)
        return jsonify({'status': 'completed',
                        'results': results})
    except Exception as e:
        return jsonify({'status': 'error',
                        'message': str(e)}), 500

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=8001, type=int)
    args = parser.parse_args()
    
    print("=" * 70)
    print("🎵 Aurora Green Agent")
    print("=" * 70)
    print(f"✓ Python {sys.version.split()[0]}")
    print(f"✓ Aurora tasks: {len(green_agent.tasks)}")
    print(f"✓ Listening on {args.host}:{args.port}")
    print("=" * 70)
    
    app.run(host=args.host, port=args.port, debug=False)
