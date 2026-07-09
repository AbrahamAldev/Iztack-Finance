"""Test OpenRouter connection directly."""
import os
from openai import OpenAI

key = os.environ.get("OPENROUTER_API_KEY", "")
print(f"Key starts: {key[:15]}...")
print(f"Key valid format: {key.startswith('sk-or-v1-')}")
print(f"Key length: {len(key)}")

if not key:
    print("ERROR: No OPENROUTER_API_KEY set")
    exit(1)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=key,
    default_headers={
        "HTTP-Referer": "https://finance.iztack.com",
        "X-Title": "Iztack-Finance Test",
    },
)

try:
    r = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Di hola en español en 5 palabras"}],
        max_tokens=50,
    )
    print("Response:", r.choices[0].message.content)
    print("Model used:", r.model)
except Exception as e:
    error_str = str(e)
    if "402" in error_str or "insufficient_quota" in error_str or "credit" in error_str.lower():
        print("ERROR: SIN CRÉDITO en OpenRouter")
    elif "401" in error_str or "Unauthorized" in error_str:
        print("ERROR: API Key inválida o expirada")
    else:
        print("Error:", error_str[:200])