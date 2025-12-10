# Aurora Green Agent - AgentBeats Setup

This guide shows how to run the Aurora green agent using the `agentbeats run_ctrl` command, following the tau-bench format.

## Important Notes on Environment Variables

- **`CLOUDRUN_HOST`**: Specify agent URL with the cloudflared forwarded domain name (e.g., `resolution-swaziland-synthesis-pot.trycloudflare.com`)
- **`HTTPS_ENABLED`**: Set to `true` to provide agent URL starting with "https" (required for Cloudflare tunnel)
- **`ROLE`**: Specific to tau-bench repo (for having two agents in one repo). **Do not run `agentbeats run_ctrl` twice under the same working directory**

## Prerequisites

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. **Sync dependencies**:
   ```bash
   cd /Users/fern/Desktop/python_projects/aurora-green-agent
   uv sync
   ```

## Running with agentbeats run_ctrl

### Step 1: Get Cloudflare Tunnel URL

In a separate terminal:
```bash
./cloudflared tunnel --url http://localhost:8001
```

Copy the domain name (e.g., `resolution-swaziland-synthesis-pot.trycloudflare.com`)

### Step 2: Set Environment Variables

```bash
export ROLE=green
export CLOUDRUN_HOST=resolution-swaziland-synthesis-pot.trycloudflare.com
export HTTPS_ENABLED=true
export AGENT_HOST=0.0.0.0
export AGENT_PORT=8001
```

Or create a `.env` file:
```bash
CLOUDRUN_HOST=resolution-swaziland-synthesis-pot.trycloudflare.com
HTTPS_ENABLED=true
AGENT_HOST=0.0.0.0
AGENT_PORT=8001
ROLE=green
```

### Step 3: Run Agent

```bash
source .venv/bin/activate
agentbeats run_ctrl
```

You should see: `Uvicorn running on http://0.0.0.0:8001`

## Alternative: Direct Execution (without agentbeats)

```bash
source .venv/bin/activate
export CLOUDRUN_HOST=your-cloudflare-domain.trycloudflare.com
export HTTPS_ENABLED=true
python3 main.py --port 8001
```

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `CLOUDRUN_HOST` | Cloudflared forwarded domain name | Yes (for Cloudflare tunnel) |
| `HTTPS_ENABLED` | Set to `true` for HTTPS URLs | Yes (for Cloudflare tunnel) |
| `ROLE` | Set to `green` for green agent | Yes (for agentbeats run_ctrl) |
| `AGENT_HOST` | Host to bind to | No (default: 0.0.0.0) |
| `AGENT_PORT` | Port to listen on | No (default: 8001) |

## Testing

```bash
# Test agent card
curl http://localhost:8001/.well-known/agent-card.json

# Verify URL uses HTTPS
curl -s http://localhost:8001/.well-known/agent-card.json | grep -o '"url":"[^"]*"'
```

## Important Warnings

⚠️ **Do not run `agentbeats run_ctrl` twice in the same working directory** - This is for repos that have both green and white agents. Since Aurora is just the green agent, you only need to run it once.
