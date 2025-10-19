# Aurora Green Agent - Development Roadmap 🗺️

## ✅ Phase 1: MVP (COMPLETE)

**Status:** Production-ready demo ✅

### What's Working:
- ✅ Green agent orchestrates evaluation
- ✅ White agent generates code to create playlists
- ✅ Real AppWorld-style APIs (26 curated tracks)
- ✅ 3 hardcoded routes with static weather
- ✅ Basic scoring system (0.67 for valid playlists)
- ✅ A2A protocol compliance
- ✅ AgentBeats integration
- ✅ Demo tools (`quick_test.sh`, `demo_evaluation.py`)

**Demo Command:**
```bash
./quick_test.sh aurora_001
```

**Current Score:** 0.67 (placeholder - shows system works)

---

## 🚀 Phase 2: Smart Scoring System

**Goal:** Replace placeholder scoring with actual playlist analysis

### Improvements:

#### 1. Context Alignment (40% weight)
**Currently:** Fixed 0.7 if playlist exists  
**Target:** Analyze actual context matching

```python
def calculate_context_alignment(playlist, route):
    """
    Score based on:
    - Do track titles/artists mention the city?
    - Do genres match city culture?
    - Are tracks era-appropriate for the city?
    """
    score = 0.0
    
    for leg in playlist:
        city = leg['city']
        tracks = leg['tracks']
        
        # Check city mentions in titles/artists
        city_mentions = count_city_references(tracks, city)
        
        # Check genre appropriateness
        genre_match = evaluate_genre_fit(tracks, city)
        
        # Aggregate
        score += (city_mentions * 0.5 + genre_match * 0.5)
    
    return score / len(playlist)
```

**Examples:**
- "California Love" for Los Angeles → High score ✅
- "Empire State of Mind" for NYC → High score ✅
- Random pop song for Seattle → Lower score

#### 2. Creativity (30% weight)
**Currently:** Fixed 0.6 if playlist exists  
**Target:** Measure diversity and uniqueness

```python
def calculate_creativity(playlist):
    """
    Score based on:
    - Artist diversity (no repeats)
    - Genre variety
    - Mix of popular and obscure tracks
    - Temporal variety (different eras)
    """
    all_tracks = flatten_playlist(playlist)
    
    # Check for repeated artists
    unique_artists = len(set([t['artist'] for t in all_tracks]))
    artist_diversity = unique_artists / len(all_tracks)
    
    # Check genre variety
    genres = infer_genres(all_tracks)
    genre_diversity = len(set(genres)) / len(all_tracks)
    
    return (artist_diversity * 0.5 + genre_diversity * 0.5)
```

**Examples:**
- All tracks from different artists → High score ✅
- Same artist repeated → Lower score
- Mix of rock, hip-hop, indie → High score ✅

#### 3. UX Coherence (30% weight)
**Currently:** Fixed 0.7 if playlist exists  
**Target:** Evaluate flow and transitions

```python
def calculate_ux_coherence(playlist):
    """
    Score based on:
    - Smooth energy transitions
    - Consistent vibe progression
    - No jarring genre switches
    - Good length per city (2-3 tracks)
    """
    scores = []
    
    # Check track count per city
    for leg in playlist:
        track_count = len(leg['tracks'])
        optimal = 2 <= track_count <= 4
        scores.append(1.0 if optimal else 0.5)
    
    # Check transitions between cities
    transition_score = evaluate_transitions(playlist)
    
    return (sum(scores) / len(scores) * 0.5 + transition_score * 0.5)
```

**Examples:**
- Smooth energy flow → High score ✅
- Good track count (2-3 per city) → High score ✅
- Abrupt genre changes → Lower score

### Implementation Tasks:
- [ ] Parse playlist JSON structure
- [ ] Implement city reference detection
- [ ] Add genre inference (keyword-based or API)
- [ ] Create artist deduplication check
- [ ] Build transition analyzer
- [ ] Update `_evaluate_playlist()` in both green agents
- [ ] Test with different white agent strategies

**Expected Outcome:** Scores vary from 0.3 to 0.9 based on actual quality

---

## 🌍 Phase 3: Dynamic Route Generation

**Goal:** Transform from static routes to dynamic, data-driven route planning

### Architecture Changes:

#### Current Flow:
```
Static Tasks → Green Agent → White Agent → Evaluation
(hardcoded)      (executes)    (generates)   (scores)
```

#### New Flow:
```
Start + End → Route API → Cities + Weather → Green Agent → White Agent → Evaluation
  (input)    (dynamic)     (real data)       (executes)     (generates)   (scores)
```

### Components to Add:

#### 1. Route Planning API
**Options:**
- Google Maps Directions API
- Mapbox Directions API
- OpenRouteService API
- TomTom Routing API

**What we need:**
```python
def get_route(start: str, end: str) -> Dict:
    """
    Input: "Los Angeles" → "San Francisco"
    
    Output:
    {
        'start': 'Los Angeles, CA',
        'end': 'San Francisco, CA',
        'distance': 383.2,  # miles
        'duration': 5.8,    # hours
        'waypoints': [
            {'city': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437},
            {'city': 'Santa Barbara', 'lat': 34.4208, 'lon': -119.6982},
            {'city': 'San Luis Obispo', 'lat': 35.2828, 'lon': -120.6596},
            {'city': 'San Francisco', 'lat': 37.7749, 'lon': -122.4194}
        ]
    }
    """
```

#### 2. Points of Interest API
**Options:**
- Google Places API
- Foursquare Places API
- Yelp Fusion API
- TripAdvisor API

**What we need:**
```python
def get_poi_along_route(waypoints: List[Dict]) -> List[Dict]:
    """
    For each waypoint, find nearby points of interest
    
    Output:
    [
        {
            'city': 'Santa Barbara',
            'poi': [
                {'name': 'Santa Barbara Mission', 'type': 'landmark'},
                {'name': 'Stearns Wharf', 'type': 'attraction'},
                {'name': 'State Street', 'type': 'shopping'}
            ]
        },
        ...
    ]
    """
```

#### 3. Weather API
**Options:**
- OpenWeatherMap API (free tier: 1000 calls/day)
- WeatherAPI.com (free tier: 1M calls/month)
- Weatherstack API
- Tomorrow.io API

**What we need:**
```python
def get_weather(lat: float, lon: float) -> Dict:
    """
    Input: Coordinates
    
    Output:
    {
        'conditions': 'Partly Cloudy',
        'temp': 68,  # Fahrenheit
        'temp_c': 20,  # Celsius
        'humidity': 65,
        'wind_speed': 12,
        'description': 'Comfortable weather for driving'
    }
    """
```

### Implementation:

#### New `RouteGenerator` Class:
```python
class RouteGenerator:
    """Dynamically generates routes with real data."""
    
    def __init__(self, maps_api_key: str, weather_api_key: str):
        self.maps_api = MapsClient(maps_api_key)
        self.weather_api = WeatherClient(weather_api_key)
    
    def create_route(self, start: str, end: str) -> Dict:
        """
        Generate a complete route with cities, POIs, and weather.
        """
        # Step 1: Get route
        route_data = self.maps_api.get_directions(start, end)
        waypoints = self._extract_major_cities(route_data)
        
        # Step 2: Get POIs for each waypoint
        for waypoint in waypoints:
            waypoint['poi'] = self.maps_api.get_nearby_places(
                waypoint['lat'], 
                waypoint['lon'],
                radius=10000  # 10km
            )
        
        # Step 3: Get current weather
        for waypoint in waypoints:
            waypoint['weather'] = self.weather_api.get_current(
                waypoint['lat'],
                waypoint['lon']
            )
        
        return {
            'start': start,
            'end': end,
            'legs': waypoints,
            'total_distance': route_data['distance'],
            'estimated_duration': route_data['duration']
        }
```

#### Updated Green Agent:
```python
class AuroraGreenAgent:
    def __init__(self):
        self.route_generator = RouteGenerator(
            maps_api_key=os.getenv('MAPS_API_KEY'),
            weather_api_key=os.getenv('WEATHER_API_KEY')
        )
    
    def create_task(self, start: str, end: str) -> Dict:
        """Generate a task dynamically from start/end."""
        route = self.route_generator.create_route(start, end)
        
        return {
            'id': f'aurora_{uuid.uuid4().hex[:8]}',
            'route': route,
            'instruction': f"Create a travel playlist from {start} to {end}"
        }
```

### Environment Setup:
```bash
# .env file
MAPS_API_KEY=your_google_maps_key
WEATHER_API_KEY=your_openweather_key
POI_API_KEY=your_places_key  # optional
```

### Implementation Tasks:
- [ ] Choose route API provider
- [ ] Choose weather API provider
- [ ] Implement `RouteGenerator` class
- [ ] Add API key management
- [ ] Update green agent to use dynamic routes
- [ ] Add error handling for API failures
- [ ] Cache results to minimize API calls
- [ ] Test with various start/end combinations

**Example Usage:**
```python
# Instead of hardcoded aurora_001, aurora_002...
task = green_agent.create_task(
    start="Seattle, WA",
    end="Portland, OR"
)
# Returns real route with current weather!
```

---

## 📊 Success Metrics

### Phase 2 (Smart Scoring):
- ✅ Scores vary based on actual playlist quality
- ✅ Can distinguish good vs bad playlists
- ✅ Scores range from 0.3-0.9 (not all 0.67)

### Phase 3 (Dynamic Routes):
- ✅ Generate route from any start/end in USA
- ✅ Real-time weather data
- ✅ 5-10 waypoints per route
- ✅ POIs for context
- ✅ API calls < 1000/day (within free tier)

---

## 🔧 Technical Considerations

### API Cost Management:
- Use free tiers where possible
- Cache route/weather data (valid for 1-24 hours)
- Rate limiting
- Fallback to static data if API fails

### Performance:
- Async API calls (fetch route + weather in parallel)
- Database for caching popular routes
- Pre-generate common routes

### Scalability:
- Support international routes (not just USA)
- Multiple route options (scenic vs fast)
- Different vehicle types (car, bike, walking)

---

## 🎯 Priority Order

1. **Phase 2 (Smart Scoring)** - 1-2 days
   - Most immediate value
   - No external dependencies
   - Shows real evaluation quality

2. **Phase 3 (Dynamic Routes)** - 3-5 days
   - Requires API keys
   - More complex integration
   - Transforms the product

---

## 📝 Notes

**Current Status:** Ready for Phase 2 implementation

**MVP is demo-ready** with:
- Working end-to-end flow
- Real track generation
- Clean demo tools
- AgentBeats integration ✅

**Next Session:** Start implementing smart scoring system!

---

