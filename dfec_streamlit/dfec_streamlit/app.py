import streamlit as st
import os

st.title("你好 :blue[Streamlit]")
st.write("该应用程序提供制造可追溯性数据的获取和简单的数据分析菜单。")
st.write("请从侧边栏选择菜单。")

st.subheader("更新履歴")

updates = [
    {"date": "2025年3月19日", 
     "description": "<span style='color:red;'>发布:</span> 初版发布",
    },
    
    {"date": '2025年04月3日', 
     'description': "<span style='color:red;'>新增项目:</span> SL材料工序历史、冷解冻历史日志"
    },  

    {"date": '2026年03月9日', 
     'description': "<span style='color:red;'>新增项目:</span>已完成导入DFEGH-MPI注册的绕线机设定数据和温感成型PRASS注册的加工条件数据。"
    },  
]

for update in updates:
    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            # 日付部分
            st.markdown(f"**{update['date']}**")
        with col2:
            # 説明部分 (HTMLも使用可能)
            st.markdown(update['description'], unsafe_allow_html=True)

with st.sidebar:
    st.page_link("app.py", label="首页", icon="🏠")

    st.subheader("DFEC数据")
    st.page_link("pages/trace_start.py", label="制造数据追踪")
    # st.page_link("pages/trace_from_delivery.py", label="出货历史查询")

