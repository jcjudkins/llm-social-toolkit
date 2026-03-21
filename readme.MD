# llm-social-toolkit

> **Learning LLM integration patterns through a real use case — generating social media posts.**

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-green?logo=django&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Learning%20Project-orange)

Built in public by [Jason Judkins](https://judkins.dev) · [@jjudkins77](https://twitter.com/jjudkins77) · [Mastodon](https://fosstodon.org/@jjudkins) · [LinkedIn](https://www.linkedin.com/in/jasoncjudkins/) · [Blog](https://judkins.dev/blog)

---

## What this is

A public Django project for learning and experimenting with LLM APIs. The use case is simple: give it a topic or URL, get back a platform-appropriate social media post.

This is a learning repo, not a production app. No OAuth, no real social accounts, no platform API clients. Just the LLM layer — isolated and easy to poke at.

Proven patterns here get ported back into a [private social media automation tool](https://judkins.dev/blog) once they're solid.

---

## Learning goals

1. **OpenAI request/response loop** — get comfortable with the basics
2. **Prompt engineering** — tone and format differences across platforms
3. **Structured outputs** — return JSON (`content`, `hashtags`, `character_count`)
4. **Provider comparison** — OpenAI vs Anthropic Claude vs Groq (Llama 3)
5. **Cost tracking** — log token usage per request
6. **Basic web UI** — Django templates, no React needed
7. **Async generation** — Celery task so slow API calls don't block the view

---

## Tech stack

| Layer | Choice |
|---|---|
| Framework | Django 5.x + Django REST Framework |
| LLM | OpenAI SDK (`gpt-4o-mini` default — cheap for dev) |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | SQLite (zero config) |
| Config | `python-decouple` |

---

## Local setup

```bash
# 1. Clone + virtualenv
git clone https://github.com/jcjudkins/llm-social-toolkit.git
cd llm-social-toolkit
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# 3. Database
python manage.py migrate

# 4. Run
python manage.py runserver
```

### Environment variables

```env
SECRET_KEY=        # Django secret key
OPENAI_API_KEY=    # platform.openai.com/api-keys
```

---

## API

### `POST /api/generate-post/`

**Request:**

```json
{
  "topic": "https://djangoproject.com",
  "platform": "twitter"
}
```

**Response:**

```json
{
  "content": "Django 5.1 is here...",
  "platform": "twitter"
}
```

### Supported platforms

| Platform | Character limit |
|---|---:|
| Twitter | 280 |
| Bluesky | 300 |
| Mastodon | 500 |
| LinkedIn | 3,000 |
| Instagram | 2,200 |

---

## Architecture

The LLM call lives in `social_media/ai.py`, isolated from views. Provider swaps are a one-file change.

```python
# ai.py — the only file that knows about OpenAI
def generate_social_post(topic: str, platform: str) -> str:
    ...

# views.py — calls the helper, doesn't care about the provider
from .ai import generate_social_post
```

---

## What this is NOT

- ❌ Not a production app
- ❌ Not connected to real social media accounts
- ❌ No encrypted token storage, no OAuth
- ❌ No platform API clients

Those live in the private automation tool. This repo is for LLM patterns only.

---

## Author

**Jason Judkins** — DjangoCon US Marketing Chair, Django.social Raleigh/Durham organizer

- 🌐 [judkins.dev](https://judkins.dev)
- 🐦 [@jjudkins77](https://twitter.com/jjudkins77)
- 🐘 [@jjudkins@fosstodon.org](https://fosstodon.org/@jjudkins)

---

## License

[MIT](LICENSE)
