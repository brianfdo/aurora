# Aurora Green Agent 🎵

A green agent for evaluating white agents on **context-aware travel playlist generation** using the AppWorld benchmark framework.

---

## 📁 Project Structure

```
aurora-green-agent/
├── agents/                      # Custom A2A implementation (Production)
│   ├── green_agent.py              Core orchestrator logic
│   ├── green_agent_a2a.py          A2A protocol server
│   ├── white_agent.py              White agent (generates playlists)
│   └── appworld_api_provider.py    Real AppWorld-style APIs
│
├── agentbeats_sdk/              # SDK-enhanced version
│   ├── aurora_agent.py             SDK-compatible agent core
│   ├── aurora_green_server.py      SDK A2A server
│   ├── appworld_api_provider.py    API provider
│   └── run_sdk.sh                  SDK runner
│
├── scripts/                     # Utilities
│   ├── run.sh                      Main runner script
│   └── kickoff.py                  Benchmark kickoff
│
├── data/                        # AppWorld benchmark data
├── aurora_tasks.json            # Aurora task definitions (3 routes)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── ROADMAP.md                   # Development roadmap
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.11+
pyenv install 3.11.13
pyenv local 3.11.13

# Install dependencies
pip install -r requirements.txt

# Download AppWorld data (required)
appworld download data
```

**Note:** The `data/` folder is not included in the repo. Use `appworld download data` to fetch it.

### Run Locally

```bash
# Terminal 1: Start green agent
./scripts/run.sh green-a2a

# Terminal 2: Start white agent
./scripts/run.sh white

# Terminal 3: Run evaluation
./scripts/run.sh kickoff
```
---

## 📊 Aurora Benchmark

**Task:** Generate context-aware travel playlists for road trips

### Routes

1. **Los Angeles → San Francisco** (3 legs)
   - Los Angeles (75°F, Sunny)
   - Santa Barbara (68°F, Cloudy)
   - San Francisco (60°F, Foggy)

2. **New York → Boston** (2 legs)
   - New York (65°F, Clear)
   - Boston (58°F, Rainy)

3. **Seattle → Portland** (2 legs)
   - Seattle (52°F, Rainy)
   - Portland (55°F, Overcast)

### Evaluation Metrics

| Metric | Weight | Description |
|--------|--------|-------------|
| **Context Alignment** | 40% | Does the playlist match the cities/route? |
| **Creativity** | 30% | Are the tracks diverse and interesting? |
| **UX Coherence** | 30% | Does the playlist flow well? |

**Passing Score:** ≥ 0.5

---

## 🎵 Real API Data

Aurora uses **26 curated tracks** across 7 cities:

**Example tracks:**
- Los Angeles: "California Love" - Tupac
- San Francisco: "San Francisco" - Scott McKenzie  
- New York: "Empire State of Mind" - Jay-Z
- Boston: "More Than a Feeling" - Boston
- Seattle: "Come As You Are" - Nirvana

See `appworld_api_provider.py` for complete track listing.

<!-- ---

## 🌐 AgentBeats Integration

### A2A Protocol Endpoints

```
GET  /.well-known/agent.json    - Agent card
GET  /a2a/health                - Health check
GET  /a2a/tasks                 - List tasks
GET  /a2a/task/<id>             - Task details
POST /a2a/evaluate              - Run evaluation
POST /a2a/reset                 - Reset state
POST /chat                      - Chat (JSON-RPC 2.0)
```

### Register on AgentBeats

```
Agent URL: https://your-ngrok-url.ngrok.io
Green Agent: ✅ ON
```

--- -->

## 🔧 Development

### Run Agents

```bash
# Custom A2A version (recommended)
./scripts/run.sh green-a2a    # Green agent (port 8001)
./scripts/run.sh white        # White agent (port 9000)

# SDK version (alternative)
cd agentbeats_sdk && ./run_sdk.sh
```

### Evaluation Flow

1. **White Agent** generates code:
   ```python
   for city in route:
       tracks = apis.spotify.search_tracks(f"{city} music")
       playlist.append({'city': city, 'tracks': tracks})
   ```

2. **Green Agent** executes the code with real APIs

3. **Green Agent** evaluates the playlist and returns scores

---

## 📈 Current Status

- ✅ Green agent orchestrates evaluation
- ✅ White agent generates playlists  
- ✅ Real AppWorld-style APIs (26 tracks)
- ✅ 3 routes with weather data
- ✅ A2A protocol compliant
- ✅ AgentBeats registered

**Current Scores:** 0.67 (placeholder - shows system works)

---

## 🗺️ Roadmap

See `ROADMAP.md` for future development plans:

### Phase 2: Smart Scoring (Next)
- Analyze actual playlist quality
- Context matching, artist diversity, flow analysis
- Variable scores (0.3 to 0.9)

### Phase 3: Dynamic Routes
- Real-time route generation (Google Maps API)
- Current weather data (OpenWeather API)
- Points of interest along route

<!-- ---

## 🛠️ Technical Stack

- **Language:** Python 3.11.13
- **Framework:** Flask (A2A server)
- **APIs:** AppWorld-style (Spotify)
- **Protocol:** A2A (Agent-to-Agent)
- **Platform:** AgentBeats

--- -->

## 📝 License

MIT

---

**Built for context-aware travel playlists** 🎵✨
