# I'm Learning LLM Integration in Public — Here's What I Built First

I've been building a private social media automation tool for a while now. It does real things — connects to actual platform APIs, manages OAuth tokens, schedules posts. But the LLM layer inside it? That part I bolted on without really understanding what I was doing. It works, but I couldn't confidently explain *why* it works, and I couldn't improve it without guessing.

So I built a learning project.

**[llm-social-toolkit](https://github.com/jcjudkins/llm-social-toolkit)** is a small, public Django app with one job: give it a topic or URL, get back a social media post formatted for a specific platform. That's it. No real account connections, no OAuth, no scheduler. Just the LLM layer — isolated and easy to poke at.

Here's what I learned building the first working version.

---

## The Setup

The stack is intentionally boring:

- Django 5 + Django REST Framework — familiar ground
- OpenAI SDK with `gpt-4o-mini` — cheap enough to experiment freely
- SQLite — zero configuration
- `python-decouple` — proper env var handling from day one

One endpoint: `POST /api/generate-post/` takes a `topic` and a `platform`, returns generated content. That's the whole app.

---

## The Most Important Decision: Isolate the LLM

Before writing a single line of view code, I decided where the OpenAI import would live. The answer: one file, `social_media/ai.py`, and nowhere else.

```python
# ai.py — the only file that knows about OpenAI
def generate_social_post(topic: str, platform: str) -> str:
    ...

# views.py — calls the helper, doesn't know or care about the provider
from .ai import generate_social_post
```

This sounds obvious, but it's easy to skip when you're moving fast. The benefit shows up immediately: if I want to swap OpenAI for Anthropic Claude or Groq, I change one file. The view doesn't change. The serializer doesn't change. The URL doesn't change.

It also makes the LLM logic easy to find and easy to reason about. All the prompts live in one place.

---

## What I Learned About Prompts

I've been writing prompts casually for months. Building this forced me to think more carefully.

The first thing that clicked: **system prompt vs user prompt are not interchangeable**. The system prompt is instructions. The user prompt is input. Keeping them separated makes prompts easier to tune because you can adjust the instructions without touching the input, and vice versa.

```python
messages=[
    {"role": "system", "content": f"Write a {platform} post. Tone: {tone}. Hard limit: {limit} characters. Return only the post text."},
    {"role": "user", "content": topic},
]
```

The second thing: **be explicit about what you don't want**. "Return only the post text — no explanations, no quotes, no labels" prevents the model from responding with `"Here's a great tweet for you: ..."`. Without that instruction, it does that constantly.

The third thing: character limits need to be stated as hard limits, not suggestions. "Keep it short" produces wildly inconsistent results. "Hard limit: 280 characters" is something the model can actually follow.

---

## The Five Platforms

The app supports Twitter (280), Bluesky (300), Mastodon (500), LinkedIn (3,000), and Instagram (2,200). Each has a different character limit and a different tone in the system prompt.

What's interesting is how much the tone instruction changes the output. The same topic run through "punchy and direct" (Twitter) vs "professional and insightful" (LinkedIn) produces genuinely different writing — not just different lengths. The model understands platform conventions surprisingly well.

That's the prompt engineering lesson I'll be spending the most time on: what can you encode in the system prompt, and what do you actually have to engineer?

---

## What's Next

This first version just returns a plain string. The next learning steps, in order:

1. **Structured outputs** — return JSON with `content`, `hashtags`, and `character_count` so the client gets structured data instead of raw text
2. **Token usage logging** — log what every request costs so I can track usage and experiment with cost/quality tradeoffs
3. **Provider comparison** — swap in Anthropic Claude and Groq (Llama 3), run the same prompts, compare outputs
4. **A basic web UI** — Django templates, no React, just a form and a result

The repo is public and I'm building it openly. If you're also learning LLM integration, I'd love to compare notes.

---

*Jason Judkins is the Marketing Chair for DjangoCon US and organizes Django.social Raleigh/Durham. He writes about Django and developer tooling at [judkins.dev](https://judkins.dev).*
