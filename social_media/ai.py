import logging

from decouple import config
from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

PLATFORM_LIMITS = {
    "twitter": 280,
    "bluesky": 300,
    "mastodon": 500,
    "linkedin": 3000,
    "instagram": 2200,
}

PLATFORM_TONE = {
    "twitter": "punchy and direct",
    "bluesky": "conversational and friendly",
    "mastodon": "thoughtful and community-oriented",
    "linkedin": "professional and insightful",
    "instagram": "engaging and visual, with relevant hashtags",
}

class ProviderNotConfiguredError(RuntimeError):
    """Raised when an LLM provider is selected but required credentials are missing."""


_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is not None:
        return _client

    api_key = config("OPENAI_API_KEY", default="").strip()
    if not api_key:
        raise ProviderNotConfiguredError(
            "OPENAI_API_KEY is not configured. Add it to your environment or .env file."
        )

    _client = OpenAI(api_key=api_key)
    return _client


class PostOutput(BaseModel):
    content: str
    hashtags: list[str]
    character_count: int


def generate_social_post(topic: str, platform: str) -> PostOutput:
    if platform not in PLATFORM_LIMITS:
        raise ValueError(f"Unsupported platform: {platform}")

    limit = PLATFORM_LIMITS[platform]
    tone = PLATFORM_TONE[platform]

    system_prompt = (
        f"You are a social media copywriter. Write a single {platform} post about the given topic. "
        f"Tone: {tone}. "
        f"Hard limit: {limit} characters for the content field. "
        f"Return the full post text in 'content', a list of hashtags used in 'hashtags' "
        f"(each starting with #), and the character count of the content in 'character_count'."
    )

    client = _get_client()
    response = client.beta.chat.completions.parse(
        model=config("OPENAI_MODEL", default="gpt-4o-mini"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": topic},
        ],
        response_format=PostOutput,
    )

    usage = response.usage
    logger.info(
        "[%s] input=%d output=%d total=%d",
        platform,
        usage.prompt_tokens,
        usage.completion_tokens,
        usage.total_tokens,
    )

    result = response.choices[0].message.parsed
    # Always calculate character_count ourselves because model metadata can drift.
    result.character_count = len(result.content)
    if result.character_count > limit:
        result.content = result.content[:limit]
        result.character_count = limit
    return result