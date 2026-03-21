# LLM Integration — Learning Notes

Personal reference notes from building llm-social-toolkit.

---

## OpenAI SDK Basics

### Client initialization

```python
from openai import OpenAI
client = OpenAI(api_key="your-key")
```

Lazy-initialize the client (create it once, reuse it). Avoid creating a new client on every request — it's wasteful and slow.

### Chat completions request

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a copywriter..."},
        {"role": "user", "content": "Write a post about Django"},
    ],
    max_tokens=512,
)
content = response.choices[0].message.content.strip()
```

- `messages` is a list of dicts — roles are `system`, `user`, `assistant`
- `system` sets the behavior/persona; `user` is the actual prompt
- Response lives at `response.choices[0].message.content`
- Always `.strip()` the output — models sometimes add leading/trailing whitespace

### Model choice for dev

Use `gpt-4o-mini` while experimenting. It's dramatically cheaper than `gpt-4o` and fast enough to give quick feedback loops. Switch to a stronger model when you need higher quality output or are testing prompts for production.

---

## Prompt Engineering

### System prompt vs user prompt

Think of the **system prompt** as instructions to the model and the **user prompt** as the actual input. Keep them separated — don't cram everything into the user message.

```python
# Good — system sets the rules, user provides the input
{"role": "system", "content": "Write a tweet. Max 280 chars. Punchy tone."}
{"role": "user", "content": "Django 5 was released today"}

# Avoid — mixing instructions and input makes prompts harder to tune
{"role": "user", "content": "Write a tweet about Django 5 release, max 280 chars, punchy tone"}
```

### Encode constraints directly

Put hard rules (character limits, tone, format) in the system prompt. Be explicit:

```
Hard limit: 280 characters.
Return only the post text — no explanations, no quotes, no labels.
```

Models tend to obey explicit constraints better than implied ones. "Short" is vague; "280 characters" is not.

### The output instruction matters

"Return only the post text — no explanations, no quotes, no labels" prevents the model from wrapping the answer in commentary like `"Here's a tweet for you: ..."`. Always tell it exactly what format you want back.

---

## Architecture Pattern: Isolating the LLM Layer

The most important structural decision in this project: **one file owns the LLM**.

```
views.py ──calls──► ai.py ──calls──► OpenAI API
                (only file that
                 imports openai)
```

`views.py` never imports `openai`. It calls `generate_social_post(topic, platform)` and gets a string back. It doesn't care how that string was produced.

**Why this matters:**
- Swapping from OpenAI to Anthropic Claude or Groq is a one-file change
- Easy to test the view without mocking OpenAI — just mock `generate_social_post`
- The LLM prompt logic stays in one place instead of scattered across views

This pattern is worth using in any project that touches an external AI provider.

---

## Django REST Framework Notes

### `APIView` for simple endpoints

For a single endpoint with one HTTP method, `APIView` is cleaner than a `ViewSet`:

```python
class GeneratePostView(APIView):
    def post(self, request):
        serializer = GeneratePostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        # ... do the thing
        return Response({"content": content, "platform": platform})
```

### Serializers for input validation

`Serializer` (not `ModelSerializer`) is the right tool when you're not dealing with a database model:

```python
class GeneratePostSerializer(serializers.Serializer):
    topic = serializers.CharField(min_length=1)
    platform = serializers.ChoiceField(choices=["twitter", "bluesky", ...])
```

`ChoiceField` gives you free validation — passing `"myspace"` returns a 400 automatically.

---

## Config Management with python-decouple

```python
from decouple import config

SECRET_KEY = config("SECRET_KEY")
OPENAI_API_KEY = config("OPENAI_API_KEY")
DEBUG = config("DEBUG", default=True, cast=bool)
```

- Reads from `.env` file first, then environment variables
- `cast=bool` handles `"True"` / `"False"` string → Python bool conversion
- Never hardcode secrets — not even in dev. Always use `.env` + `.env.example`

`.env.example` should always be committed to the repo. `.env` should always be in `.gitignore`.

---

## Things to Explore Next

- [ ] Structured outputs — ask the model to return JSON (`content`, `hashtags`, `character_count`)
- [ ] Token usage logging — `response.usage.prompt_tokens`, `response.usage.completion_tokens`
- [ ] Provider swap — replace OpenAI with `anthropic` SDK, same interface
- [ ] Async generation — Celery task so the view doesn't block waiting for the API
- [ ] Prompt evaluation — compare outputs across models for the same input
