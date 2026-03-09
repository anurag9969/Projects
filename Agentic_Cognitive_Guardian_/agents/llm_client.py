import os
import json
import re
from functools import lru_cache
from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------
# ENV
# ---------------------------

load_dotenv(override=True)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY missing")

# ---------------------------
# CLIENT (OpenAI compatible)
# ---------------------------

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

# 🔥 Best free OSS reasoning model currently
MODEL_NAME = "qwen/qwen-2.5-72b-instruct"

print("🚀 Loaded OpenAI OSS LLM client")

# ---------------------------
# SAFE JSON PARSER
# ---------------------------

def extract_json(raw: str) -> dict | None:
    try:
        raw = raw.replace("```json", "").replace("```", "").strip()
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            return None
        return json.loads(match.group(0))
    except Exception:
        return None


# ---------------------------
# GENERIC CALL
# ---------------------------

@lru_cache(maxsize=256)
def call_llm(system_prompt: str, user_prompt: str) -> dict | None:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )

        raw = response.choices[0].message.content.strip()
        return extract_json(raw)

    except Exception as e:
        print("❌ LLM call failed:", e)
        return None
