"""
Aurora Green Agent - Main Entry Point

Supports both agentbeats run_ctrl and direct execution.
"""

import os
import sys
import typer
from pathlib import Path
from pydantic_settings import BaseSettings

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class AuroraSettings(BaseSettings):
    role: str = "unspecified"
    host: str = "0.0.0.0"
    agent_port: int = 8001


app = typer.Typer(help="Aurora Green Agent - Deterministic evaluator for white agents")


@app.command()
def green():
    """Start the green agent (assessment manager)."""
    from src.green_agent import start_green_agent
    start_green_agent()


@app.command()
def run():
    """Run agent based on ROLE environment variable (for agentbeats run_ctrl)."""
    settings = AuroraSettings()
    from src.green_agent import start_green_agent
    import dotenv
    dotenv.load_dotenv()
    
    if settings.role == "green":
        start_green_agent(agent_name="tau_green_agent", host=settings.host, port=settings.agent_port)
    else:
        raise ValueError(f"Unknown role: {settings.role}")


if __name__ == "__main__":
    # Support direct execution
    if os.getenv("ROLE") == "green" or "run_ctrl" in sys.argv:
        from src.green_agent import start_green_agent
        import dotenv
        dotenv.load_dotenv()
        host = os.getenv("AGENT_HOST", "0.0.0.0")
        port = int(os.getenv("AGENT_PORT", "8010"))  # Default to 8010 for agentbeats
        start_green_agent(agent_name="tau_green_agent", host=host, port=port)
    else:
        app()
else:
    # Fallback to Flask version for direct execution
    from green_agent.agent import AuroraGreenAgent
    from my_util.my_a2a import create_a2a_server, create_agent_card
    from flask import request, jsonify
    import argparse
    
    def create_green_agent_server(host: str = '0.0.0.0', port: int = 8001):
        """Create Flask-based green agent server."""
        green_agent = AuroraGreenAgent()
        app = create_a2a_server(
            agent_name='Aurora Green Agent',
            agent_type='green',
            description='Deterministic evaluator for white agents on context-aware travel playlist generation'
        )
        
        # A2A endpoints (same as before)
        @app.route('/.well-known/agent-card.json', methods=['GET'])
        @app.route('/.well-known/agent.json', methods=['GET'])
        def agent_card():
            base_url = request.url_root.rstrip('/')
            if request.headers.get('X-Forwarded-Proto') == 'https' or request.scheme == 'https':
                base_url = base_url.replace('http://', 'https://')
            
            card = create_agent_card(app, base_url, {
                'task_listing': True,
                'task_evaluation': True,
                'appworld_execution': True,
            })
            
            card.update({
                'preferredTransport': 'JSONRPC',
                'protocolVersion': '1.0',
                'skills': [{
                    'id': 'aurora-playlist-eval',
                    'name': 'evaluate_playlist_generation',
                    'description': 'Evaluate white agents on context-aware travel playlist generation',
                    'tags': ['music', 'recommendation', 'evaluation', 'appworld']
                }],
            })
            return jsonify(card)
        
        @app.route('/a2a/health', methods=['GET'])
        def a2a_health():
            return jsonify({'status': 'healthy', 'protocol': 'a2a', 'version': '1.0'})
        
        @app.route('/a2a/tasks', methods=['GET'])
        def a2a_list_tasks():
            return jsonify({'protocol': 'a2a', 'tasks': green_agent.list_tasks(), 'total': len(green_agent.tasks)})
        
        @app.route('/a2a/task/<task_id>', methods=['GET'])
        def a2a_get_task(task_id: str):
            task = green_agent.get_task(task_id)
            if not task:
                return jsonify({'protocol': 'a2a', 'error': f'Task {task_id} not found'}), 404
            return jsonify({'protocol': 'a2a', 'task': task})
        
        @app.route('/a2a/evaluate', methods=['POST'])
        def a2a_evaluate():
            data = request.json or {}
            white_agent_url = data.get('white_agent_url')
            if not white_agent_url:
                return jsonify({'protocol': 'a2a', 'error': 'white_agent_url is required'}), 400
            task_ids = data.get('task_ids') or [t['id'] for t in green_agent.tasks]
            results = green_agent.execute_benchmark(task_ids, white_agent_url)
            return jsonify({'protocol': 'a2a', 'status': 'completed', 'results': results})
        
        @app.route('/chat', methods=['POST'])
        def handle_chat():
            import uuid
            return jsonify({
                'jsonrpc': '2.0',
                'result': {
                    'messageId': str(uuid.uuid4()),
                    'role': 'agent',
                    'parts': [{'type': 'text', 'text': 'Aurora Green Agent ready!'}]
                },
                'id': request.json.get('id') if request.json else None
            })
        
        return app
    
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('--host', default='0.0.0.0')
        parser.add_argument('--port', default=8001, type=int)
        args = parser.parse_args()
        
        app = create_green_agent_server(host=args.host, port=args.port)
        print(f"🎵 Aurora Green Agent (Flask)")
        print(f"✓ Listening on {args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=False)
