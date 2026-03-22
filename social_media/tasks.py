from celery import shared_task

from .ai import generate_social_post


@shared_task
def generate_post_task(topic: str, platform: str) -> dict:
    result = generate_social_post(topic, platform)
    return result.model_dump()
