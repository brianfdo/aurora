"""
Aurora Green Agent - Main Entry Point

Supports:
- Typer CLI
- agentbeats run_ctrl
"""

import sys
from pathlib import Path
import typer
from pydantic_settings import BaseSettings, SettingsConfigDict

# Add src to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "src"))

class AuroraSettings(BaseSettings):
    role: str = "unspecified"
    host: str = "0.0.0.0"
    agent_port: int = 8001

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

app = typer.Typer(help="Aurora Green Agent")

@app.command()
def green():
    """Start green agent explicitly."""
    from src.green_agent import start_green_agent
    settings = AuroraSettings()
    start_green_agent(
        agent_name="tau_green_agent",
        host=settings.host,
        port=settings.agent_port,
    )

@app.command()
def run():
    """Run agent based on ROLE (agentbeats-compatible)."""
    settings = AuroraSettings()

    if settings.role != "green":
        raise ValueError(f"Unknown role: {settings.role}")

    from src.green_agent import start_green_agent
    start_green_agent(
        agent_name="tau_green_agent",
        host=settings.host,
        port=settings.agent_port,
    )

if __name__ == "__main__":
    settings = AuroraSettings()

    if settings.role == "green":
        from src.green_agent import start_green_agent
        start_green_agent(
            agent_name="tau_green_agent",
            host=settings.host,
            port=settings.agent_port,
        )
    else:
        app()
