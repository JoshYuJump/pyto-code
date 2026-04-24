"""PyTo Code - Code Agent with Pydantic-AI."""

import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent, Tool
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


def get_model() -> str:
    """Get the model from environment variables."""
    # Claude Code style env vars
    if os.environ.get("ANTHROPIC_DEFAULT_OPUS_MODEL"):
        return os.environ.get("ANTHROPIC_DEFAULT_OPUS_MODEL")
    if os.environ.get("ANTHROPIC_DEFAULT_SONNET_MODEL"):
        return os.environ.get("ANTHROPIC_DEFAULT_SONNET_MODEL")
    if os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL"):
        return os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL")
    return os.environ.get("PYTO_MODEL", "claude-sonnet-4-20250514")


def get_api_key() -> str:
    """Get the API key from environment variables."""
    # Claude Code style env var
    return os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY")


def get_base_url() -> str:
    """Get the base URL from environment variables."""
    return os.environ.get("ANTHROPIC_BASE_URL")


def run_code(code: str) -> str:
    """Execute Python code and return the output."""
    result = subprocess.run(
        ["python", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout
    if result.stderr:
        output += f"\nSTDERR: {result.stderr}"
    if not output:
        output = "(no output)"
    return output


def create_agent(model: str = None) -> Agent:
    """Create a PyTo Code agent with code execution capability."""
    model = model or get_model()
    api_key = get_api_key()

    # Build provider with optional base_url
    base_url = get_base_url()
    if base_url:
        provider = AnthropicProvider(api_key=api_key, base_url=base_url)
    else:
        provider = AnthropicProvider(api_key=api_key)

    anthropic_model = AnthropicModel(model, provider=provider)
    agent = Agent(
        anthropic_model,
        tools=[Tool(run_code)],
    )
    return agent


async def run(prompt: str, model: str = None) -> str:
    """Run the agent with a prompt and return the result."""
    agent = create_agent(model)
    result = await agent.run(prompt)
    return result.output
