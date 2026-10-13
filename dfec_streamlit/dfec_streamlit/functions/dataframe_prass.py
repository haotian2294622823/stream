from sqlalchemy import  text
import pandas as pd
import time 
import streamlit as st
from .queries_prass import select_lot_no_list, select_wire_lot_no_list,select_tablet_lot_no_list
from .queries_prass import select_sl_process_data, select_lot_base_info, select_inspection_info
from .queries_prass import select_lot_defect_info, select_process_info,select_process_defect_info
from .queries_prass import select_process_machine_info, select_material_info, select_process_worker_info
from .queries_prass import select_lot_no_list_by_insp
from .queries_prass import select_temp_lot_numbers
#------------------------------------------------------
#　データ探索の起点となるデータフレーム作成
#------------------------------------------------------

# 1. 指定したロットNoからの検索/根据指定的LOT NO进行查询
def df_create_by_lot_no(engine, filters):
    with engine.connect() as connection:

        query = select_lot_no_list()
        params=(
            f"{filters['murata_type']}%", filters['murata_type'],
            f"{filters['toko_type']}%", filters['toko_type'],
            f"{filters['lot_flag']}%", filters['lot_flag'],
            filters['start_date'], 
            filters['end_date'], 
            f"{filters['lot_no']}%", filters['lot_no'],
            f"{filters['insp_no']}%", filters['insp_no'],
            f"{filters['machine_code']}%", filters['machine_code'],
            f"{filters['worker_code']}%", filters['worker_code'],
            f"{filters['material_lot_no']}%",filters['material_lot_no'],
        )

        df = pd.read_sql_query(query, connection, params=params)
        error_message = None
        if df.empty:
            error_message = "ロットNoが存在しない"
        return df, error_message

# # 2. 検印Noリストからの検索 (出荷実績検索から)/无需？
# def df_create_by_insp_no(engine, insp_list):
#     with engine.connect() as connection:

#         query = select_lot_no_list_by_insp(insp_list)
#         df = pd.read_sql_query(query, connection, params=tuple(insp_list))
#         error_message = None
#         if df.empty:
#             error_message = "ロットNoが存在しない"
#         return df, error_message
#------------------------------------------------------
# 各データフレームに情報を追記/向各数据框追加信息
#------------------------------------------------------
def df_add_lot_info(engine, lot_no_list, lot_flag):
    with engine.connect() as connection:
        start_time=time.time()
        #---------------------------------------------------------------------
        # 完成品
        #---------------------------------------------------------------------
        # 対象のロットリストから一次テーブルにLOT NOを格納する/从目标批次列表中将LOT NO存储到主表中
        connection.execute(text("CREATE TEMP TABLE temp_lot_numbers (lot_no VARCHAR);"))
        values_str = ', '.join(f"('{lot}')" for lot in lot_no_list)
        insert_query = f"INSERT INTO temp_lot_numbers (lot_no) VALUES {values_str};"  
        connection.execute(text(insert_query))

        #ロットの基礎的情報追加
        df = df_add_lot_base(connection, "FG")

        elapsed_time = time.time() - start_time
        #st.write(f"ロット基礎情報 経過時間: {elapsed_time:.2f}秒")

        #検印番号、PSロットナンバー追加
        df_add = df_add_inspection(connection, "FG")

        elapsed_time = time.time() - start_time
        #st.write(f"検印情報 経過時間: {elapsed_time:.2f}秒")

        df_pivot =  df_add.groupby('prass_lot_no').agg({
            'ps_lot_no': lambda x: ', '.join(x.dropna().unique()),  # NoneやNaNを除外
            'inspection_no': lambda x: ', '.join(x.dropna().unique()),
            'line_no': lambda x: ', '.join(x.dropna().unique()),
            'process_flow': lambda x: ', '.join(x.dropna().unique())
        }).reset_index()

        df = pd.merge(
            df,
            df_pivot,
            left_on='lot_no',       
            right_on='prass_lot_no',  
            how='left'             # 左外部結合。必要に応じて変更。
        ) 
        df.drop(columns=['prass_lot_no'], inplace=True)

        # LOT NOでの各不良モードの不良数合計/按LOT NO统计各不良项目的不良数
        df_add = df_add_defect(connection, "FG")

        elapsed_time = time.time() - start_time
        #st.write(f"不良情報 経過時間: {elapsed_time:.2f}秒")

        df_pivot = df_add.pivot_table(
                index='lot_no', 
                columns='defect_code', 
                values='all_defect_qty', 
                aggfunc='sum', 
                fill_value=0
        ).reset_index()

        df_pivot.columns = [f"all_{col}" 
            if col != 'lot_no' else col for col in df_pivot.columns]

        df = pd.merge(
            df,
            df_pivot,
            left_on='lot_no',       
            right_on='lot_no',  
            how='left'             # 左外部結合。必要に応じて変更。
        ) 

        # 工程別情報
        df_add = df_add_process(connection, "FG")
 
        elapsed_time = time.time() - start_time
        #st.write(f"工程情報 経過時間: {elapsed_time:.2f}秒")

        df_pivot = df_add.pivot_table(
            index='lot_no',           
            columns='process_code',   
            values=['start_datetime', 'finish_datetime', 'duration_minutes', 'input_qty', 'output_qty'],
            aggfunc='first'            
        ).reset_index()

        df_pivot.columns = [f"{col[1]}_{col[0]}" if col[0] != '' else col[0] for col in df_pivot.columns]
  
        df = pd.merge(
            df,
            df_pivot,
            left_on='lot_no',       
            right_on='_lot_no',  
            how='left'             # 左外部結合。必要に応じて変更。
        ) 
        df = df.drop(columns=['_lot_no'])

        # 工程別情報
        df_add = df_add_process_defect(connection, "FG")

        elapsed_time = time.time() - start_time
        #st.write(f"工程不良情報 経過時間: {elapsed_time:.2f}秒")

        df_pivot = df_add.pivot_table(
            index='lot_no',           
            columns='process_defect_mode',
            values='defect_qty',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        df_pivot.columns = [f"{col}_defect_qty" 
            if col != 'lot_no' else col for col in df_pivot.columns]

        df = pd.merge(
            df,
            df_pivot,
            left_on='lot_no',       
            right_on='lot_no',  
            how='left'
        ) 

        # 工程別設備
        df_add = df_add_process_machine(connection, "FG")

        elapsed_time = time.time() - start_time
        #st.write(f"工程設備情報 経過時間: {elapsed_time:.2f}秒")

        df_pivot = df_add.pivot_table(
            index='lot_no',            
            columns='process_code',   
            values='machine_code',
            aggfunc=lambda x: ', '.join(str(i) for i in x if pd.notnull(i)) 
        ).reset_index()

        df_pivot.columns = [f"{col}_machine" 
            if col != 'lot_no' else col for col in df_pivot.columns]
        
        df = pd.merge(
            df,
            df_pivot,
            left_on='lot_no',       
            right_on='lot_no',  
            how='left' 
        ) 

        # 工程別材料
        df_add = df_add_process_material(connection, "FG")

        elapsed_time = time.time() - start_time
        #st.write(f"工程材料情報 経過時間: {elapsed_time:.2f}秒")

        df_pivot = df_add.pivot_table(
            index='lot_no', 
            columns='material_class_code', 
            values='material_lot_no',   
            aggfunc=lambda x: ', '.join(str(i) for i in x if pd.notnull(i))  
        ).reset_index()

        df_pivot.columns = [f"mtl_code_{col}" 
                if col != 'lot_no' else col for col in df_pivot.columns]

        df = pd.merge(
            df,
            df_pivot,
            left_on='lot_no',       
            right_on='lot_no',  
            how='left' 
        ) 

        # 各工程作業者
        df_add = df_add_process_worker(connection, "FG")

        elapsed_time = time.time() - start_time
        #st.write(f"工程作業者情報 経過時間: {elapsed_time:.2f}秒")
       
        df_pivot = df_add.pivot_table(
            index='lot_no', 
            columns='process_code',  
            values='worker_info',
            aggfunc=lambda x: ', '.join(str(i) for i in x if pd.notnull(i))  
        ).reset_index()
        
        df_pivot.columns = [f"{col}_worker" 
                if col != 'lot_no' else col for col in df_pivot.columns]

        df = pd.merge(
            df,
            df_pivot,
            left_on='lot_no',       
            right_on='lot_no',  
            how='left'   
        )
        elapsed_time = time.time() - start_time
        #st.write(f"作業者マージ 経過時間: {elapsed_time:.2f}秒")

        if lot_flag == "F":
            #---------------------------------------------------------------------
            # 巻線工程
            #---------------------------------------------------------------------
            query = select_wire_lot_no_list()
            df_wire_lot = pd.read_sql_query(query, connection) 
            # Lot_no リスト取得
            wire_lot_list = df_wire_lot['wire_lot_no'].tolist()

            connection.execute(text("CREATE TEMP TABLE temp_wire_lots (lot_no VARCHAR);"))
            values_str = ', '.join(f"('{lot}')" for lot in wire_lot_list)
            insert_query = f"INSERT INTO temp_wire_lots (lot_no) VALUES {values_str};"  
            connection.execute(text(insert_query))

            #巻線ロットの基礎情報
            df_add = df_add_lot_base(connection, "WIRE")

            elapsed_time = time.time() - start_time
            #st.write(f"巻線ロット情報 経過時間: {elapsed_time:.2f}秒")

            #既に存在する不要な列を削除
            df_add.drop(columns=['toko_type', 'murata_type'], inplace=True)
            df_add.columns = ['E010_' + col for col in df_add.columns]

            print(df.columns)
            # # 检查 mtl_code_E010 是否存在
            # if 'mtl_code_E010' not in df.columns:
            #     raise KeyError(f"Column 'mtl_code_E010' not found in df. Available columns: {df.columns}")

            df = pd.merge(
                df,
                df_add,
                left_on='mtl_code_2110',       
                right_on='E010_lot_no',  
                how='left'   
            )

            #巻線ロットの不良情報
            df_add = df_add_defect(connection, "WIRE")

            elapsed_time = time.time() - start_time
            #st.write(f"巻線不良情報 経過時間: {elapsed_time:.2f}秒")

            df_pivot = df_add.pivot_table(
                    index='lot_no', 
                    columns='defect_code', 
                    values='all_defect_qty', 
                    aggfunc='sum', 
                    fill_value=0
            ).reset_index()

            df_pivot.columns = [f"E010_{col}_defect_qty" 
                if col != 'lot_no' else "E010_lot_no_x" for col in df_pivot.columns
            ]
            
            df = pd.merge(
                df,
                df_pivot,
                left_on='mtl_code_2110',       
                right_on='E010_lot_no_x',  
                how='left'
            ) 
            df.drop(columns=['E010_lot_no_x'], inplace=True)

            # 巻線設備
            df_add = df_add_process_machine(connection, "WIRE")

            elapsed_time = time.time() - start_time
            #st.write(f"巻線設備情報 経過時間: {elapsed_time:.2f}秒")

            df_pivot = df_add.pivot_table(
                index='lot_no',            
                columns='process_code',   
                values='machine_code',
                aggfunc=lambda x: ', '.join(str(i) for i in x if pd.notnull(i)) 
            ).reset_index()

            df_pivot.columns = [f"{col}_machine" 
                if col != 'lot_no' else "E010_lot_no_x" for col in df_pivot.columns]

            df = pd.merge(
                df,
                df_pivot,
                left_on='mtl_code_2110',       
                right_on='E010_lot_no_x',   
                how='left' 
            ) 
            df.drop(columns=['E010_lot_no_x'], inplace=True)

            # 巻線材料
            df_add = df_add_process_material(connection, "WIRE")

            elapsed_time = time.time() - start_time
            #st.write(f"巻線材料情報 経過時間: {elapsed_time:.2f}秒")

            df_pivot = df_add.pivot_table(
                index='lot_no', 
                columns='material_class_code', 
                values='material_lot_no',   
                aggfunc=lambda x: ', '.join(str(i) for i in x if pd.notnull(i))  
            ).reset_index()

            df_pivot.columns = [f"E010_mtl_code_{col}" 
                if col != 'lot_no' else "E010_lot_no_x" for col in df_pivot.columns]

            df = pd.merge(
                df,
                df_pivot,
                left_on='mtl_code_2110',       
                right_on='E010_lot_no_x',  
                how='left' 
            ) 
            df.drop(columns=['E010_lot_no_x'], inplace=True)

            # 各工程作業者
            df_add = df_add_process_worker(connection, "WIRE")

            elapsed_time = time.time() - start_time
            #st.write(f"巻線作業者情報 経過時間: {elapsed_time:.2f}秒")
        
            df_pivot = df_add.pivot_table(
                index='lot_no', 
                columns='process_code',  
                values='worker_info',
                aggfunc=lambda x: ', '.join(str(i) for i in x if pd.notnull(i))  
            ).reset_index()
            
            df_pivot.columns = [f"{col}_worker" 
                if col != 'lot_no' else "E010_lot_no_x" for col in df_pivot.columns]

            df = pd.merge(
                df,
                df_pivot,
                left_on='mtl_code_2110',       
                right_on='E010_lot_no_x',  
                how='left'   
            )
            df.drop(columns=['E010_lot_no_x'], inplace=True)

            #加工条件 didis
            # lot_no の一覧
            # lot_nos = df['mtl_code_G121'].dropna().unique().tolist()

            # prass_lot_daily_ins から一括取得
            # query = """
            # SELECT lot_no, process_code, daily_ins_id, ins_value
            # FROM public.prass_lot_daily_ins
            # WHERE lot_no = ANY(%s)
            # ORDER BY lot_no, process_code, daily_ins_id
            # """
            # prass_df = pd.read_sql(query, connection, params=(lot_nos,))

            # # daily_ins_id を列に展開（pivot）
            # pivot_df = prass_df.pivot_table(index='lot_no', columns=['process_code', 'daily_ins_id'], values='ins_value')

            # # カラム名を "didis_<daily_ins_id>" 形式に変更
            # pivot_df.columns = [f"{process_code}_{daily_ins_id}_didis" for process_code, daily_ins_id in pivot_df.columns]

            # # lot_no を index から列に
            # pivot_df.reset_index(inplace=True)
            # pivot_df.rename(columns={'lot_no': 'E010_lot_no_x'}, inplace=True)
            
            # # 元 df に結合
            # df = pd.merge(
            #     df,
            #     pivot_df,
            #     left_on='mtl_code_G121',       
            #     right_on='E010_lot_no_x',  
            #     how='left'   
            # )
            # df.drop(columns=['E010_lot_no_x'], inplace=True)
            
            # elapsed_time = time.time() - start_time
            #st.write(f"DIDISデータ結合 経過時間: {elapsed_time:.2f}秒")

            #加工条件 PMI

            # prass_lot_daily_ins から一括取得
            # query = """
            # SELECT 
            #     lot_no AS e010_lot_no_y,
            #     e010_pmi_chuck_temp,
            #     e010_pmi_core_diameter,
            #     e010_pmi_program_no,
            #     e010_pmi_turn_count,
            #     e010_pmi_sending_amount,
            #     e010_pmi_wire_speed,
            #     e010_pmi_fusion_time,
            #     e010_pmi_flow_rate,
            #     e010_pmi_wire_stop_position,
            #     e010_pmi_wire_tension,
            #     e010_pmi_backend_tension,
            #     e010_pmi_wire_height_1,
            #     e010_pmi_wire_height_2,
            #     e010_pmi_wire_height_3,
            #     e010_pmi_wire_height_4,
            #     e010_pmi_wire_height_5,
            #     e010_pmi_wire_out_dia_1,
            #     e010_pmi_wire_out_dia_2,
            #     e010_pmi_wire_out_dia_3,
            #     e010_pmi_wire_out_dia_4,
            #     e010_pmi_wire_out_dia_5,
            #     e010_pmi_machine_pressure
            # FROM public.prass_lot_wire_machine
            # WHERE lot_no = ANY(%s)
            # """
            # prass_df = pd.read_sql(query, connection, params=(lot_nos,))
            # # 元 df に結合
            # df = pd.merge(
            #     df,
            #     prass_df,
            #     left_on='mtl_code_G121',       
            #     right_on='e010_lot_no_y',  
            #     how='left'   
            # )
            # df.drop(columns=['e010_lot_no_y'], inplace=True)
        

            # elapsed_time = time.time() - start_time
            #st.write(f"DIDISデータ結合 経過時間: {elapsed_time:.2f}秒")

            #---------------------------------------------------------------------
            # タブレット成形工程/板块成型工程
            #---------------------------------------------------------------------
            query = select_tablet_lot_no_list()

            df_tablet_lot = pd.read_sql_query(query, connection) 
            # Lot_no リスト取得
            tablet_lot_list = df_tablet_lot['tab_lot_no'].tolist()
            # 一時テーブルの作成 巻線ロット
            connection.execute(text("CREATE TEMP TABLE temp_tablet_lots (lot_no VARCHAR);"))
            values_str = ', '.join(f"('{lot}')" for lot in tablet_lot_list)
            insert_query = f"INSERT INTO temp_tablet_lots (lot_no) VALUES {values_str};"  
            connection.execute(text(insert_query))

            #タブレットロットの基礎情報
            df_add = df_add_lot_base(connection, "TABLET")

            elapsed_time = time.time() - start_time
            #st.write(f"タブレットロット情報 経過時間: {elapsed_time:.2f}秒")

            #既に存在する不要な列を削除
            df_add.drop(columns=['toko_type', 'murata_type'], inplace=True)
            df_add.columns = ['E020_XXX_' + col for col in df_add.columns]

            # G122からG129までの処理を繰り返す
            for i in range(122, 130):
                column_name = f'mtl_code_G{i}'   # mtl_code_G122～G129
                new_tablet_column_prefix = f'G110_G{i}' # tablet_G122～G129

                if column_name in df.columns:
                    df = pd.merge(
                        df,
                        df_add,
                        left_on=column_name,     
                        right_on='G110_XXX_lot_no',  
                        how='left'   
                    )
                    df.rename(columns=lambda x: x.replace('G110_XXX', new_tablet_column_prefix) 
                            if x.startswith('G110_XXX') else x, inplace=True)
                
            #タブレットロットの不良情報/TABLET LOT 不良信息
            df_add = df_add_defect(connection, "TABLET")
            elapsed_time = time.time() - start_time
            #st.write(f"タブレット不良情報 経過時間: {elapsed_time:.2f}秒")

            if not df_add.empty:
                df_pivot = df_add.pivot_table(
                        index='lot_no', 
                        columns='defect_code', 
                        values='all_defect_qty', 
                        aggfunc='sum', 
                        fill_value=0
                ).reset_index()

                df_pivot.columns = ['G110_XXX_' + str(col) if col != 'lot_no' else 'G110_lot_no_x' for col in df_pivot.columns]         

                # G122からG129までの処理を繰り返す
                for i in range(122, 130):
                    column_name = f'mtl_code_G{i}'   # mtl_code_G122～G129
                    new_tablet_column_prefix = f'G110_G{i}' # tablet_G122～G129

                    if column_name in df.columns:
                        df = pd.merge(
                            df,
                            df_pivot,
                            left_on=column_name,     
                            right_on='G110_lot_no_x',  
                            how='left'   
                        )
                        df.rename(columns=lambda x: x.replace('G110_XXX', new_tablet_column_prefix) 
                                if x.startswith('G110_XXX') else x, inplace=True)
                        # G110_lot_no_x が存在する場合のみ削除
                        if 'G110_lot_no_x' in df.columns:
                            df.drop(columns=['G110_lot_no_x'], inplace=True)

            #タブレットロットの設備情報
            df_add = df_add_process_machine(connection, "TABLET")
            elapsed_time = time.time() - start_time
            #st.write(f"タブレット設備情報 経過時間: {elapsed_time:.2f}秒")

            if not df_add.empty:
                df_pivot = df_add.pivot_table(
                    index='lot_no',            
                    columns='process_code',   
                    values='machine_code',
                    aggfunc=lambda x: ', '.join(str(i) for i in x if pd.notnull(i)) 
                ).reset_index()

                df_pivot.columns = [str(col) + '_XXX_' + 'machine' if col != 'lot_no' else 'G110_lot_no_x' for col in df_pivot.columns]

                # G122からG129までの処理を繰り返す
                for i in range(122, 130):
                    column_name = f'mtl_code_G{i}'   # mtl_code_G122～G129
                    new_tablet_column_prefix = f'G110_G{i}' # tablet_G122～G129

                    if column_name in df.columns:
                        df = pd.merge(
                            df,
                            df_pivot,
                            left_on=column_name,     
                            right_on='G110_lot_no_x',  
                            how='left',
                        ) 
                    
                        # G110_lot_no_x が存在する場合のみ削除
                        if 'G110_lot_no_x' in df.columns:
                            df.drop(columns=['G110_lot_no_x'], inplace=True)
                        df.rename(columns=lambda x: x.replace('G110_XXX', new_tablet_column_prefix) 
                                if x.startswith('G110_XXX') else x, inplace=True)

            #タブレットロットの材料情報
            df_add = df_add_process_material(connection, "TABLET")
            elapsed_time = time.time() - start_time
            #st.write(f"タブレット材料情報 経過時間: {elapsed_time:.2f}秒")

            if not df_add.empty:
                df_pivot = df_add.pivot_table(
                    index='lot_no', 
                    columns='material_class_code', 
                    values='material_lot_no',   
                    aggfunc=lambda x: ', '.join(str(i) for i in x if pd.notnull(i))  
                ).reset_index()

                df_pivot.columns = ['G110_XXX_' + 'mtl_code_' + str(col)  if col != 'lot_no' else 'G110_lot_no_x' for col in df_pivot.columns]         

                # G122からG129までの処理を繰り返す
                for i in range(122, 130):
                    column_name = f'mtl_code_G{i}'   # mtl_code_G122～G129
                    new_tablet_column_prefix = f'G110_G{i}' # tablet_G122～G129

                    if column_name in df.columns:
                        df = pd.merge(
                            df,
                            df_pivot,
                            left_on=column_name,     
                            right_on='G110_lot_no_x',  
                            how='left',
                        ) 
                        
                        # G110_lot_no_x が存在する場合のみ削除
                        if 'G110_lot_no_x' in df.columns:
                            df.drop(columns=['G110_lot_no_x'], inplace=True)
                        df.rename(columns=lambda x: x.replace('G110_XXX', new_tablet_column_prefix) 
                                if x.startswith('G110_XXX') else x, inplace=True)

            #タブレットロットの作業者情報
            df_add = df_add_process_worker(connection, "TABLET")

            elapsed_time = time.time() - start_time
            #st.write(f"タブレット作業者情報 経過時間: {elapsed_time:.2f}秒")

            if not df_add.empty:
                df_pivot = df_add.pivot_table(
                    index='lot_no', 
                    columns='process_code',  
                    values='worker_info',
                    aggfunc=lambda x: ', '.join(str(i) for i in x if pd.notnull(i))  
                ).reset_index()

                df_pivot.columns = ['G110_XXX_' + str(col) + '_worker' if col != 'lot_no' else 'G110_lot_no_x' for col in df_pivot.columns]         

                # G122からG129までの処理を繰り返す
                for i in range(122, 130):
                    column_name = f'mtl_code_G{i}'   # mtl_code_G122～G129
                    new_tablet_column_prefix = f'G110_G{i}' # tablet_G122～G129

                    if column_name in df.columns:
                        df = pd.merge(
                            df,
                            df_pivot,
                            left_on=column_name,     
                            right_on='G110_lot_no_x',  
                            how='left',
                        ) 
                        
                        # G110_lot_no_x が存在する場合のみ削除
                        if 'G110_lot_no_x' in df.columns:
                            df.drop(columns=['G110_lot_no_x'], inplace=True)
                        df.rename(columns=lambda x: x.replace('G110_XXX', new_tablet_column_prefix) 
                                if x.startswith('G110_XXX') else x, inplace=True)
                elapsed_time = time.time() - start_time
            # st.write(f"タブレット作業者マージ 経過時間: {elapsed_time:.2f}秒")
                
            #---------------------------------------------------------------------
            # SL材製造データ/SL材料制造数据
            #---------------------------------------------------------------------
            query = select_sl_process_data()
            df_sl_lots = pd.read_sql_query(query, connection)
            df_sl_selected = df_sl_lots[
                [
                    'product_lot_no', 
                    'sl_lot_no', 
                    'sl_p1_user', 
                    'sl_p1_start_date', 
                    'sl_p1_end_date', 
                    'sl_p1_m1_item',
                    'sl_p1_m1_lot',
                    'sl_p1_m1_weight',
                    'sl_p1_m2_item',
                    'sl_p1_m2_lot',
                    'sl_p1_m2_weight',
                    'sl_p1_m3_item',
                    'sl_p1_m3_lot',
                    'sl_p1_m3_weight',
                    'sl_p1_m4_item',
                    'sl_p1_m4_lot',
                    'sl_p1_m4_weight',
                    'sl_p1_m5_item',
                    'sl_p1_m5_lot',
                    'sl_p1_m5_weight',
                    'sl_p1_c1_item',
                    'sl_p1_c1_lot',
                    'sl_p1_c1_weight',
                    'sl_p1_memo',
                    'sl_p2_machine',
                    'sl_p2_user',
                    'sl_p2_start_date',
                    'sl_p2_end_date',
                    'sl_p2_end_weight',
                    'sl_p2_memo',
                    'sl_p2_kiln_temp',
                    'sl_p2_n2_flow_g_axis',
                    'sl_p2_n2_flow_m_axis',
                    'sl_p3_machine',
                    'sl_p3_user',
                    'sl_p3_start1_date',
                    'sl_p3_start2_date',
                    'sl_p3_start3_date',
                    'sl_p3_start4_date',
                    'sl_p3_start5_date',
                    'sl_p3_start6_date',
                    'sl_p3_start7_date',
                    'sl_p3_start8_date',
                    'sl_p3_start9_date',
                    'sl_p3_start10_date',
                    'sl_p3_end_date',
                    'sl_p3_end_weight',
                    'sl_p3_dispose_weight',
                    'sl_p3_memo',
                    'sl_p4_machine',
                    'sl_p4_user',
                    'sl_p4_start_date',
                    'sl_p4_end_date',
                    'sl_p4_bat1_weight',
                    'sl_p4_bat2_weight',
                    'sl_p4_bat3_weight',
                    'sl_p4_bat4_weight',
                    'sl_p4_end_weight',
                    'sl_p4_hardness',
                    'sl_p4_memo',
                    'sl_p5_machine',
                    'sl_p5_user',
                    'sl_p5_start_date',
                    'sl_p5_end_date',
                    'sl_p5_cnt',
                    'sl_p5_end_weight',
                    'sl_p5_dispose_weight',
                    'sl_p5_memo',
                    'sl_p6_machine',
                    'sl_p6_user',
                    'sl_p6_start_date',
                    'sl_p6_end_date',
                    'sl_p6_end_weight',
                    'sl_p6_m1_item',
                    'sl_p6_m1_lot',
                    'sl_p6_m1_weight',
                    'sl_p6_memo',
                    'sl_p7_user',
                    'sl_p7_start_date',
                    'sl_p7_end_date',
                    'sl_p7_p1_weight',
                    'sl_p7_p2_weight',
                    'sl_p7_samp1_weight',
                    'sl_p7_samp2_weight',
                    'sl_p7_memo',
                ]
            ]
            # 各 product_lot_no ごとの sl_lot_no の出現回数をカウントし、その最大値を取得/统计每个product_lot_no对应的sl_lot_no出现次数，并获取其最大值
            max_occurrences = df_sl_selected.groupby('product_lot_no')['sl_lot_no'].count().max()
            df_expanded = df_sl_selected.groupby('product_lot_no').apply(expand_grouped_columns, max_occurrences).reset_index()

            df = pd.merge(
                        df,
                        df_expanded,
                        left_on='lot_no',     
                        right_on='product_lot_no',  
                        how='left',
                )
            df.drop(columns=[col for col in df.columns if col.startswith('product_lot_no')], inplace=True)
            elapsed_time = time.time() - start_time
            #st.write(f"SL材工程データ結合 経過時間: {elapsed_time:.2f}秒")

            #---------------------------------------------------------------------
            # # SL材冷凍、解凍データ
            # #---------------------------------------------------------------------
            # query = select_sl_unfreezelog_data()
            # df_sl_lots = pd.read_sql_query(query, connection)
            # df_sl_selected = df_sl_lots[
            #     [
            #         'product_lot_no',
            #         'sl_lot_no',
            #         'sl_u_lot_no',
            #         'sl_u_ware_housing_time',
            #         'sl_u_weight',
            #         'sl_u_datetime_out_of_fridge',
            #         'sl_u_freezing_hours',
            #         'sl_u_unfreeze_user',
            #         'sl_u_assigned_machine1',
            #         'sl_u_assigned_machine2',
            #         'sl_u_assigned_machine3',
            #         'sl_u_assigned_time',
            #         'sl_u_unfreezing_hours',
            #     ]
            # ]

            # # machine 1-3をカンマ区切りで1カラムに結合（Noneの場合は結合しない）
            # df_sl_selected['sl_u_assigned_machines'] = df_sl_selected[
            #     ['sl_u_assigned_machine1', 'sl_u_assigned_machine2', 'sl_u_assigned_machine3']
            # ].fillna('').agg(lambda x: ','.join(filter(None, x)), axis=1)
            # df_sl_selected = df_sl_selected.drop(
            #     columns=['sl_u_assigned_machine1', 'sl_u_assigned_machine2', 'sl_u_assigned_machine3']
            # )
            # # 各 product_lot_no ごとの sl_lot_no の出現回数をカウントし、その最大値を取得
            # max_occurrences = df_sl_selected.groupby('product_lot_no')['sl_lot_no'].count().max()
            # df_expanded = df_sl_selected.groupby('product_lot_no').apply(expand_grouped_columns, max_occurrences).reset_index()
            # df_expanded.drop(columns=[col for col in df_expanded.columns if col.startswith('sl_lot_no')], inplace=True)

            # df = pd.merge(
            #             df,
            #             df_expanded,
            #             left_on='lot_no',     
            #             right_on='product_lot_no',  
            #             how='left',
            #     )
            # df.drop(columns=[col for col in df.columns if col.startswith('product_lot_no')], inplace=True)
            # elapsed_time = time.time() - start_time
            # #st.write(f"SL材冷凍、解凍データ結合 経過時間: {elapsed_time:.2f}秒")

        #---------------------------------------------------------------------
        # # 加工条件　DIDISから
        # # ---------------------------------------------------------------------
        # # lot_no の一覧
        # lot_nos = df['lot_no'].dropna().unique().tolist()

        # # prass_lot_daily_ins から一括取得
        # query = """
        # SELECT lot_no, process_code, daily_ins_id, ins_value
        # FROM public.prass_lot_daily_ins
        # WHERE lot_no = ANY(%s)
        # ORDER BY lot_no, process_code, daily_ins_id
        # """
        # prass_df = pd.read_sql(query, connection, params=(lot_nos,))

        # # daily_ins_id を列に展開（pivot）
        # pivot_df = prass_df.pivot_table(index='lot_no', columns=['process_code', 'daily_ins_id'], values='ins_value')

        # # カラム名を "didis_<daily_ins_id>" 形式に変更
        # pivot_df.columns = [f"{process_code}_{daily_ins_id}_didis" for process_code, daily_ins_id in pivot_df.columns]

        # # lot_no を index から列に
        # pivot_df.reset_index(inplace=True)

        # # 元 df に結合
        # df = df.merge(pivot_df, on='lot_no', how='left')
        
        # elapsed_time = time.time() - start_time
        # # st.write(f"DIDISデータ結合 経過時間: {elapsed_time:.2f}秒")

        #---------------------------------------------------------------------
        # 加工条件　PRASSから
        # ---------------------------------------------------------------------
        # lot_no の一覧
        lot_nos = df['lot_no'].dropna().unique().tolist()

        # prass_lot_daily_ins から一括取得
        query = """
        SELECT noc0027 as lot_no , streamlit_item, dhc1578
        FROM public.pth8031
        WHERE noc0027 = ANY(%s)
        ORDER BY noc0027, streamlit_item
        """
        prass_df = pd.read_sql(query, connection, params=(lot_nos,))
        prass_df['dhc1578'] = prass_df['dhc1578'].apply(to_float_or_original)
        # daily_ins_id を列に展開（pivot）
        pivot_df = prass_df.pivot_table(
            index='lot_no',        # 行は lot_no
            columns='streamlit_item',  # 列は streamlit_item 名
            values='dhc1578',      # セルの値は dhc1578
            aggfunc='first'        # 同一セルに複数値ある場合は最初の値
        )
        # カラム名を "didis_<daily_ins_id>" 形式に変更
        pivot_df.columns = [str(col) for col in pivot_df.columns]
        # lot_no を index から列に
        pivot_df.reset_index(inplace=True)

        # 元 df に結合
        df = df.merge(pivot_df, on='lot_no', how='left')
        
        elapsed_time = time.time() - start_time
        # st.write(f"DIDISデータ結合 経過時間: {elapsed_time:.2f}秒")

        if lot_flag == "W":
            # ---------------------------------------------------------------------
            # 巻線加工条件　PMIから
            # ---------------------------------------------------------------------
            # lot_no の一覧
            lot_nos = df['lot_no'].dropna().unique().tolist()

            # # prass_lot_daily_ins から一括取得
            # query = """
            # SELECT 
            #     lot_no ,
            #     e010_pmi_chuck_temp,
            #     e010_pmi_core_diameter,
            #     e010_pmi_program_no,
            #     e010_pmi_turn_count,
            #     e010_pmi_sending_amount,
            #     e010_pmi_wire_speed,
            #     e010_pmi_fusion_time,
            #     e010_pmi_flow_rate,
            #     e010_pmi_wire_stop_position,
            #     e010_pmi_wire_tension,
            #     e010_pmi_backend_tension,
            #     e010_pmi_wire_height_1,
            #     e010_pmi_wire_height_2,
            #     e010_pmi_wire_height_3,
            #     e010_pmi_wire_height_4,
            #     e010_pmi_wire_height_5,
            #     e010_pmi_wire_out_dia_1,
            #     e010_pmi_wire_out_dia_2,
            #     e010_pmi_wire_out_dia_3,
            #     e010_pmi_wire_out_dia_4,
            #     e010_pmi_wire_out_dia_5,
            #     e010_pmi_machine_pressure
            # FROM public.prass_lot_wire_machine
            # WHERE lot_no = ANY(%s)
            # """
            # prass_df = pd.read_sql(query, connection, params=(lot_nos,))

            # # 元 df に結合
            # df = df.merge(prass_df, on='lot_no', how='left')
            
            # elapsed_time = time.time() - start_time
            # #st.write(f"DIDISデータ結合 経過時間: {elapsed_time:.2f}秒")

        return df

#------------------------------------------------------
# LOT NOに関する基礎的なデータ追加 
#------------------------------------------------------
def df_add_lot_base(connection, category) :    
    query = select_lot_base_info(category)
    df = pd.read_sql_query(query, connection) 
    return(df)


#------------------------------------------------------
# 検印番号、PSロット
#------------------------------------------------------
def df_add_inspection(connection, category) : 
    query =select_inspection_info(category)
    df = pd.read_sql_query(query, connection) 
    return(df)

#------------------------------------------------------
# 不良項目別、不良数追加 
#------------------------------------------------------
def df_add_defect(connection, category) :
    query = select_lot_defect_info(category)
    df = pd.read_sql_query(query, connection) 
    return(df)

#------------------------------------------------------
# 工程情報 
#------------------------------------------------------
def df_add_process(connection, category) :
    query = select_process_info(category)
    df = pd.read_sql_query(query, connection)
    return(df)


#------------------------------------------------------
# 工程別不良情報 
#------------------------------------------------------
def df_add_process_defect(connection, category) :
    query = select_process_defect_info(category)
    df = pd.read_sql_query(query, connection)
    return(df)

#------------------------------------------------------
# 工程設備情報 
#------------------------------------------------------
def df_add_process_machine(connection, category) :
    query = select_process_machine_info(category)
    df = pd.read_sql_query(query, connection)
    return(df)

#------------------------------------------------------
# 工程材料情報 
#------------------------------------------------------
def df_add_process_material(connection, category) :
    query = select_material_info(category)
    df = pd.read_sql_query(query, connection)
    return(df)

#------------------------------------------------------
# 工程作業者情報 
#------------------------------------------------------
def df_add_process_worker(connection, category) :
    query = select_process_worker_info(category)
    df = pd.read_sql_query(query, connection) 
    return(df)


# データフレームをグループ化し、サフィックス付きで展開する関数定義
def expand_grouped_columns(group, max_length):

    # サフィックス付きカラム名生成と初期化
    expanded_data = {}
    
    for i in range(max_length):
        for col in group.columns:
            new_col_name = f"{col}_{i + 1}"
            if i < len(group[col]):
                expanded_data[new_col_name] = group[col].iloc[i]
            else:
                expanded_data[new_col_name] = None  # デフォルト値はNone

    return pd.Series(expanded_data)

#数値化できればfloat、できなければ元の値を返す
def to_float_or_original(val):
    try:
        # Noneや空文字はそのまま返す
        if val is None or str(val).strip() == "":
            return val
        return float(val)
    except (ValueError, TypeError):
        return val