import streamlit as st

st.title(":blue[DFEC数据] 制造数据追踪")
st.write("该应用程序提供制造可追溯性数据的获取和简单的数据分析菜单。")
st.write("请从侧边栏选择菜单。")

with st.sidebar:
    st.page_link("app.py", label="首页", icon="🏠")   
    st.page_link("pages/trace_by_lot.py", label="LotNo搜索")

