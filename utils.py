import os
import json
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if API_KEY else None


def analyze_with_openai(city: str, memory: str):
    if client is None:
        return None

    prompt = (
        "You are an art director AI. Analyze the user's memory text about a city and "
        "generate design parameters for a poetic, minimalist, atmospheric poster "
        "(soft gradients, mist, flowing motion, dreamy colors).\n\n"
        "Return ONLY JSON with the following keys:\n"
        "{\n"
        '  \"title\": \"poetic title\",\n'
        '  \"subtitle\": \"1–2 emotional lines\",\n'
        '  \"mood\": \"nostalgic calm\",\n'
        '  \"intensity\": 0.0,\n'
        '  \"palette\": [\"#AABBCC\", \"#112233\", \"#FFEEDD\"],\n'
        '  \"style_mode\": \"misty_gradient\",\n'
        '  \"city_keywords\": [\"mist\", \"ocean\", \"neon\"],\n'
        '  \"typography_focus\": \"balanced\"\n'
        "}\n\n"
        f"City: {city}\nMemory: {memory}\n"
    )

    try:
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        content = resp.output_text  # New SDK field
        return json.loads(content)

    except Exception as e:
        print("OpenAI error:", e)
        return None


def local_analyze(city, memory):
    return {
        "title": f"{city} 的记忆",
        "subtitle": "关于这座城市的情绪片段",
        "mood": "calm nostalgic",
        "intensity": 0.5,
        "palette": ["#A9C8D8", "#E4EEF5", "#6FA3C8"],
        "style_mode": "misty_gradient",
        "city_keywords": [city.lower()],
        "typography_focus": "balanced"
    }
