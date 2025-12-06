import os
import json
from openai import OpenAI

# 从环境变量读取 API Key（本地可以用 .env；Streamlit Cloud 用 Secrets）
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if API_KEY else None


def analyze_with_openai(city: str, memory: str):
    """调用 OpenAI，让它当「艺术总监」输出设计参数。"""
    if client is None:
        return None

    # 注意：这里不用 f-string 里的 {{ }}，避免语法冲突
    prompt = (
        "You are an art-director AI. Analyze the user's memory text about a city and "
        "design parameters for a poetic, atmospheric poster (soft gradients, motion, "
        "mist, flowing paint). You will NOT describe the image in words; instead you "
        "output pure design parameters.\n\n"
        "You MUST return ONLY valid JSON with the following keys:\n"
        "{\n"
        '  \"title\": \"poetic short title (1–8 words, can be Chinese)\",\n'
        '  \"subtitle\": \"1–2 short emotional lines (can be Chinese)\",\n'
        '  \"mood\": \"2–3 word mood label (e.g. nostalgic calm)\",\n'
        '  \"intensity\": 0.0–1.0,\n'
        '  \"palette\": [\"#RRGGBB\", \"#RRGGBB\", ... 3–5 colors],\n'
        '  \"style_mode\": \"one of: misty_gradient, ocean_motion, flowing_paint, clean_minimal\",\n'
        '  \"city_keywords\": [\"abstract visual words like mist, ocean, neon, snow\"],\n'
        '  \"typography_focus\": \"one of: large_title, balanced, text_on_bottom\"\n'
        "}\n\n"
        "City:\n"
        f"{city}\n\n"
        "Memory text:\n"
        f"{memory}\n"
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        content = resp.choices[0].message.content
        data = json.loads(content)
        return data
    except Exception:
        return None


def local_analyze(city: str, memory: str):
    """没有 API key 或请求失败时的简易规则版分析。"""
    text = (city + " " + memory).lower()
    mood = "calm nostalgic"

    if any(w in text for w in ["rain", "雨", "fog", "雾", "lonely", "寂寞", "sad"]):
        mood = "melancholic soft"
        palette = ["#7FA2C8", "#E7EDF5", "#405B88"]
        style = "misty_gradient"
    elif any(w in text for w in ["sea", "海", "beach", "浪", "wave", "波"]):
        mood = "ocean dream"
        palette = ["#6EC3D6", "#E3F6FD", "#2C5B8A"]
        style = "ocean_motion"
    elif any(w in text for w in ["summer", "夏天", "sun", "阳光"]):
        mood = "bright warm"
        palette = ["#F9E8A5", "#FFBE88", "#7FD2C3"]
        style = "flowing_paint"
    else:
        palette = ["#A9C8D8", "#E4EEF5", "#6FA3C8"]
        style = "misty_gradient"

    return {
        "title": f"{city} 的记忆",
        "subtitle": "一段关于城市与情绪的片段。",
        "mood": mood,
        "intensity": 0.5,
        "palette": palette,
        "style_mode": style,
        "city_keywords": [city.lower(), "memory"],
        "typography_focus": "balanced",
    }
