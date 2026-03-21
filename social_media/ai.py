from decouple import config
from openai import OpenAI
from pydantic import BaseModel

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

_client = OpenAI(api_key=config("OPENAI_API_KEY"))


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

    response = _client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": topic},
        ],
        response_format=PostOutput,
        max_tokens=512,
    )

    result = response.choices[0].message.parsed
    # Always calculate character_count ourselves — models sometimes get it wrong
    result.character_count = len(result.content)
    if result.character_count > limit:
        result.content = result.content[:limit]
        result.character_count = limit
    return result
