import streamlit as st
import os
import random
import json
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import io

# Try to import OpenAI new SDK style. If not available or no API key provided,
# we'll fall back to a simple deterministic local analyzer (mock).
try:
    from openai import OpenAI
    has_openai_pkg = True
except Exception:
    OpenAI = None
    has_openai_pkg = False

st.set_page_config(page_title="Emotion × City × Memory — Poster Generator", layout="wide")
st.title("🎨 Emotion × City × Memory — Poster Generator")

# ---------- Sidebar / Controls ----------
st.sidebar.header("Poster Controls")
style = st.sidebar.selectbox("Choose poster style", ["Minimal", "Neon", "Pastel", "Grainy", "Geometric"])
seed = int(st.sidebar.number_input("Random seed (for reproducibility)", value=42, step=1))
wobble = float(st.sidebar.slider("Wobble / Noise strength", min_value=0.0, max_value=1.0, value=0.4, step=0.05))
size = st.sidebar.selectbox("Output size", ["800x1000", "600x800", "1200x1500"])
w, h = map(int, size.split("x"))

st.sidebar.markdown("---")
st.sidebar.write("Hints: enter city first, then describe a memory. If you don't set an API key, a local analyzer will run.")

# ---------- Step 1: Inputs ----------
st.header("Step 1 — Enter City and Memory")
city = st.text_input("City name (e.g., Seoul, Paris, Tokyo)", value="")
memory = st.text_area("Write a memory about this city (describe feelings, places, moments)...", height=220)

generate = st.button("Generate Poster")

# ---------- Utility: safe JSON parse from model output ----------
def safe_parse_json(s):
    try:
        return json.loads(s)
    except Exception:
        # attempt to find first brace and eval
        try:
            start = s.index('{')
            obj = s[start:]
            return json.loads(obj)
        except Exception:
            return None

# ---------- Analyzer: tries OpenAI new SDK, otherwise local mock ----------
def analyze_memory_with_openai(text, city_name):
    # Expect assistant to return a JSON string with keys: emotions(list), palette(list of [r,g,b]), intensity(float), keywords(list)
    try:
        client = OpenAI()
        prompt = f\"\"\"You are a helpful assistant. Analyze the following user memory and the provided city.

Tasks:
1) Return 2-4 short emotion labels (strings) inferred from the text.
2) Return a color palette of 5 RGB colors (each as a list of three integers 0-255) that matches the emotions.
3) Return an emotion intensity as a number between 0 and 1 (higher means stronger / more vivid).
4) Return 2-5 short keywords related to the city or memory (lowercase strings).

Output EXACTLY a JSON object with keys:
{
  "emotions": [...],
  "palette": [[r,g,b],...],
  "intensity": 0.0,
  "keywords": [...]
}

City: {city_name}
Memory text:
{text}
\"\"\"
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.8,
            max_tokens=400
        )
        content = resp.choices[0].message.content
        parsed = safe_parse_json(content)
        if parsed:
            return parsed
    except Exception as e:
        # fall through to local fallback
        st.warning("OpenAI analysis failed or is unavailable — using local analyzer instead.")
    return None

def local_analyze(text, city_name):
    # Simple deterministic rule-based analyzer as fallback.
    t = text.lower()
    emotions = []
    if any(x in t for x in ["happy","joy","joyful","glad","delight","amazing","excited"]):
        emotions.append("joy")
    if any(x in t for x in ["sad","sorrow","lonely","tears","cry"]):
        emotions.append("sadness")
    if any(x in t for x in ["love","romantic","love","beloved"]):
        emotions.append("love")
    if any(x in t for x in ["nostalgia","nostalgic","remember","memory"]):
        emotions.append("nostalgia")
    if any(x in t for x in ["anxious","anxiety","nervous","scared","fear"]):
        emotions.append("anxiety")
    if not emotions:
        # default emotionally neutral + curiosity
        emotions = ["nostalgia"]

    # simple palette mapping by emotion
    palette_map = {
        "joy": [[255,230,120],[255,180,80],[255,120,120],[255,200,150],[240,240,180]],
        "sadness": [[30,60,120],[80,110,160],[120,150,200],[40,80,140],[20,40,80]],
        "love": [[255,120,150],[255,80,110],[240,180,200],[255,200,210],[220,100,140]],
        "nostalgia": [[220,180,150],[200,170,140],[240,220,200],[180,150,130],[210,190,170]],
        "anxiety": [[180,60,60],[140,40,40],[200,80,80],[160,70,70],[120,50,50]]
    }
    # Build palette by mixing palettes of detected emotions
    palette = []
    for i in range(5):
        # pick color from first emotion primarily, else fallback
        e = emotions[0]
        col = palette_map.get(e, palette_map["nostalgia"])[i % 5]
        palette.append(col)

    # intensity proportional to punctuation and length
    intensity = min(1.0, max(0.05, (len(text) / 400) + text.count("!")*0.1))

    # keywords: pick some city + nouns by simple heuristics (split on spaces, pick content words)
    words = [w.strip(".,!?") for w in text.split() if len(w) > 3]
    keywords = []
    if city_name:
        keywords.append(city_name.lower())
    for w in words:
        lw = w.lower()
        if lw not in keywords and len(keywords) < 5:
            keywords.append(lw)
    if not keywords:
        keywords = [city_name.lower() if city_name else "city", "memory"]

    return {
        "emotions": emotions[:4],
        "palette": palette,
        "intensity": round(float(intensity), 3),
        "keywords": keywords[:5]
    }

def analyze_memory(text, city_name):
    # Try OpenAI first if package present and key set
    result = None
    if has_openai_pkg:
        # ensure deployers set OPENAI_API_KEY in st.secrets or environment
        try:
            # client will read from environment as OpenAI() does by default
            result = analyze_memory_with_openai(text, city_name)
        except Exception:
            result = None
    if result is None:
        result = local_analyze(text, city_name)
    return result

# ---------- Poster generation functions ----------
def draw_gradient(img, color1, color2):
    # vertical gradient
    base = Image.new('RGB', img.size, tuple(color1))
    top = Image.new('RGB', img.size, tuple(color2))
    mask = Image.linear_gradient("L").resize(img.size)
    return Image.composite(top, base, mask)

def generate_poster_image(palette, intensity, keywords, seed, style, size_w, size_h, wobble):
    random.seed(seed)
    img = Image.new("RGB", (size_w, size_h), tuple(palette[0]))
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    draw = ImageDraw.Draw(layer)

    # Determine counts based on intensity and style
    count = int(6 + intensity*20)

    # Shapes
    for i in range(count):
        cx = random.randint(0, size_w)
        cy = random.randint(0, size_h)
        rx = random.randint(int(size_w*0.05), int(size_w*0.25))
        ry = random.randint(int(size_h*0.05), int(size_h*0.25))
        color = tuple(random.choice(palette))
        bbox = [cx-rx, cy-ry, cx+rx, cy+ry]
        if style == "Minimal":
            draw.ellipse(bbox, fill=color + (200,))
        elif style == "Neon":
            # draw ring
            draw.ellipse(bbox, outline=color + (255,), width=max(3,int(6*wobble)))
            inner = [bbox[0]+int(rx*0.25), bbox[1]+int(ry*0.25), bbox[2]-int(rx*0.25), bbox[3]-int(ry*0.25)]
            draw.ellipse(inner, fill=(0,0,0,0))
        elif style == "Pastel":
            draw.ellipse(bbox, fill=color + (160,))
        elif style == "Grainy":
            draw.rectangle(bbox, fill=color + (200,))
        elif style == "Geometric":
            # triangle
            draw.polygon([(cx, cy-ry),(cx-rx, cy+ry),(cx+rx, cy+ry)], fill=color + (220,))

    # City-specific abstract elements (keywords prioritized + city name)
    lc = " ".join(keywords).lower()
    if "seoul" in lc:
        # vertical neon-like lines
        line_color = tuple(palette[2])
        for x in range(0, size_w, max(10,int(40*(1-intensity)))):
            draw.line([(x,0),(x,size_h)], fill=line_color + (200,), width=max(2,int(8*wobble)))
    if "tokyo" in lc:
        # pixel grid
        for x in range(0, size_w, 20):
            for y in range(0, size_h, 20):
                if random.random() < 0.08 + intensity*0.05:
                    draw.rectangle([x,y,x+8,y+8], fill=tuple(palette[3]) + (200,))
    if "paris" in lc:
        # arches
        for x in range(0, size_w, 100):
            draw.arc([x, int(size_h*0.25), x+100, int(size_h*0.75)], 0, 180, fill=tuple(palette[4]) + (200,), width=max(3,int(6*wobble)))

    # Merge layer down
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

    # Gradient overlay based on palette
    grad = draw_gradient(img, palette[0], palette[-1])
    img = ImageChops.overlay(img, grad)

    # Apply grain/noise based on intensity and wobble
    if style == "Grainy" or wobble > 0:
        noise = Image.effect_noise(img.size, 100*intensity*wobble + 1)
        noise = noise.convert("L").point(lambda p: int(p * 0.6))
        noise_rgb = Image.merge("RGB", (noise, noise, noise)).filter(ImageFilter.GaussianBlur(radius=1))
        img = ImageChops.add(img, noise_rgb)

    # Slight blur or sharpen depending on style
    if style == "Pastel":
        img = img.filter(ImageFilter.GaussianBlur(radius=1 + 2*(1-intensity)))
    if style == "Neon":
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

    return img

# ---------- Main generate flow ----------
if generate:
    if not city.strip():
        st.warning("Please enter a city name before generating.")
    elif not memory.strip():
        st.warning("Please write a memory about that city.")
    else:
        with st.spinner("Analyzing memory and generating poster..."):
            analysis = analyze_memory(memory, city)
            # analysis expected: emotions, palette, intensity, keywords
            emotions = analysis.get("emotions", [])
            palette = analysis.get("palette", [[220,180,150]]*5)
            intensity = float(analysis.get("intensity", 0.4))
            keywords = analysis.get("keywords", [city.lower()])

            # Normalize palette to ints
            palette = [[int(c) for c in col] for col in palette]

            st.subheader("Step 2 — Analysis result")
            col1, col2 = st.columns([1,2])
            with col1:
                st.write("**Emotions**")
                st.write(emotions)
                st.write("**Intensity**")
                st.write(round(intensity,3))
                st.write("**Keywords**")
                st.write(keywords)
            with col2:
                st.write("**Color palette**")
                cols = st.columns(5)
                for i, c in enumerate(palette):
                    cols[i].markdown(f"RGB: {c}")
                    sw = Image.new("RGB", (80,80), tuple(c))
                    buf = io.BytesIO()
                    sw.save(buf, format="PNG")
                    cols[i].image(buf.getvalue())

            st.subheader("Step 3 — Generated Poster")
            img = generate_poster_image(palette, intensity, keywords, seed, style, w, h, wobble)
            st.image(img, use_column_width=True)

            # Download
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button("Download poster (PNG)", data=buf.getvalue(), file_name=f"{city.replace(' ','_')}_poster.png", mime="image/png")

# ---------- Footer: instructions ----------
st.markdown("---")
st.markdown("**Notes:**\n- To use the OpenAI analyzer, set `OPENAI_API_KEY` in Streamlit secrets.\n- Local analyzer runs automatically if no OpenAI key is available.")
