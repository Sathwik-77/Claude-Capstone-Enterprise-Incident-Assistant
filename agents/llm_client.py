import os
from anthropic import Anthropic
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str:
    """
    Call Claude claude-sonnet-4-6 with a system and user prompt.

    Args:
        system_prompt: instructions for the agent role
        user_prompt: the actual query/task
        max_tokens: max response length

    Returns:
        Claude's response as a string
    """
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.content[0].text