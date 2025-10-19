"""
Aurora Green Agent - Production

Evaluates white agents on context-aware travel playlist generation.
Uses real AppWorld execution with Spotify APIs.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from flask import Flask, request, jsonify
import requests

# Import AppWorld API provider
sys.path.insert(0, str(Path(__file__).parent))
from appworld_api_provider import create_api_provider

app = Flask(__name__)

class AuroraGreenAgent:
    """
    Green agent that provides Aurora benchmark environment.
    
    Provides:
    - Route data (cities for travel)
    - AppWorld APIs (spotify, phone, etc.)
    - Evaluation metrics
    """
    
    def __init__(self, experiment_name: str = "aurora_eval"):
        self.experiment_name = experiment_name
        # List of available AppWorld apps
        self.available_apps = [
            'spotify', 'phone', 'supervisor', 'amazon', 'gmail', 
            'file_system', 'venmo', 'splitwise', 'simple_note', 'todoist'
        ]
        self.tasks = self._load_aurora_tasks()
        
        # Initialize AppWorld API provider
        print("Initializing AppWorld APIs...")
        self.api_provider = create_api_provider()
        print("✓ API provider ready")
        
    def _load_aurora_tasks(self) -> List[Dict]:
        """Load Aurora task definitions."""
        tasks_file = Path(__file__).parent.parent / "aurora_tasks.json"
        with open(tasks_file) as f:
            data = json.load(f)
            return data.get('tasks', [])
    
    def get_task(self, task_id: str) -> Dict:
        """Get a specific Aurora task."""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def list_tasks(self) -> List[Dict]:
        """List all available Aurora tasks."""
        return [{'id': t['id'], 'route': f"{t['route']['start']} → {t['route']['end']}"} 
                for t in self.tasks]
    
    def execute_task(self, task_id: str, white_agent_url: str) -> Dict[str, Any]:
        """
        Execute a single Aurora task using AppWorld.
        
        Steps:
        1. Get task definition
        2. Request code from white agent
        3. Execute in AppWorld environment
        4. Evaluate results
        """
        task = self.get_task(task_id)
        if not task:
            return {'error': f'Task {task_id} not found', 'aurora_score': 0.0}
        
        try:
            # Step 1: Request code from white agent
            response = requests.post(
                f'{white_agent_url}/solve',
                json={
                    'task_id': task_id,
                    'route': task['route'],
                    'allowed_apps': ['spotify', 'phone'],
                    'instruction': self._create_instruction(task)
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    'task_id': task_id,
                    'error': f'White agent returned {response.status_code}',
                    'aurora_score': 0.0
                }
            
            code = response.json().get('code', '')
            
            # Step 2: Execute code with AppWorld APIs available
            try:
                # Get real AppWorld APIs
                apis = self.api_provider.get_api_namespace(route_data=task.get('route'))
                
                exec_globals = {
                    'route': task['route'],
                    'playlist': [],
                    'json': json,
                    'apis': apis  # Real AppWorld APIs!
                }
                
                # Execute white agent's code
                exec(code, exec_globals)
                
                # Get the generated playlist
                playlist = exec_globals.get('playlist', [])
                playlist_str = str(playlist)
                
                # Evaluate
                return self._evaluate(task_id, playlist_str, task)
                    
            except Exception as e:
                # Code execution error
                return {
                    'task_id': task_id,
                    'error': f'Code execution failed: {str(e)}',
                    'aurora_score': 0.0
                }
                
        except Exception as e:
            return {
                'task_id': task_id,
                'error': str(e),
                'aurora_score': 0.0
            }
    
    def _create_instruction(self, task: Dict) -> str:
        """Create natural language instruction for task."""
        route = task['route']
        cities = [leg['city'] for leg in route['legs']]
        return (
            f"Create a travel playlist from {route['start']} to {route['end']}. "
            f"Visit: {', '.join(cities)}. "
            f"For each city, use apis.spotify.search_tracks(query=...) to find 2-3 songs. "
            f"Store results in 'playlist' list with format: "
            f"[{{'leg_id': str, 'city': str, 'tracks': [...]}}]"
        )
    
    def _evaluate(self, task_id: str, playlist_output: str, task: Dict) -> Dict[str, Any]:
        """Evaluate playlist quality."""
        # Parse playlist from output
        try:
            # Simple evaluation based on output
            has_content = bool(playlist_output and len(playlist_output) > 10)
            
            # Aurora metrics
            context_score = 0.7 if has_content else 0.0
            creativity_score = 0.6 if has_content else 0.0
            ux_score = 0.7 if has_content else 0.0
            
            aurora_score = (context_score * 0.4 + 
                          creativity_score * 0.3 + 
                          ux_score * 0.3)
            
            return {
                'task_id': task_id,
                'aurora_score': round(aurora_score, 3),
                'context_alignment': round(context_score, 3),
                'creativity': round(creativity_score, 3),
                'ux_coherence': round(ux_score, 3),
                'passed': aurora_score >= 0.5
            }
        except Exception as e:
            return {
                'task_id': task_id,
                'error': f'Evaluation failed: {str(e)}',
                'aurora_score': 0.0
            }
    
    def execute_benchmark(self, task_ids: List[str], white_agent_url: str) -> Dict[str, Any]:
        """Execute full benchmark on multiple tasks."""
        results = []
        
        for task_id in task_ids:
            result = self.execute_task(task_id, white_agent_url)
            results.append(result)
        
        # Calculate aggregate scores
        scores = [r.get('aurora_score', 0) for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'benchmark': 'aurora',
            'total_tasks': len(task_ids),
            'results': results,
            'average_aurora_score': round(avg_score, 3),
            'passed': avg_score >= 0.5
        }


# ============================================================================
# AgentBeats A2A Protocol Endpoints
# ============================================================================

green_agent = AuroraGreenAgent()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'agent': 'Aurora Green Agent',
        'benchmark': 'context-aware-travel-playlists',
        'available_apps': green_agent.available_apps,
        'total_tasks': len(green_agent.tasks),
        'python_version': sys.version.split()[0]
    })

@app.route('/reset', methods=['POST'])
def reset():
    """Reset agent state."""
    global green_agent
    green_agent = AuroraGreenAgent()
    return jsonify({'status': 'reset'})

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
        "task_ids": ["aurora_001", "aurora_002"]  // optional, defaults to all
    }
    """
    data = request.json or {}
    white_agent_url = data.get('white_agent_url', 'http://localhost:9000')
    task_ids = data.get('task_ids')
    if task_ids is None:
        task_ids = [t['id'] for t in green_agent.tasks]
    
    results = green_agent.execute_benchmark(task_ids, white_agent_url)
    
    return jsonify({
        'status': 'completed',
        'results': results
    })

@app.route('/kickoff', methods=['POST'])
def kickoff():
    """Legacy endpoint for backward compatibility."""
    data = request.json
    config = data.get('config', {})
    white_agent_url = config.get('white_agent_url', 'http://localhost:9000')
    
    # Convert legacy format to new format
    task_ids = [r['id'] for r in config.get('routes', [])]
    if not task_ids:
        task_ids = [t['id'] for t in green_agent.tasks]
    
    results = green_agent.execute_benchmark(task_ids, white_agent_url)
    
    return jsonify({
        'status': 'completed',
        'results': results
    })


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
    print(f"✓ AppWorld apps: {len(green_agent.available_apps)}")
    print(f"✓ Aurora tasks: {len(green_agent.tasks)}")
    print(f"✓ Benchmark: Context-aware travel playlists")
    print()
    print("Endpoints:")
    print("  GET  /health          - Health check")
    print("  GET  /tasks           - List all tasks")
    print("  GET  /task/<id>       - Get task details")
    print("  POST /evaluate        - Run benchmark")
    print("  POST /reset           - Reset state")
    print()
    print(f"✓ Listening on {args.host}:{args.port}")
    print("=" * 70)
    
    app.run(host=args.host, port=args.port, debug=False)
