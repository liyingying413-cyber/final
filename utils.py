import os
import json
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if API_KEY else None


def analyze_with_openai(city: str, memory: str):
    if client is None:
        return None

    prompt = (
        "You are an art-director AI. Analyze the user's memory text about a city and "
        "generate design parameters for a poetic, minimalist, atmospheric poster "
        "(soft gradients, mist, flowing motion, dreamy colors).\n\n"
        "Return ONLY JSON with the following keys:\n"
        "{\n"
        '  "title": "poetic title",\n'
        '  "subtitle": "1–2 emotional lines",\n'
        '  "mood": "nostalgic calm",\n'
        '  "intensity": 0.0,\n'
        '  "palette": ["#AABBCC", "#112233", "#FFEEDD"],\n'
        '  "style_mode": "misty_gradient",\n'
        '  "city_keywords": ["mist", "ocean", "neon"],\n'
        '  "typography_focus": "balanced"\n'
        "}\n\n"
        f"City: {city}\n\nMemory: {memory}\n"
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return None


def local_analyze(city: str, memory: str):
    text = (city + memory).lower()

    palette = ["#A9C8D8", "#E4EEF5", "#6FA3C8"]
    style_mode = "misty_gradient"
    mood = "calm nostalgic"

    if any(w in text for w in ["rain", "fog", "雾", "雨", "sad", "lonely", "寂寞"]):
        palette = ["#7FA2C8", "#E7EDF5", "#405B88"]
        style_mode = "misty_gradient"
        mood = "melancholic soft"
    elif any(w in text for w in ["sea", "海", "wave", "ocean"]):
        palette = ["#6EC3D6", "#E3F6FD", "#2C5B8A"]
        style_mode = "ocean_motion"
        mood = "ocean dream"
    elif any(w in text for w in ["summer", "阳光", "暖", "bright"]):
        palette = ["#F9E8A5", "#FFBE88", "#7FD2C3"]
        style_mode = "flowing_paint"
        mood = "warm bright"

    return {
        "title": f"{city} 的记忆",
        "subtitle": "关于这座城市的情绪片段。",
        "mood": mood,
        "intensity": 0.5,
        "palette": palette,
        "style_mode": style_mode,
        "city_keywords": [city.lower()],
        "typography_focus": "balanced",
    }
