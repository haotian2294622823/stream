from sqlalchemy import  text
import pandas as pd
import time 
import streamlit as st
import fnmatch

#------------------------------------------------------
#　カラムの置換
#------------------------------------------------------

# データフレームの列名置換
def df_column_replace(engine, lang,  df):
    with engine.connect() as connection:
        query = """
        SELECT column_name, description_jp, description_local, data_type
        FROM public.streamlit_column_list;
        """

        column_info_df = pd.read_sql(query, engine)

        rename_mapping = {}
        not_renamed_columns = [] 

        for index, row in column_info_df.iterrows():
            if lang == "jp":
                rename_mapping[row['column_name']] = (row['description_jp'],row['data_type'])
            elif  lang == "local" :
                rename_mapping[row['column_name']] = (row['description_local'],row['data_type'])

        for col in df.columns:
            renamed = False
            
            for pattern, (replacement, data_type) in rename_mapping.items():
                if fnmatch.fnmatch(col, pattern):  # ワイルドカードマッチング
                    new_col_name = replacement.replace('*', col.split('_')[-1])  # 元のカラムから番号部分を取得して置き換え
                    new_col_name = f"{new_col_name}_{data_type}"
                    df.rename(columns={col: new_col_name}, inplace=True)
                    renamed = True
                    break
                
            if not renamed:
                not_renamed_columns.append(col)  # 変換できなかったカラム名を追加

        return df, not_renamed_columns 

