"""
Aurora Green Agent - Deterministic Evaluator

Refactored to follow tau-bench pattern using A2A Starlette application.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

try:
    from a2a.server.apps import A2AStarletteApplication
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.agent_execution import AgentExecutor, RequestContext
    from a2a.server.events import EventQueue
    from a2a.server.tasks import InMemoryTaskStore
    from a2a.types import AgentCard, SendMessageSuccessResponse, Message
    from a2a.utils import new_agent_text_message, get_text_parts
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


class AuroraGreenAgent:
    """
    Deterministic Aurora green agent core logic.
    
    Orchestrates evaluation of white agents without using any LLMs.
    All scoring is based on deterministic rule-based analysis.
    """
    
    def __init__(self, tasks_file: Optional[Path] = None):
        """Initialize Aurora green agent with tasks."""
        if tasks_file is None:
            tasks_file = Path(__file__).parent.parent.parent / "aurora_tasks.json"
        self.tasks = self._load_aurora_tasks(tasks_file)
        self.available_apps = ['spotify', 'phone', 'supervisor']
        
        # Initialize API provider
        import sys
        src_path = Path(__file__).parent.parent.parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        from my_util.appworld_api import create_api_provider
        self.api_provider = create_api_provider()
    
    def _load_aurora_tasks(self, tasks_file: Path) -> List[Dict]:
        """Load Aurora task definitions."""
        with open(tasks_file) as f:
            data = json.load(f)
            return data.get('tasks', [])
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a specific Aurora task."""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def list_tasks(self) -> List[Dict]:
        """List all available Aurora tasks."""
        return [
            {'id': t['id'], 'route': f"{t['route']['start']} → {t['route']['end']}"}
            for t in self.tasks
        ]
    
    def execute_task(self, task_id: str, white_agent_url: str, use_a2a: bool = False) -> Dict[str, Any]:
        """Execute a single task and evaluate the result deterministically."""
        task = self.get_task(task_id)
        if not task:
            return {'task_id': task_id, 'error': 'Task not found', 'aurora_score': 0.0}
        
        try:
            # Try A2A protocol first if requested and available
            if use_a2a and A2A_AVAILABLE:
                try:
                    code = self._get_code_via_a2a(task_id, task, white_agent_url)
                except Exception as e:
                    print(f"⚠️  A2A communication failed, falling back to HTTP: {e}")
                    code = self._get_code_via_http(task_id, task, white_agent_url)
            else:
                # Default to HTTP POST for backward compatibility
                code = self._get_code_via_http(task_id, task, white_agent_url)
            
            result = self._execute_code(code, task)
            return result
            
        except Exception as e:
            return {'task_id': task_id, 'error': str(e), 'aurora_score': 0.0}
    
    def _get_code_via_http(self, task_id: str, task: Dict, white_agent_url: str) -> str:
        """Get code from white agent via HTTP POST to /solve endpoint."""
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
            raise Exception(f'White agent returned {response.status_code}')
        
        return response.json().get('code', '')
    
    def _get_code_via_a2a(self, task_id: str, task: Dict, white_agent_url: str) -> str:
        """Get code from white agent via A2A protocol."""
        import asyncio
        from src.my_util.my_a2a import send_message, get_agent_card
        
        # Format the instruction for the white agent
        instruction = self._create_instruction(task)
        
        # Create message that includes task details in structured format
        # Put Route JSON on a single line for easier parsing
        route_json = json.dumps(task['route'])
        message = f"""Task ID: {task_id}
Instruction: {instruction}
Route: {route_json}
Allowed apps: spotify, phone

Please generate code to create a playlist for this task."""
        
        # Send message via A2A (use existing event loop or create new one)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, we can't use it directly
                # In this case, we'll use a thread to run the async code
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._send_a2a_message(white_agent_url, message))
                    response = future.result(timeout=30)
            else:
                response = loop.run_until_complete(self._send_a2a_message(white_agent_url, message))
        except RuntimeError:
            # No event loop, create one
            response = asyncio.run(self._send_a2a_message(white_agent_url, message))
        
        # Extract code from response
        from a2a.utils import get_text_parts
        if response and hasattr(response, 'root') and response.root:
            if hasattr(response.root, 'result') and hasattr(response.root.result, 'parts'):
                text_parts = get_text_parts(response.root.result.parts)
                if text_parts:
                    # Try to extract Python code from the response
                    response_text = text_parts[0]
                    # Look for code block
                    import re
                    code_match = re.search(r'```python\n(.*?)\n```', response_text, re.DOTALL)
                    if code_match:
                        return code_match.group(1)
                    # If no code block, try to find code after "Generated code"
                    code_match = re.search(r'Generated code[:\s]+(.*?)(?=\n\n|\Z)', response_text, re.DOTALL)
                    if code_match:
                        return code_match.group(1).strip()
                    # Fallback: return the full response (white agent should return code)
                    return response_text.strip()
        
        raise Exception("No code found in A2A response")
    
    async def _send_a2a_message(self, url: str, message: str):
        """Async helper to send A2A message."""
        from src.my_util.my_a2a import send_message
        return await send_message(url, message)
    
    def execute_benchmark(self, task_ids: List[str], white_agent_url: str, use_a2a: bool = False) -> Dict[str, Any]:
        """Execute full benchmark on multiple tasks."""
        results = []
        for task_id in task_ids:
            result = self.execute_task(task_id, white_agent_url, use_a2a=use_a2a)
            results.append(result)
        
        scores = [r.get('aurora_score', 0) for r in results if 'aurora_score' in r]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'benchmark': 'aurora',
            'total_tasks': len(task_ids),
            'results': results,
            'average_aurora_score': round(avg_score, 3),
            'passed': avg_score >= 0.5,
            'protocol_used': 'A2A' if use_a2a else 'HTTP'
        }
    
    def _execute_code(self, code: str, task: Dict) -> Dict[str, Any]:
        """Execute white agent code in controlled environment."""
        try:
            apis = self.api_provider.get_api_namespace(route_data=task.get('route'))
            exec_globals = {
                'route': task['route'],
                'playlist': [],
                'json': json,
                'apis': apis
            }
            exec(code, exec_globals)
            playlist = exec_globals.get('playlist', [])
            return self._evaluate_playlist_deterministic(task['id'], playlist, task)
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
    
    def _evaluate_playlist_deterministic(
        self, task_id: str, playlist: List[Dict], task: Dict
    ) -> Dict[str, Any]:
        """Deterministic evaluation of playlist quality."""
        try:
            route = task['route']
            expected_cities = [leg['city'].lower() for leg in route['legs']]
            
            context_score = self._score_context_alignment(playlist, expected_cities)
            creativity_score = self._score_creativity(playlist)
            ux_score = self._score_ux_coherence(playlist, expected_cities)
            
            aurora_score = context_score * 0.4 + creativity_score * 0.3 + ux_score * 0.3
            
            return {
                'task_id': task_id,
                'aurora_score': round(aurora_score, 3),
                'context_alignment': round(context_score, 3),
                'creativity': round(creativity_score, 3),
                'ux_coherence': round(ux_score, 3),
                'passed': aurora_score >= 0.5,
                'playlist_length': len(playlist)
            }
        except Exception as e:
            return {'task_id': task_id, 'error': f'Evaluation failed: {str(e)}', 'aurora_score': 0.0}
    
    def _score_context_alignment(self, playlist: List[Dict], expected_cities: List[str]) -> float:
        """Score how well playlist matches route cities."""
        if not playlist:
            return 0.0
        
        found_cities = set()
        for item in playlist:
            city = item.get('city', '').lower()
            if city:
                found_cities.add(city)
            
            leg_id = str(item.get('leg_id', '')).lower()
            if leg_id:
                for exp_city in expected_cities:
                    if exp_city[:2] in leg_id or leg_id in exp_city[:2]:
                        found_cities.add(exp_city)
            
            tracks = item.get('tracks', [])
            for track in tracks:
                title = str(track.get('title', '')).lower()
                artist = str(track.get('artist', '')).lower()
                for exp_city in expected_cities:
                    city_words = exp_city.split()
                    for word in city_words:
                        if len(word) > 3 and (word in title or word in artist):
                            found_cities.add(exp_city)
        
        if not found_cities:
            return 0.0
        
        coverage = len(found_cities) / len(expected_cities) if expected_cities else 0.0
        has_tracks = any(item.get('tracks') and len(item.get('tracks', [])) > 0 for item in playlist)
        track_bonus = 0.2 if has_tracks else 0.0
        
        return min(1.0, coverage * 0.8 + track_bonus)
    
    def _score_creativity(self, playlist: List[Dict]) -> float:
        """Score creativity based on track diversity."""
        if not playlist:
            return 0.0
        
        all_tracks = []
        for item in playlist:
            tracks = item.get('tracks', [])
            if isinstance(tracks, list):
                all_tracks.extend(tracks)
        
        if not all_tracks:
            return 0.0
        
        artists = set()
        for track in all_tracks:
            artist = track.get('artist', '')
            if artist:
                artists.add(artist.lower())
        
        unique_ratio = len(artists) / len(all_tracks) if all_tracks else 0.0
        track_count_score = min(1.0, len(all_tracks) / 10.0)
        
        return unique_ratio * 0.6 + track_count_score * 0.4
    
    def _score_ux_coherence(self, playlist: List[Dict], expected_cities: List[str]) -> float:
        """Score UX coherence: structure and completeness."""
        if not playlist:
            return 0.0
        
        structure_score = 0.3 if isinstance(playlist, list) and all(isinstance(item, dict) for item in playlist) else 0.0
        completeness_score = min(1.0, len(playlist) / len(expected_cities)) * 0.4 if expected_cities else 0.0
        
        valid_entries = 0
        for item in playlist:
            has_city_or_leg = 'city' in item or 'leg_id' in item
            has_tracks = 'tracks' in item and item.get('tracks')
            if has_city_or_leg and has_tracks:
                valid_entries += 1
        
        field_score = (valid_entries / len(playlist)) * 0.3 if playlist else 0.0
        
        return structure_score + completeness_score + field_score


# A2A AgentExecutor pattern (only if A2A available)
if A2A_AVAILABLE:
    from src.my_util import parse_tags
    
    class AuroraGreenAgentExecutor(AgentExecutor):
        """A2A AgentExecutor that uses AuroraGreenAgent for evaluation."""
        
        def __init__(self):
            self.aurora_agent = AuroraGreenAgent()
        
        async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
            """Execute Aurora evaluation task."""
            print("Green agent: Received a task, parsing...")
            user_input = context.get_user_input()
            tags = parse_tags(user_input)
            
            white_agent_url = tags.get("white_agent_url", "").strip()
            task_ids_str = tags.get("task_ids", "[]").strip()
            
            try:
                task_ids = json.loads(task_ids_str)
            except:
                # Default to all tasks if not specified
                task_ids = [t['id'] for t in self.aurora_agent.tasks]
            
            if not white_agent_url:
                await event_queue.enqueue_event(
                    new_agent_text_message("Error: white_agent_url not provided in task")
                )
                return
            
            print(f"Green agent: Evaluating white agent at {white_agent_url} on tasks {task_ids}")
            timestamp_started = time.time()
            
            # Use A2A protocol for communication with white agent (if available)
            # Falls back to HTTP if A2A fails
            use_a2a = True
            
            # Execute benchmark
            results = self.aurora_agent.execute_benchmark(task_ids, white_agent_url, use_a2a=use_a2a)
            
            metrics = {
                "time_used": time.time() - timestamp_started,
                "average_score": results.get('average_aurora_score', 0),
                "passed": results.get('passed', False)
            }
            
            result_emoji = "✅" if metrics["passed"] else "❌"
            
            print("Green agent: Evaluation complete.")
            await event_queue.enqueue_event(
                new_agent_text_message(
                    f"Finished. White agent evaluation: {result_emoji}\n"
                    f"Average Score: {metrics['average_score']}\n"
                    f"Time: {metrics['time_used']:.2f}s\n"
                    f"Results: {json.dumps(results, indent=2)}"
                )
            )
        
        async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
            raise NotImplementedError


def load_agent_card_toml(agent_name: str = "tau_green_agent") -> Dict[str, Any]:
    """Load agent card from TOML file."""
    if not tomllib:
        raise ImportError("tomllib or tomli required. Install: pip install tomli")
    
    current_dir = Path(__file__).parent
    toml_file = current_dir / f"{agent_name}.toml"
    
    with open(toml_file, "rb") as f:
        return tomllib.load(f)


def start_green_agent(agent_name: str = "tau_green_agent", host: str = "0.0.0.0", port: int = 8001):
    """Start the Aurora green agent using A2A Starlette application."""
    if not A2A_AVAILABLE:
        raise ImportError(
            "a2a-sdk required. Install: pip install 'a2a-sdk[http-server]' uvicorn\n"
            "Or use: uv sync (if using uv)"
        )
    
    import uvicorn
    import os
    import dotenv
    
    dotenv.load_dotenv()
    
    print("Starting Aurora green agent...")
    agent_card_dict = load_agent_card_toml(agent_name)
    
    # Use CLOUDRUN_HOST from environment if set (for Cloudflare tunnel)
    # Otherwise use AGENT_URL if set, otherwise use host:port
    cloudrun_host = os.getenv("CLOUDRUN_HOST")
    agent_url = os.getenv("AGENT_URL")
    
    if cloudrun_host:
        # CLOUDRUN_HOST specifies the cloudflared forwarded domain name
        https_enabled = os.getenv("HTTPS_ENABLED", "false").lower() == "true"
        protocol = "https" if https_enabled else "http"
        agent_url = f"{protocol}://{cloudrun_host}"
    elif agent_url:
        # Fallback to AGENT_URL if set
        agent_url = agent_url
    else:
        # Default to localhost
        agent_url = f"http://{host}:{port}"
    
    agent_card_dict["url"] = agent_url
    
    request_handler = DefaultRequestHandler(
        agent_executor=AuroraGreenAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    app = A2AStarletteApplication(
        agent_card=AgentCard(**agent_card_dict),
        http_handler=request_handler,
    )
    
    print(f"🎵 Aurora Green Agent - A2A Server")
    print(f"✓ Listening on {host}:{port}")
    print(f"✓ Agent URL: {agent_url}")
    print("=" * 70)
    
    uvicorn.run(app.build(), host=host, port=port)
