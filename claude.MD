# CLAUDE.md — llm-social-toolkit

Context for AI assistants working in this repo.

---

## What this project is

A public Django learning project for exploring LLM integration patterns.
Standalone companion to a private social media automation tool. The goal is
to learn LLM development openly — results get ported back to the product
once proven here.

**This repo is intentionally public. Do not add any product code, OAuth
integrations, or proprietary business logic from the automation tool.**

---

## Learning goals (in order)

1. OpenAI request/response loop — get comfortable with the basics
2. Prompt engineering — tone/format differences across platforms
3. Structured outputs — return JSON (content, hashtags, character_count)
4. Provider comparison — OpenAI vs Anthropic Claude vs Groq (Llama 3)
5. Cost tracking — log token usage per request
6. Basic web UI — Django templates, no React needed
7. Async generation — Celery task so slow API calls don't block the view

---

## Tech stack

- **Django 5.x** + Django REST Framework
- **OpenAI SDK** (`gpt-4o-mini` default — cheap for dev)
- **JWT auth** via `djangorestframework-simplejwt`
- **Celery + Redis** (added when async generation is needed)
- SQLite for local dev (zero config)
- `python-decouple` for env config

---

## Key architecture decision

The LLM call lives in `social_media/ai.py` (or equivalent), isolated from
views. Provider swaps are a one-file change. Views never import the OpenAI
SDK directly.

Pattern:
```python
# ai.py — the only file that knows about OpenAI
def generate_social_post(topic: str, platform: str) -> str:
    ...

# views.py — calls the helper, doesn't care about the provider
from .ai import generate_social_post
