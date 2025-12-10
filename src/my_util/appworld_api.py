"""
AppWorld API Provider - Deterministic Mock APIs

Provides deterministic AppWorld-style APIs (Spotify, Phone, etc.) 
for white agent code execution.
"""

from typing import Dict, Any, List


class AppWorldAPIProvider:
    """
    Provides AppWorld-style APIs for code execution.
    
    All APIs are deterministic - same inputs always produce same outputs.
    """
    
    def __init__(self):
        """Initialize AppWorld API provider."""
        self.available_apps = ['spotify', 'phone', 'supervisor']
    
    def get_api_namespace(self, route_data: Dict = None) -> 'AppWorldAPINamespace':
        """
        Get an API namespace object for code execution.
        
        Args:
            route_data: Optional route data to contextualize APIs
            
        Returns:
            APINamespace object with .spotify, .phone, etc. attributes
        """
        return AppWorldAPINamespace(route_data)


class AppWorldAPINamespace:
    """Namespace providing AppWorld-style APIs."""
    
    def __init__(self, route_data: Dict = None):
        self.route_data = route_data or {}
        
        # Initialize APIs with AppWorld-style signatures
        self.spotify = SpotifyAPI(route_data)
        self.phone = PhoneAPI(route_data)
        self.supervisor = SupervisorAPI(route_data)


class SpotifyAPI:
    """
    Deterministic Spotify API.
    
    Same query always returns same results (deterministic).
    """
    
    # Curated music database for different queries
    MUSIC_DATABASE = {
        'los angeles': [
            {'title': 'California Love', 'artist': 'Tupac', 'id': 'spotify_1'},
            {'title': 'Going to California', 'artist': 'Led Zeppelin', 'id': 'spotify_2'},
            {'title': 'Hotel California', 'artist': 'Eagles', 'id': 'spotify_3'},
            {'title': 'West Coast', 'artist': 'Lana Del Rey', 'id': 'spotify_4'},
            {'title': 'Dani California', 'artist': 'Red Hot Chili Peppers', 'id': 'spotify_5'},
        ],
        'san francisco': [
            {'title': 'San Francisco', 'artist': 'Scott McKenzie', 'id': 'spotify_6'},
            {'title': 'Lights', 'artist': 'Journey', 'id': 'spotify_7'},
            {'title': 'Golden Gate', 'artist': 'Rancid', 'id': 'spotify_8'},
            {'title': 'Bay Area', 'artist': 'E-40', 'id': 'spotify_9'},
        ],
        'new york': [
            {'title': 'Empire State of Mind', 'artist': 'Jay-Z ft. Alicia Keys', 'id': 'spotify_10'},
            {'title': 'New York State of Mind', 'artist': 'Billy Joel', 'id': 'spotify_11'},
            {'title': 'NYC', 'artist': 'The Chainsmokers', 'id': 'spotify_12'},
            {'title': 'Concrete Jungle', 'artist': 'Alicia Keys', 'id': 'spotify_13'},
        ],
        'boston': [
            {'title': 'More Than a Feeling', 'artist': 'Boston', 'id': 'spotify_14'},
            {'title': 'Shipping Up to Boston', 'artist': 'Dropkick Murphys', 'id': 'spotify_15'},
            {'title': 'Tessie', 'artist': 'Dropkick Murphys', 'id': 'spotify_16'},
        ],
        'seattle': [
            {'title': 'Come As You Are', 'artist': 'Nirvana', 'id': 'spotify_17'},
            {'title': 'Black Hole Sun', 'artist': 'Soundgarden', 'id': 'spotify_18'},
            {'title': 'Alive', 'artist': 'Pearl Jam', 'id': 'spotify_19'},
            {'title': 'Seattle', 'artist': 'Public Image Ltd', 'id': 'spotify_20'},
        ],
        'portland': [
            {'title': 'Portland', 'artist': 'The Replacements', 'id': 'spotify_21'},
            {'title': 'Keep Portland Weird', 'artist': 'Various Artists', 'id': 'spotify_22'},
            {'title': 'Pacific Northwest', 'artist': 'Local Natives', 'id': 'spotify_23'},
        ],
        'santa barbara': [
            {'title': 'Surfin USA', 'artist': 'The Beach Boys', 'id': 'spotify_24'},
            {'title': 'Santa Barbara', 'artist': 'The Mamas & The Papas', 'id': 'spotify_25'},
            {'title': 'California Girls', 'artist': 'The Beach Boys', 'id': 'spotify_26'},
        ]
    }
    
    def __init__(self, route_data: Dict = None):
        self.route_data = route_data or {}
    
    def search_tracks(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for tracks by query (deterministic).
        
        Same query always returns same results.
        
        Args:
            query: Search query (artist, genre, city, mood, etc.)
            limit: Maximum number of tracks to return (default: 5)
            
        Returns:
            List of track dictionaries with 'title', 'artist', 'id'
        """
        query_lower = query.lower()
        
        # Try to find relevant tracks based on query (deterministic)
        results = []
        
        # Check if query matches a city in our database
        for city, tracks in self.MUSIC_DATABASE.items():
            if city in query_lower or query_lower in city:
                results.extend(tracks[:limit])
                break
        
        # If no city match, search for keywords
        if not results:
            for city, tracks in self.MUSIC_DATABASE.items():
                for track in tracks:
                    if (query_lower in track['title'].lower() or 
                        query_lower in track['artist'].lower()):
                        results.append(track)
                        if len(results) >= limit:
                            break
                if len(results) >= limit:
                    break
        
        # If still no results, return generic tracks (deterministic based on query)
        if not results:
            results = [
                {
                    'title': f'Track {i+1} for {query[:30]}',
                    'artist': f'Artist {i+1}',
                    'id': f'spotify_gen_{hash(query) % 10000}_{i}'
                }
                for i in range(min(limit, 3))
            ]
        
        # Return limited results (deterministic order)
        return results[:limit]


class PhoneAPI:
    """AppWorld-style Phone API (deterministic)."""
    
    CONTACTS = [
        {'name': 'Alex Chen', 'location': 'San Francisco', 'phone': '415-555-0101'},
        {'name': 'Jordan Smith', 'location': 'Los Angeles', 'phone': '310-555-0202'},
        {'name': 'Taylor Park', 'location': 'Seattle', 'phone': '206-555-0303'},
        {'name': 'Morgan Lee', 'location': 'Portland', 'phone': '503-555-0404'},
        {'name': 'Casey Rivera', 'location': 'Boston', 'phone': '617-555-0505'},
        {'name': 'Riley Kim', 'location': 'New York', 'phone': '212-555-0606'},
    ]
    
    def __init__(self, route_data: Dict = None):
        self.route_data = route_data or {}
    
    def get_contacts(self) -> List[Dict]:
        """Get all contacts (deterministic)."""
        return self.CONTACTS.copy()
    
    def get_contacts_by_location(self, location: str) -> List[Dict]:
        """Get contacts filtered by location (deterministic)."""
        location_lower = location.lower()
        return [
            contact.copy() for contact in self.CONTACTS
            if location_lower in contact['location'].lower()
        ]


class SupervisorAPI:
    """AppWorld-style Supervisor API (deterministic)."""
    
    def __init__(self, route_data: Dict = None):
        self.route_data = route_data or {}
    
    def get_current_context(self) -> Dict:
        """Get current execution context (deterministic)."""
        return {
            'environment': 'aurora',
            'benchmark': 'context-aware-travel-playlists',
            'route': self.route_data.copy(),
            'available_apis': ['spotify', 'phone', 'supervisor']
        }


def create_api_provider() -> AppWorldAPIProvider:
    """Factory function to create API provider."""
    return AppWorldAPIProvider()


