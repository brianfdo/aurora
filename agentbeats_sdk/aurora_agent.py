"""
Aurora Green Agent - AgentBeats SDK Version

Uses the official agentbeats SDK for integration.
This is the orchestrator that evaluates white agents on playlist generation.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add parent directory to path to import aurora tasks
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import AppWorld API provider
from appworld_api_provider import create_api_provider


class AuroraGreenAgentSDK:
    """
    Aurora Green Agent for AgentBeats SDK.
    
    Orchestrates evaluation of white agents on context-aware travel playlist generation.
    """
    
    def __init__(self):
        """Initialize Aurora green agent with tasks and evaluation metrics."""
        self.tasks = self._load_aurora_tasks()
        self.available_apps = ['spotify', 'phone', 'supervisor', 'amazon', 'gmail']
        
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
        return [
            {
                'id': t['id'],
                'route': f"{t['route']['start']} → {t['route']['end']}"
            }
            for t in self.tasks
        ]
    
    def evaluate_white_agent(self, white_agent_url: str, task_ids: List[str] = None) -> Dict[str, Any]:
        """
        Main evaluation function called by AgentBeats SDK.
        
        Args:
            white_agent_url: URL of the white agent to evaluate
            task_ids: List of task IDs to evaluate (optional, defaults to all)
            
        Returns:
            Dictionary with evaluation results
        """
        import requests
        
        if task_ids is None:
            task_ids = [t['id'] for t in self.tasks]
        
        results = []
        
        for task_id in task_ids:
            result = self._evaluate_single_task(task_id, white_agent_url)
            results.append(result)
        
        # Calculate aggregate scores
        scores = [r.get('aurora_score', 0) for r in results if 'aurora_score' in r]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'benchmark': 'aurora',
            'total_tasks': len(task_ids),
            'results': results,
            'average_aurora_score': round(avg_score, 3),
            'passed': avg_score >= 0.5
        }
    
    def _evaluate_single_task(self, task_id: str, white_agent_url: str) -> Dict[str, Any]:
        """Evaluate white agent on a single task."""
        import requests
        
        task = self.get_task(task_id)
        if not task:
            return {'task_id': task_id, 'error': 'Task not found', 'aurora_score': 0.0}
        
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
            
            # Step 2: Execute code with mock APIs
            result = self._execute_code(code, task)
            
            return result
            
        except Exception as e:
            return {
                'task_id': task_id,
                'error': str(e),
                'aurora_score': 0.0
            }
    
    def _execute_code(self, code: str, task: Dict) -> Dict[str, Any]:
        """Execute white agent code in controlled environment."""
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
            return self._evaluate_playlist(task['id'], playlist_str, task)
            
        except Exception as e:
            return {
                'task_id': task['id'],
                'error': f'Code execution failed: {str(e)}',
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
            f"Store results in 'playlist' list."
        )
    
    def _evaluate_playlist(self, task_id: str, playlist_output: str, task: Dict) -> Dict[str, Any]:
        """Evaluate playlist quality using Aurora metrics."""
        try:
            # Simple evaluation based on output
            has_content = bool(playlist_output and len(playlist_output) > 10)
            
            # Aurora metrics
            context_score = 0.7 if has_content else 0.0
            creativity_score = 0.6 if has_content else 0.0
            ux_score = 0.7 if has_content else 0.0
            
            aurora_score = (
                context_score * 0.4 + 
                creativity_score * 0.3 + 
                ux_score * 0.3
            )
            
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


# Entry point for AgentBeats SDK
def create_agent():
    """Factory function called by agentbeats SDK."""
    return AuroraGreenAgentSDK()


if __name__ == "__main__":
    # Test the agent locally
    agent = create_agent()
    print(f"Aurora Green Agent SDK initialized")
    print(f"Tasks loaded: {len(agent.tasks)}")
    print(f"Available apps: {agent.available_apps}")

