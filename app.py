import streamlit as st
import random
import numpy as np
from PIL import Image, ImageDraw
import io
import base64
from openai import OpenAI

# ---------------------------------------
# Safe OpenAI client creation
# ---------------------------------------
def create_openai_client():
    try:
        return OpenAI()
    except Exception:
        return None

client = create_openai_client()

# ---------------------------------------
# Local fallback analyzer (if OpenAI fails)
# ---------------------------------------
def local_analyze(city, memory):
    # Very simplified emotion/color extraction
    keywords = ["happy", "bright", "love", "warm", "sad", "cold", "night", "busy", "quiet"]
    emotions = []
    colors = []

    text = (city + " " + memory).lower()

    if "happy" in text or "love" in text or "warm" in text:
        emotions.append("positive")
        colors.append([0.9, 0.5, 0.4])
    if "sad" in text or "cold" in text or "night" in text:
        emotions.append("negative")
        colors.append([0.3, 0.3, 0.6])
    if "busy" in text:
        emotions.append("energetic")
        colors.append([0.9, 0.8, 0.2])
    if "quiet" in text:
        emotions.append("calm")
        colors.append([0.2, 0.6, 0.5])

    if not emotions:
        emotions = ["neutral"]
        colors = [[0.5, 0.5, 0.5]]

    wobble = random.uniform(0.15, 0.45)

    city_keywords = []
    if "seoul" in text:
        city_keywords = ["vertical neon lines"]
    elif "tokyo" in text:
        city_keywords = ["pixel grid"]
    elif "paris" in text:
        city_keywords = ["arches"]
    else:
        city_keywords = ["abstract shapes"]

    return {
        "emotions": emotions,
        "color_palette": colors,
        "intensity": wobble,
        "city_keywords": city_keywords,
    }

# ---------------------------------------
# OpenAI (preferred) analyzer
# ---------------------------------------
def analyze_with_openai(city, memory):
    if client is None:
        return None  # no client → fallback later

    prompt = f"""
You are an AI that analyzes the user's memory text and city name to extract:
1) emotion labels (list)
2) an RGB color palette (list of [r,g,b])
3) an emotion intensity value 0–1
4) city-related abstract visual keywords

City: {city}
Memory: {memory}

Return JSON with keys: emotions, color_palette, intensity, city_keywords.
"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        import json
        parsed = json.loads(resp.choices[0].message.content)
        return parsed

    except Exception:
        return None  # fail → fallback


# ---------------------------------------
# Abstract poster generator
# ---------------------------------------
def generate_poster(style, colors, intensity, seed, city_keywords):
    random.seed(seed)
    np.random.seed(seed)

    img = Image.new("RGB", (800, 1200), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # background
    base_color = tuple(int(c * 255) for c in colors[0])
    draw.rectangle([0, 0, 800, 1200], fill=base_color)

    # simple abstract shapes
    for _ in range(15):
        x1 = random.randint(0, 800)
        y1 = random.randint(0, 1200)
        size = random.randint(80, 200)
        noise = int(80 * intensity)

        r = max(0, min(255, base_color[0] + random.randint(-noise, noise)))
        g = max(0, min(255, base_color[1] + random.randint(-noise, noise)))
        b = max(0, min(255, base_color[2] + random.randint(-noise, noise)))
        color = (r, g, b)

        draw.ellipse([x1, y1, x1 + size, y1 + size], fill=color)

    # city abstract element overlay
    if "vertical neon lines" in city_keywords:
        for x in range(0, 800, 50):
            draw.line([x, 0, x, 1200], fill=(255, 255, 255, 80), width=6)

    elif "pixel grid" in city_keywords:
        for x in range(0, 800, 40):
            for y in range(0, 1200, 40):
                draw.rectangle([x, y, x + 8, y + 8], fill=(255, 255, 255))

    elif "arches" in city_keywords:
        for x in range(100, 700, 200):
            draw.arc([x, 300, x + 300, 900], 0, 180, fill=(255, 255, 255), width=8)

    return img


def convert_img_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------
# Streamlit UI
# ---------------------------------------
st.title("城市 × 记忆 × 情绪 → 抽象海报生成器 🎨")

style = st.selectbox("选择海报风格：", ["Minimal", "Neon", "Pastel", "Grainy", "Geometric"])
city_input = st.text_input("输入城市名 (例如 Seoul, Tokyo, Paris...)")
memory_input = st.text_area("写下你对这个城市的记忆：")

seed = st.number_input("Seed（可重复生成）", min_value=0, max_value=999999, value=42)

if st.button("Generate Poster"):
    if not city_input.strip() or not memory_input.strip():
        st.error("请填写城市名和记忆文本！")
        st.stop()

    # STEP 2 — AI Analysis
    result = analyze_with_openai(city_input, memory_input)
    if result is None:
        st.warning("OpenAI 调用失败，使用本地 fallback 分析。")
        result = local_analyze(city_input, memory_input)

    colors = result["color_palette"]
    intensity = result["intensity"]
    city_kw = result["city_keywords"]

    # STEP 3 — Generate Poster
    poster = generate_poster(style, colors, intensity, seed, city_kw)

    st.image(poster, caption="Generated Poster", use_column_width=True)

    # STEP 4 — Show Analysis
    st.subheader("AI 分析结果")
    st.json(result)

    # Download button
    st.download_button(
        label="下载海报 PNG",
        data=convert_img_to_bytes(poster),
        file_name="poster.png",
        mime="image/png",
    )
