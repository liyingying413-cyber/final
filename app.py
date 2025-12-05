
import streamlit as st
import openai
import random
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Emotion × City × Memory Poster Generator", layout="wide")

st.title("🎨 Emotion × City × Memory — AI Poster Generator")

# Sidebar
st.sidebar.header("Poster Style")
style = st.sidebar.selectbox("Choose style", ["Minimal", "Neon", "Pastel", "Grainy", "Geometric"])

seed = st.sidebar.number_input("Random Seed", value=42)

st.sidebar.markdown("---")
st.sidebar.write("Click to generate once text is entered below.")

# Step 1 — User input
st.header("Step 1 — Input Your Memory Text")
memory_text = st.text_area("Enter your memory, feelings, and city-related experience here...", height=200)

generate = st.button("Generate Poster")

def analyze_memory(text):
    prompt = f"""
    You are an AI that analyzes memory-based text.

    TASKS:
    1. Extract emotional labels (2–4).
    2. Generate an RGB color palette reflecting the feelings (5 colors as tuples of 0–255).
    3. Give emotion intensity between 0 and 1.
    4. Extract city-related keywords (2–5).

    Return JSON with keys: emotions, palette, intensity, keywords.
    Text: {text}
    """

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return eval(resp.choices[0].message["content"])

def generate_poster(palette, intensity, keywords, seed, style):
    random.seed(seed)
    img = Image.new("RGB", (800, 1000), palette[0])
    draw = ImageDraw.Draw(img)

    # Geometry & style
    for i in range(12):
        x1 = random.randint(0, 800)
        y1 = random.randint(0, 1000)
        x2 = x1 + random.randint(80, 240)
        y2 = y1 + random.randint(80, 240)
        color = random.choice(palette)

        if style == "Minimal":
            draw.ellipse([x1, y1, x2, y2], fill=color)
        elif style == "Neon":
            draw.rectangle([x1, y1, x2, y2], fill=color)
        elif style == "Pastel":
            draw.ellipse([x1, y1, x2, y2], fill=color)
        elif style == "Grainy":
            draw.rectangle([x1, y1, x2, y2], fill=color)
        elif style == "Geometric":
            draw.polygon([(x1,y1),(x2,y1),(x2,y2)], fill=color)

    # City-based abstract elements
    if "seoul" in keywords:
        for x in range(0, 800, 40):
            draw.line([x, 0, x, 1000], fill=palette[2], width=4)
    if "tokyo" in keywords:
        for x in range(0, 800, 20):
            for y in range(0, 1000, 20):
                if random.random() < 0.1:
                    draw.rectangle([x,y,x+10,y+10], fill=palette[3])
    if "paris" in keywords:
        for x in range(0, 800, 100):
            draw.arc([x, 300, x+200, 700], 0, 180, fill=palette[4], width=6)

    # Noise based on emotion intensity
    pixels = img.load()
    noise_strength = int(40 * intensity)
    for i in range(800):
        for j in range(1000):
            r = pixels[i,j][0] + random.randint(-noise_strength, noise_strength)
            g = pixels[i,j][1] + random.randint(-noise_strength, noise_strength)
            b = pixels[i,j][2] + random.randint(-noise_strength, noise_strength)
            pixels[i,j] = (max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b)))

    return img

if generate and memory_text.strip():
    st.header("Step 2 — AI Analyzing Your Memory")
    with st.spinner("Analyzing memory text..."):
        result = analyze_memory(memory_text)

    emotions = result["emotions"]
    palette = result["palette"]
    intensity = float(result["intensity"])
    keywords = [k.lower() for k in result["keywords"]]

    st.subheader("Analysis Result")
    st.json(result)

    st.header("Step 3 — Generating Poster")
    img = generate_poster(palette, intensity, keywords, seed, style)

    st.image(img, caption="Generated Poster", use_column_width=True)

    # Download
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button("Download Poster PNG", data=buf.getvalue(), file_name="poster.png", mime="image/png")
