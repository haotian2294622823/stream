import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
import time 
from db_util import connect_to_postgresql
from datetime import datetime
import os
import uuid
import math
import glob

from functions.dataframe_prass import df_create_by_lot_no, df_add_lot_info
from functions.charts import display_charts
from functions.column_replace import df_column_replace


def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def save_chunk_as_parquet(df_chunk, session_id, chunk_index):
    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/{session_id}_chunk_{chunk_index}.parquet"
    df_chunk.to_parquet(file_path, index=False)
    return file_path

def combine_parquet_to_csv(session_id):
    files = glob.glob(f"temp/{session_id}_chunk_*.parquet")
    dfs = []
    for f in files:
        df = pd.read_parquet(f)
        # datetime64[ns] を安全に文字列化（NaTは空白に）
        for col in df.select_dtypes(include=["datetime64[ns]"]).columns:
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S').fillna('')
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)
    csv_path = f"temp/{session_id}_combined.csv"
    combined_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    return csv_path

    combined_df = pd.concat(dfs, ignore_index=True)
    csv_path = f"temp/{session_id}_combined.csv"
    combined_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    return csv_path

def delete_session_parquet_files(session_id):
    files = glob.glob(f"temp/{session_id}_chunk_*.parquet")
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            st.warning(f"Failed to delete parquet files : {f} - {e}")

# メイン関数
def main():

    st.title("LotNo搜索")
    
    # データベース接続情報とエンジン作成
    engine = create_db_engine()
    # サイドバーでフィルタ設定を取得
    filters = sidebar_filters()

    search_button_clicked = st.sidebar.button('搜索')

    #工程別対象ロットの工程別情報
    if search_button_clicked :
        start_time=time.time()
        st.subheader('検索条件')
        st.write(filters)

        lot_flag = filters['lot_flag']

        df, error = df_create_by_lot_no(engine, filters)
        if error :
            st.error(error)
            return

        lot_no_list = df['lot_no'].tolist()
        total_lots = len(lot_no_list)
        st.write(f"対象ロット数: {total_lots}")

        # チャンクサイズ設定（メモリとの相談で調整）
        chunk_size = 1000
        
        # セッションごとにユニークなファイル名を生成（初回のみ）
        # セッションIDの生成＆管理
        if 'session_id' not in st.session_state:
            st.session_state.session_id = uuid.uuid4().hex

        # 既存のチャンクファイルは削除（任意）
        for f in glob.glob(f"temp/{st.session_state.session_id}_chunk_*.parquet"):
            os.remove(f)
        combined_csv_path = f"temp/{st.session_state.session_id}_combined.csv"
        if os.path.exists(combined_csv_path):
            os.remove(combined_csv_path)
        
        progress_bar = st.progress(0)
        total_chunks = math.ceil(total_lots / chunk_size)

        # エラーリストを初期化
        st.session_state.accumulated_error_list = []

        for chunk_index, lot_chunk in enumerate(chunk_list(lot_no_list, chunk_size), start=1):
            # チャンク単位でDBから情報取得・加工
            df_chunk = df_add_lot_info(engine, lot_chunk, lot_flag)

            selected_lang_value = filters['lang']
            df_chunk, chunk_error_list = df_column_replace(engine, selected_lang_value, df_chunk)

            # 重複を除いて累積エラーリストに追加
            combined_errors = set(st.session_state.accumulated_error_list) | set(chunk_error_list)
            st.session_state.accumulated_error_list = list(combined_errors)

            save_chunk_as_parquet(df_chunk, st.session_state.session_id, chunk_index)
            progress_bar.progress(chunk_index / total_chunks)
            st.write(f"チャンク {chunk_index}/{total_chunks} 処理済み")

        st.success("全チャンクの処理が完了しました。")

        if 'accumulated_error_list' in st.session_state:
            st.subheader("変換未設定項目:")
            st.write(st.session_state.accumulated_error_list)

        csv_path = combine_parquet_to_csv(st.session_state.session_id)
        # Parquetファイルを削除
        delete_session_parquet_files(st.session_state.session_id)
        
        # CSVファイルをバイナリで読み込み、ダウンロードボタンを作成
        with open(csv_path, "rb") as f:
            st.download_button(
                label="CSVをダウンロード",
                data=f,
                file_name="lot_info_combined.csv",
                mime="text/csv"
            )
        elapsed_time = time.time() - start_time
        st.write(f"処理時間: {elapsed_time:.2f}秒")

def create_db_engine():
    conn_pg = connect_to_postgresql()
    try:
        return create_engine('postgresql://', creator=lambda: conn_pg)
    except Exception as e:
        st.error(f"发生错误: {e}")


def sidebar_filters():
    with st.sidebar:
        st.page_link("app.py", label="首页", icon="🏠")
        st.page_link("pages/trace_start.py", label="制造数据追踪") 
 
        murata_type = st.text_input("品名")
        toko_type = st.text_input("タイプ")

        options = ["F: 成品", "W: 卷线", "T: タブレット"]
        selected_option = st.selectbox("Lot识别を選択してください:", options)
        lot_flag = selected_option.split(":")[0]
  
        lot_no = st.text_input("Lot No. ")
        machine_code = st.text_input("设备编码")
        material_lot_no = st.text_input("材料LotNo")
        worker_code = st.text_input("作业者编码")
        insp_no = st.text_input("检验No. ")
 
        today = datetime.today().date()
        default_start = today.replace(year=today.year - 2, day=1)
        start_date, end_date = st.slider(
            "生产开始日期",
            min_value=default_start,
            max_value=today,
            value=(default_start, today),
            format="YYYY/MM/DD"
        )

        lang_options = {
            "变换无": None,   # 変換なし
            "日文": "jp",     # 日本語
            "中文": "local"   # 現地語（中国語）
        }

        lang_key = st.selectbox("请选择语言", list(lang_options.keys()))
        
        return {
            'murata_type': murata_type,
            'toko_type': toko_type,
            'lot_flag' : lot_flag,
            'lot_no': lot_no,
            'machine_code': machine_code,
            'material_lot_no': material_lot_no,
            'worker_code': worker_code,
            'insp_no': insp_no,
            'start_date': start_date,
            'end_date': end_date,
            'lang' : lang_options[lang_key],
        }
   
if __name__ == "__main__":
    main()
