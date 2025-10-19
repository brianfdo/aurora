"""
Aurora White Agent - Production

Generates code that uses AppWorld's real APIs.
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'agent': 'Aurora White Agent'})

@app.route('/solve', methods=['POST'])
def solve():
    """Generate code that uses real AppWorld APIs."""
    data = request.json
    task_id = data.get('task_id')
    route = data.get('route', {})
    
    # Generate code that uses AppWorld's real Spotify API
    code = f"""
# Task: {task_id}
playlist = []

for leg in route.get('legs', []):
    city = leg.get('city')
    
    # Use real AppWorld Spotify API
    tracks = apis.spotify.search_tracks(query=f"{{city}} music")
    
    playlist.append({{
        'leg_id': leg['leg_id'],
        'city': city,
        'tracks': tracks[:2] if isinstance(tracks, list) else []
    }})
"""
    
    return jsonify({'code': code, 'task_id': task_id})


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=9000, type=int)
    args = parser.parse_args()
    
    app.run(host=args.host, port=args.port, debug=False)
