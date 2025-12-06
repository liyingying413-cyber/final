import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils import analyze_with_openai, local_analyze
from poster_generator import generate_poster

st.set_page_config(page_title="City × Memory × Emotion — AI Poster", layout="centered")

st.title("🌆 Emotion × City × Memory — AI Poster Generator")

st.markdown(
    "输入城市名和记忆文本，AI 会分析其中的情绪、色彩、意象，并自动生成唯美渐变风格的艺术海报。"
)

city = st.text_input("城市名（City）", placeholder="例如：Seoul / Tokyo / Paris …")
memory = st.text_area("写下你和这个城市的记忆：", height=200)

seed = st.number_input("随机种子 Seed（相同 seed 会生成相似风格海报）", value=42, step=1)

if st.button("生成海报"):
    if not city.strip() or not memory.strip():
        st.error("城市名与记忆内容不能为空！")
        st.stop()

    with st.spinner("Step 1 — 使用 OpenAI 分析文本风格…"):
        result = analyze_with_openai(city, memory)
        if result is None:
            st.warning("⚠️ OpenAI 调用失败，改用本地 fallback 分析。")
            result = local_analyze(city, memory)

    st.subheader("Step 2 — AI 分析结果（可写入报告）")
    st.json(result)

    with st.spinner("Step 3 — 生成艺术海报…"):
        img = generate_poster(result, seed=seed)

    st.subheader("生成海报预览")
    st.image(img, use_column_width=True)

    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        "下载 PNG 海报",
        data=buf.getvalue(),
        file_name="city_memory_poster.png",
        mime="image/png",
    )
