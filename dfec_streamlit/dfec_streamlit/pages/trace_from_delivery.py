# import streamlit as st
# from sqlalchemy import create_engine, text
# import pandas as pd
# import time 
# from db_util import connect_to_postgresql
# from datetime import datetime
# from io import BytesIO

# from functions.dataframe_delivery import  df_delivery_record
# from functions.dataframe_prass import  df_create_by_insp_no, df_add_lot_info

# from functions.column_replace import df_column_replace

# # メイン関数
# def main():

#     st.title(":blue[DFEC数据] 出货历史查询")

#     # データベース接続情報とエンジン作成    
#     engine = create_db_engine()
#     # サイドバーでフィルタ設定を取得
#     filters = sidebar_filters()

#     search_button_clicked = st.sidebar.button('搜索')

#     # セッションステートの初期化
#     if 'df' not in st.session_state:
#         st.session_state.df = None

#     #工程別対象ロットの工程別情報
#     if search_button_clicked :
#         start_time=time.time()
#         st.subheader('検索条件')
#         st.write(filters)
#         df, error = df_delivery_record(engine, filters)
#         if error :
#             st.error(error)
#         else :

#             row_count = len(df)
#             st.write(f"対象件数: {row_count}")

#             selected_lang_value = filters['lang']
#             df, error_list = df_column_replace(engine, selected_lang_value, df )
            
#             st.subheader('出货历史')
#             st.session_state.df = df
#             st.write(st.session_state.df)
#             st.write(st.session_state.df.shape[1])

#             # Excelファイルとして書き込むためのバッファ作成
#             buffer = BytesIO()
#             with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
#                 st.session_state.df.to_excel(writer, index=False, sheet_name='Sheet1')
#             # バッファの位置を先頭に戻す
#             buffer.seek(0)
#             # ダウンロードボタンの作成
#             st.download_button(
#                 label="Download Excel",
#                 data=buffer,
#                 file_name="delivery_record.xlsx",
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )

#             st.button("出荷履歴に対応する製造履歴を発行(DFECのみ)")

#             st.subheader('変換未設定項目')
#             st.write(error_list)

#             elapsed_time = time.time() - start_time
#             st.write(f"処理時間: {elapsed_time:.2f}秒")

#     elif st.session_state.df is not None:
#         # 検索ボタンが押されていない場合でも、既存のdfがある場合は表示とパレート図描画する。
#         st.subheader('出货历史')
#         st.write(st.session_state.df)
#         # Excelファイルとして書き込むためのバッファ作成
#         buffer = BytesIO()
#         with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
#             st.session_state.df.to_excel(writer, index=False, sheet_name='Sheet1')
#         # バッファの位置を先頭に戻す
#         buffer.seek(0)
#         # ダウンロードボタンの作成
#         st.download_button(
#             label="Download Excel",
#             data=buffer,
#             file_name="delivery_record.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )
#         if st.button("出荷履歴に対応する製造履歴を発行(DFECのみ)") :
#             filtered_df = st.session_state.df[
#                 st.session_state.df['toko_type'].notna() & 
#                 st.session_state.df['toko_type'].str.startswith(('DFE'))
#             ]
#             insp_list = filtered_df['inspection_no'].unique().tolist()
#             if insp_list is not None :

#                 df, error = df_create_by_insp_no(engine, insp_list)
#                 lot_no_list = df['lot_no'].tolist()
#                 count = len(lot_no_list)
#                 st.write(f"対象ロット数: {count}")

#                 df = df_add_lot_info(engine, lot_no_list)

#                 selected_lang_value = filters['lang']
#                 df, error_list = df_column_replace(engine, selected_lang_value, df )
                
#                 st.session_state.df_pd = df
#                 st.write(st.session_state.df_pd)
#                 st.write(st.session_state.df_pd.shape[1])

# def create_db_engine():
#     conn_pg = connect_to_postgresql()
#     try:
#         return create_engine('postgresql://', creator=lambda: conn_pg)
#     except Exception as e:
#         st.error(f"发生错误: {e}")


# def sidebar_filters():
#     with st.sidebar:
#         st.page_link("app.py", label="首页", icon="🏠")    
#         insno_from = st.text_input("Inspection No. From:", "ZG0000000")
#         insno_to = st.text_input("To:", "ZG99999ZZ")
    
#         today = datetime.today().date()
#         two_years_ago = today.replace(year=today.year - 2, day=1)
    
#         start_date, end_date = st.slider(
#             "SALES_DATE",
#             min_value=two_years_ago,
#             max_value=today,
#             value=(two_years_ago, today),
#             format="YYYY/MM/DD"
#         )
        
#         st.markdown("---")

#         # Type
#         murata_type = st.text_input("Murata Type")

#         lang_options = {
#             "变换无": None,   # 変換なし
#             "日文": "jp",     # 日本語
#             "中文": "local"   # 現地語（中国語）
#         }
#         lang_key = st.selectbox("请选择语言", list(lang_options.keys()))

#         return {
#             'murata_type': murata_type,
#             'insno_from': insno_from,
#             'insno_to' : insno_to,
#             'start_date': start_date,
#             'end_date': end_date,
#             'lang' : lang_options[lang_key],
#         }
   
# if __name__ == "__main__":
#     main()
