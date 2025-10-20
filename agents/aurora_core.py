"""
Aurora Green Agent - Core Logic

Shared evaluation logic used by both SDK and production versions.
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Any, List
import requests

CITY_KEYWORDS = {
    "Los Angeles": ["los angeles","la","california","hollywood"],
    "Santa Barbara": ["santa barbara","california","sb"],
    "San Francisco": ["san francisco","sf","bay","golden gate","california"],
    "New York": ["new york","nyc","manhattan","brooklyn"],
    "Boston": ["boston","massachusetts","ma"],
    "Seattle": ["seattle","washington","pnw"],
    "Portland": ["portland","oregon","pnw"],
}

CITY_GENRES = {
    "Los Angeles": {"hip hop","pop","west coast","surf","rock"},
    "Santa Barbara": {"surf","acoustic","indie","rock","folk"},
    "San Francisco": {"indie","alt","electronic","rock","hip hop"},
    "New York": {"hip hop","jazz","pop","alt","rock"},
    "Boston": {"alt","rock","indie","folk"},
    "Seattle": {"grunge","alt","indie","rock"},
    "Portland": {"indie","folk","alt","rock"},
}

def _txt(tr):
    title = str(tr.get("title",""))
    artist = str(tr.get("artist",""))
    album = str(tr.get("album",""))
    return f"{title} {artist} {album}".lower()

def _count_city_refs(tracks, city):
    keys = CITY_KEYWORDS.get(city, [])
    return sum(any(k in _txt(tr) for k in keys) for tr in tracks)

def _infer_genres(tracks):
    out = []
    for tr in tracks:
        g = tr.get("genre")
        if g:
            out.append(str(g).lower())
        else:
            t = _txt(tr)
            if "jazz" in t: out.append("jazz")
            elif "hip hop" in t or "rap" in t: out.append("hip hop")
            elif "folk" in t: out.append("folk")
            elif "surf" in t: out.append("surf")
            elif "electro" in t or "synth" in t: out.append("electronic")
            elif "grunge" in t: out.append("grunge")
            elif "indie" in t: out.append("indie")
            else: out.append("pop")
    return out

def _artist_diversity(tracks):
    artists = [str(tr.get("artist","")).lower() for tr in tracks if tr.get("artist")]
    return (len(set(artists))/len(artists)) if artists else 0.0

def _genre_diversity(genres):
    return (len(set(genres))/len(genres)) if genres else 0.0

class AuroraGreenAgentCore:
    """
    Core Aurora green agent logic.
    
    Orchestrates evaluation of white agents on context-aware travel playlist generation.
    """
    
    def __init__(self):
        """Initialize Aurora green agent with tasks and evaluation metrics."""
        self.tasks = self._load_aurora_tasks()
        self.available_apps = ['spotify', 'phone', 'supervisor']
        
        # Initialize API provider
        from appworld_api_provider import create_api_provider
        self.api_provider = create_api_provider()
        
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
    
    def execute_task(self, task_id: str, white_agent_url: str) -> Dict[str, Any]:
        """Execute a single task and evaluate the result."""
        task = self.get_task(task_id)
        if not task:
            return {'task_id': task_id, 'error': 'Task not found', 'aurora_score': 0.0}
        
        try:
            # Request code from white agent
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
            
            # Execute code with real APIs
            result = self._execute_code(code, task)
            return result
            
        except Exception as e:
            return {
                'task_id': task_id,
                'error': str(e),
                'aurora_score': 0.0
            }
    
    def execute_benchmark(self, task_ids: List[str], white_agent_url: str) -> Dict[str, Any]:
        """Execute full benchmark on multiple tasks."""
        results = []
        
        for task_id in task_ids:
            result = self.execute_task(task_id, white_agent_url)
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
    
    def _execute_code(self, code: str, task: Dict) -> Dict[str, Any]:
        try:
            apis = self.api_provider.get_api_namespace(route_data=task.get('route'))

            exec_globals = {
                'route': task['route'],
                'playlist': [],     # white agent should write here
                'json': json,
                'apis': apis
            }

            exec(code, exec_globals)

            playlist = exec_globals.get('playlist', [])
            # Accept JSON string fallback
            if isinstance(playlist, str):
                try:
                    playlist = json.loads(playlist)
                except Exception:
                    pass

            # Basic schema validation
            if not isinstance(playlist, list):
                raise ValueError("playlist must be a list")
            for leg in playlist:
                if not isinstance(leg, dict):
                    raise ValueError("each playlist leg must be a dict")
                if 'city' not in leg or 'tracks' not in leg:
                    raise ValueError("each leg must have 'city' and 'tracks'")
                if not isinstance(leg['tracks'], list):
                    raise ValueError("'tracks' must be a list")

            # Evaluate using structured playlist
            return self._evaluate_playlist(task['id'], playlist, task)

        except Exception as e:
            return {
                'task_id': task['id'],
                'error': f'Code execution failed: {str(e)}',
                'aurora_score': 0.0
            }
    
    def _create_instruction(self, task: Dict) -> str:
        route = task['route']
        cities = [leg['city'] for leg in route['legs']]
        return (
            f"Create a travel playlist from {route['start']} to {route['end']} visiting {', '.join(cities)}. "
            f"For each city, call apis.spotify.search_tracks(city_name, limit=10) and select 3 tracks that "
            f"(1) reference the city or match its vibe, and (2) avoid repeating artists across different cities. "
            f"Return a Python list named 'playlist' with items like {{'city': <city>, 'tracks': [{{'title':..,'artist':..,'genre':..}}, ...]}}."
        )

    
    def _evaluate_playlist(self, task_id: str, playlist: List[Dict], task: Dict) -> Dict[str, Any]:
        try:
            if not playlist:
                return {'task_id': task_id, 'aurora_score': 0.0,
                        'context_alignment': 0.0, 'creativity': 0.0,
                        'ux_coherence': 0.0, 'passed': False}

            # 1) Context per leg: city references + genre fit
            per_leg_ctx = []
            all_tracks = []
            for leg in playlist:
                city = leg.get("city") or leg.get("name") or leg.get("label")
                tracks = leg.get("tracks", [])
                all_tracks.extend(tracks)

                city_refs = _count_city_refs(tracks, city)
                genres = _infer_genres(tracks)
                expected = CITY_GENRES.get(city, set())
                genre_fit = (sum(1 for g in genres if g in expected)/len(genres)) if genres else 0.0

                # at least 1 city mention is good; >1 is bonus, cap at 1.0
                city_ref_score = min(city_refs, 2) / 2.0
                per_leg_ctx.append(0.5*city_ref_score + 0.5*genre_fit)

            context_alignment = sum(per_leg_ctx)/len(per_leg_ctx)

            # 2) Creativity: artist & genre diversity across the whole route
            genres_all = _infer_genres(all_tracks)
            creativity = 0.5*_artist_diversity(all_tracks) + 0.5*_genre_diversity(genres_all)

            # 3) UX coherence: leg size + simple transition penalty for repeated artists across legs
            leg_len_scores = []
            prev_artists = set()
            penalty = 0.0

            for leg in playlist:
                n = len(leg.get("tracks", []))
                leg_len_scores.append(1.0 if 2 <= n <= 4 else (0.6 if n in (1,5) else 0.4))

                curr = set(str(tr.get("artist","")).lower() for tr in leg.get("tracks", []) if tr.get("artist"))
                if prev_artists and (curr & prev_artists):
                    penalty += 0.15  # small hit for repeating same artist across cities
                prev_artists = curr

            transition_score = max(0.0, 1.0 - penalty)
            ux_coherence = 0.5*(sum(leg_len_scores)/len(leg_len_scores)) + 0.5*transition_score

            aurora_score = 0.4*context_alignment + 0.3*creativity + 0.3*ux_coherence

            return {
                'task_id': task_id,
                'aurora_score': round(aurora_score, 3),
                'context_alignment': round(context_alignment, 3),
                'creativity': round(creativity, 3),
                'ux_coherence': round(ux_coherence, 3),
                'passed': aurora_score >= 0.5
            }

        except Exception as e:
            return {'task_id': task_id, 'error': f'Evaluation failed: {str(e)}', 'aurora_score': 0.0}
