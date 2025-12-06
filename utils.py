
import os, json
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

def analyze_with_openai(city, memory):
    if client is None:
        return None

    prompt = f"""
Analyze the user's memory and return structured JSON:
{{
 "emotions": [...],
 "intensity": 0.0,
 "color_palette": [[r,g,b], ...],
 "art_style": "Dreamy",
 "city_keywords": [...]
}}

City: {city}
Memory: {memory}
"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
        )
        return json.loads(resp.choices[0].message.content)
    except:
        return None


def local_analyze(city, memory):
    return {
        "emotions": ["nostalgic", "calm"],
        "intensity": 0.4,
        "color_palette": [
            [0.3,0.5,0.7],
            [0.9,0.2,0.4],
            [0.5,0.4,0.6]
        ],
        "art_style": "Dreamy",
        "city_keywords": [
            city.lower(),
            "abstract memory"
        ]
    }
