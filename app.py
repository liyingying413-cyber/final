import streamlit as st
from utils import analyze_with_openai, local_analyze
from poster_generator import generate_poster

st.set_page_config(page_title="City × Memory × Emotion — AI Poster", layout="centered")

st.title("🌆 Emotion × City × Memory — AI Poster Generator")

st.markdown(
    "输入一个城市名和一段关于它的记忆，AI 会分析其中的情绪和氛围，"
    "生成适合的色彩与艺术风格，并自动排版成一张唯美的海报。"
)

city = st.text_input("城市名（City）", placeholder="例如：Seoul / Tokyo / Paris …")
memory = st.text_area("写下你和这个城市的记忆：", height=200)

seed = st.number_input("随机种子 Seed（相同 seed 会得到风格类似的海报）", value=42, step=1)

if st.button("生成海报"):
    if not city.strip() or not memory.strip():
        st.error("城市名和记忆内容都要填写哦。")
        st.stop()

    with st.spinner("Step 1 — 使用 OpenAI 分析情绪与视觉参数…"):
        result = analyze_with_openai(city, memory)
        if result is None:
            st.warning("⚠️ OpenAI 调用失败，使用本地 fallback 分析。")
            result = local_analyze(city, memory)

    st.subheader("Step 2 — AI 分析结果（可写进报告）")
    st.json(result)

    with st.spinner("Step 3 — 生成海报…"):
        img = generate_poster(result, seed=seed)

    st.subheader("Step 4 — 生成的海报预览")
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
