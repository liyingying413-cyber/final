import streamlit as st

st.title("城市记忆收集器")

city = st.text_input("请输入城市名称：")
memory = st.text_area("请输入你对这个城市的记忆：")

if st.button("提交"):
    if not city.strip() or not memory.strip():
        st.warning("城市名称和记忆都不能为空！")
    else:
        st.success(f"已成功记录你对 **{city}** 的记忆！")
        st.write("### 你的记录内容：")
        st.write(memory)
