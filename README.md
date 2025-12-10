# Aurora Green Agent

Deterministic green agent for evaluating white agents.

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
