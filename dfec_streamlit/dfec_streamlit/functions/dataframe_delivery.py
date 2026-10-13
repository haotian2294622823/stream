# from sqlalchemy import  text
# import pandas as pd
# import time 
# import streamlit as st
# from .queries_delivery import select_delivery_list
# from .queries_prass import select_inspection_info, select_lot_base_info, select_lot_defect_info
# from .queries_prass import select_material_info, select_process_info, select_process_machine_info
# from .queries_prass import select_process_worker_info, select_process_defect_info

# #------------------------------------------------------
# #　データ探索の起点となるデータフレーム作成
# #------------------------------------------------------

# # 1. 指定したロットNoからの検索
# def df_delivery_record(engine, filters):
#     with engine.connect() as connection:

#         query = select_delivery_list()

#         params=(
#             f"{filters['murata_type']}%", filters['murata_type'],
#             f"{filters['insno_from']}%", filters['insno_to'],
#             filters['start_date'], 
#             filters['end_date'], 
#         )

#         df = pd.read_sql_query(query, connection, params=params)
#         error_message = None
#         if df.empty:
#             error_message = "ロットNoが存在しない"
#         return df, error_message


# #------------------------------------------------------
# # LOT NOに関する基礎的なデータ追加 
# #------------------------------------------------------
# def df_add_lot_base(connection, category) :    
#     query = select_lot_base_info(category)
#     df = pd.read_sql_query(query, connection) 
#     return(df)


# #------------------------------------------------------
# # 検印番号、PSロット
# #------------------------------------------------------
# def df_add_inspection(connection, category) : 
#     query =select_inspection_info(category)
#     df = pd.read_sql_query(query, connection) 
#     return(df)

# #------------------------------------------------------
# # 不良項目別、不良数追加 
# #------------------------------------------------------
# def df_add_defect(connection, category) :
#     query = select_lot_defect_info(category)
#     df = pd.read_sql_query(query, connection) 
#     return(df)

# #------------------------------------------------------
# # 工程情報 
# #------------------------------------------------------
# def df_add_process(connection, category) :
#     query = select_process_info(category)
#     df = pd.read_sql_query(query, connection)
#     return(df)


# #------------------------------------------------------
# # 工程別不良情報 
# #------------------------------------------------------
# def df_add_process_defect(connection, category) :
#     query = select_process_defect_info(category)
#     df = pd.read_sql_query(query, connection)
#     return(df)

# #------------------------------------------------------
# # 工程設備情報 
# #------------------------------------------------------
# def df_add_process_machine(connection, category) :
#     query = select_process_machine_info(category)
#     df = pd.read_sql_query(query, connection)
#     return(df)

# #------------------------------------------------------
# # 工程材料情報 
# #------------------------------------------------------
# def df_add_process_material(connection, category) :
#     query = select_material_info(category)
#     df = pd.read_sql_query(query, connection)
#     return(df)

# #------------------------------------------------------
# # 工程作業者情報 
# #------------------------------------------------------
# def df_add_process_worker(connection, category) :
#     query = select_process_worker_info(category)
#     df = pd.read_sql_query(query, connection) 
#     return(df)


# # データフレームをグループ化し、サフィックス付きで展開する関数定義
# def expand_grouped_columns(group, max_length):

#     # サフィックス付きカラム名生成と初期化
#     expanded_data = {}
    
#     for i in range(max_length):
#         for col in group.columns:
#             new_col_name = f"{col}_{i + 1}"
#             if i < len(group[col]):
#                 expanded_data[new_col_name] = group[col].iloc[i]
#             else:
#                 expanded_data[new_col_name] = None  # デフォルト値はNone

#     return pd.Series(expanded_data)