from decouple import config
from openai import OpenAI

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

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=config("OPENAI_API_KEY"))
    return _client


def generate_social_post(topic: str, platform: str) -> str:
    if platform not in PLATFORM_LIMITS:
        raise ValueError(f"Unsupported platform: {platform}")

    limit = PLATFORM_LIMITS[platform]
    tone = PLATFORM_TONE[platform]

    system_prompt = (
        f"You are a social media copywriter. Write a single {platform} post about the given topic. "
        f"Tone: {tone}. "
        f"Hard limit: {limit} characters. "
        f"Return only the post text — no explanations, no quotes, no labels."
    )

    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": topic},
        ],
        max_tokens=512,
    )

    return response.choices[0].message.content.strip()
