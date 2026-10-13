import streamlit as st

st.title("你好 :blue[Streamlit]")
st.write("该应用程序提供制造可追溯性数据的获取和简单的数据分析菜单。")
st.write("请从侧边栏选择菜单。")

with st.sidebar:
    st.page_link("app.py", label="首页", icon="🏠")

    st.subheader("DFEC数据")
    st.page_link("pages/trace_start.py", label="制造数据追踪")

    st.subheader("可视化菜单")
    st.page_link("pages/visualize_data.py", label="直方图")
    st.page_link("pages/visualize_pair.py", label="配对图")