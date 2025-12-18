"""
Legacy Flask-based Aurora Green Agent Server

This file exists ONLY for legacy / compatibility use.
It is intentionally separated from:
- Typer CLI
- agentbeats run_ctrl
"""

import sys
from pathlib import Path
from flask import Flask, request, jsonify

# --- Path setup ---
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "src"))

# --- Imports from your codebase ---
from src.green_agent.agent import AuroraGreenAgent
from src.my_util.my_a2a import create_a2a_server, create_agent_card


def create_green_agent_server(host: str = "0.0.0.0", port: int = 8001):
    """
    Create a Flask-based A2A server for the Aurora Green Agent.
    """

    green_agent = AuroraGreenAgent()

    app: Flask = create_a2a_server(
        agent_name="Aurora Green Agent",
        agent_type="green",
        description=(
            "Deterministic evaluator for white agents on "
            "context-aware travel playlist generation"
        ),
    )

    # ---------------------------
    # A2A: Agent Card
    # ---------------------------
    @app.route("/.well-known/agent-card.json", methods=["GET"])
    @app.route("/.well-known/agent.json", methods=["GET"])
    def agent_card():
        base_url = request.url_root.rstrip("/")

        # Respect reverse proxies / tunnels
        if (
            request.headers.get("X-Forwarded-Proto") == "https"
            or request.scheme == "https"
        ):
            base_url = base_url.replace("http://", "https://")

        card = create_agent_card(
            app,
            base_url,
            capabilities={
                "task_listing": True,
                "task_evaluation": True,
                "appworld_execution": True,
            },
        )

        card.update(
            {
                "preferredTransport": "JSONRPC",
                "protocolVersion": "1.0",
                "skills": [
                    {
                        "id": "aurora-playlist-eval",
                        "name": "evaluate_playlist_generation",
                        "description": (
                            "Evaluate white agents on context-aware "
                            "travel playlist generation"
                        ),
                        "tags": [
                            "music",
                            "playlist",
                            "evaluation",
                            "aurora",
                        ],
                    }
                ],
            }
        )

        return jsonify(card)

    # ---------------------------
    # A2A: Health
    # ---------------------------
    @app.route("/a2a/health", methods=["GET"])
    def a2a_health():
        return jsonify(
            {
                "status": "healthy",
                "protocol": "a2a",
                "version": "1.0",
            }
        )

    # ---------------------------
    # A2A: Tasks
    # ---------------------------
    @app.route("/a2a/tasks", methods=["GET"])
    def a2a_list_tasks():
        return jsonify(
            {
                "protocol": "a2a",
                "tasks": green_agent.list_tasks(),
                "total": len(green_agent.tasks),
            }
        )

    @app.route("/a2a/task/<task_id>", methods=["GET"])
    def a2a_get_task(task_id: str):
        task = green_agent.get_task(task_id)
        if not task:
            return (
                jsonify(
                    {
                        "protocol": "a2a",
                        "error": f"Task {task_id} not found",
                    }
                ),
                404,
            )

        return jsonify(
            {
                "protocol": "a2a",
                "task": task,
            }
        )

    # ---------------------------
    # A2A: Evaluation
    # ---------------------------
    @app.route("/a2a/evaluate", methods=["POST"])
    def a2a_evaluate():
        data = request.json or {}

        white_agent_url = data.get("white_agent_url")
        if not white_agent_url:
            return (
                jsonify(
                    {
                        "protocol": "a2a",
                        "error": "white_agent_url is required",
                    }
                ),
                400,
            )

        task_ids = data.get("task_ids") or [
            t["id"] for t in green_agent.tasks
        ]

        results = green_agent.execute_benchmark(
            task_ids=task_ids,
            white_agent_url=white_agent_url,
        )

        return jsonify(
            {
                "protocol": "a2a",
                "status": "completed",
                "results": results,
            }
        )

    # ---------------------------
    # Chat fallback
    # ---------------------------
    @app.route("/chat", methods=["POST"])
    def chat():
        import uuid

        return jsonify(
            {
                "jsonrpc": "2.0",
                "result": {
                    "messageId": str(uuid.uuid4()),
                    "role": "agent",
                    "parts": [
                        {
                            "type": "text",
                            "text": "Aurora Green Agent ready!",
                        }
                    ],
                },
                "id": request.json.get("id") if request.json else None,
            }
        )

    return app


# ---------------------------
# Standalone execution
# ---------------------------
if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int)
    args = parser.parse_args()

    # ✅ PORT precedence: ENV > CLI > default
    port = (
        int(os.environ.get("PORT"))
        if os.environ.get("PORT")
        else args.port or 8001
    )

    app = create_green_agent_server(
        host=args.host,
        port=port,
    )

    print("🎵 Aurora Green Agent (Legacy Flask)")
    print(f"✓ Listening on {args.host}:{port}")

    app.run(host=args.host, port=port, debug=False)
