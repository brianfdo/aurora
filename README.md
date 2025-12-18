# Aurora 

## Overview
Aurora is a deterministic evaluation benchmark inspired by AppWorld, designed to evaluate white agents that generate travel playlists. A white agent produces executable playlist-generation code, and the green agent evaluates the output using deterministic, rule-based metrics without relying on LLMs or external services.

## Repository Structure
- `src/white_agent/` — Deterministic white agent that generates playlist code.
- `src/green_agent/` — Aurora green agent that executes and evaluates white agent outputs.
- `aurora_tasks.json` — Fixed benchmark task definitions (routes, cities, weather).
- `src/my_util/appworld_api.py` — Local sandboxed APIs used during evaluation.
- `main.py` — Entry point for running agents.

## Evaluation Metrics

Playlists are evaluated deterministically using the following metrics:

- Context Alignment (30%)
- Creativity / Diversity (25%)
- UX Coherence (20%)
- Weather & Time Alignment (15%)
- Transition Smoothness (10%)

Metric weights are fixed in code to ensure reproducibility. Aggregate statistics (min/max/mean) are computed across runs to detect instability or score drift.

## Run Agents

### Install Dependencies
```bash
uv sync
# or
pip install -r requirements.txt
```

### Run Green Agent
```bash
export ROLE=green
export AGENT_PORT=8010
python main.py run
```

### Run White Agent (separate terminal)
```bash
python -m src.white_agent.agent --port 9000
```

### Output
- Green agent runs on `http://localhost:8010`
- White agent runs on `http://localhost:9000`
- Agent cards available at `/.well-known/agent-card.json`
- Green agent communicates with white agent via A2A protocol

### Optional: Public URL for AgentBeats
```bash
# Start Cloudflare tunnel
./cloudflared tunnel --url http://localhost:8010

# Update .env with the URL shown
export CLOUDRUN_HOST=your-url.trycloudflare.com
export HTTPS_ENABLED=true

# Restart green agent
```
