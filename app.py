
import streamlit as st
import json
from utils import analyze_with_openai, local_analyze
from poster_generator import generate_poster_image

st.set_page_config(page_title="City × Memory × Emotion — AI Poster", layout="wide")

st.title("🌆 Emotion × City × Memory — AI Poster Generator")

city = st.text_input("Enter a city name (e.g., Seoul, Tokyo, Paris)")
memory = st.text_area("Describe your memory about this city")
style = st.selectbox("Choose AI Art Style", ["Dreamy","Cyberpunk","Film mood","Shimmer","Brutalist grid"])
seed = st.number_input("Seed (for reproducibility)", value=42, step=1)

if st.button("Generate Poster"):
    if not city.strip() or not memory.strip():
        st.error("Please enter both city and memory text!")
        st.stop()

    with st.spinner("Analyzing with OpenAI..."):
        result = analyze_with_openai(city, memory)
        if result is None:
            st.warning("⚠️ OpenAI failed. Using fallback local analyzer.")
            result = local_analyze(city, memory)

    st.subheader("AI Analysis Result")
    st.json(result)

    with st.spinner("Generating Poster..."):
        img = generate_poster_image(result, style, seed)

    st.image(img, caption="Generated Poster", use_column_width=True)

    # Download
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button("Download Poster", data=buf.getvalue(), file_name="poster.png", mime="image/png")
