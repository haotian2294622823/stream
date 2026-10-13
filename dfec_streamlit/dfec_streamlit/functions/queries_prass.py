
#条件にみあう完成品ロット一覧の取得
def select_lot_no_list():
    return  """
        SELECT
            DISTINCT t1.lot_no 
        FROM 
            prass_lot t1
        LEFT JOIN prass_lot_inspection t2 ON t2.prass_lot_no = t1.lot_no
        LEFT JOIN prass_process_machine t3 ON t3.lot_no = t1.lot_no
        LEFT JOIN prass_process_worker t4 ON t4.lot_no = t1.lot_no
        LEFT JOIN prass_process_material t5 ON t5.lot_no = t1.lot_no
        WHERE (t1.murata_type LIKE %s OR %s = '')
            AND (t1.toko_type LIKE %s OR %s = '')
            AND (t1.lot_flag LIKE %s OR %s = '')
            AND t1.start_datetime >= %s 
            AND t1.start_datetime <= %s 
            AND (t1.lot_no LIKE %s OR %s = '')
            AND (t2.inspection_no LIKE %s OR %s = '')
            AND (t3.machine_code LIKE %s OR %s = '')
            AND (t4.worker_code LIKE %s OR %s = '')
            AND (t5.material_lot_no LIKE %s OR %s = '')
        ORDER BY t1.lot_no
    """
def select_lot_no_list_by_insp(insp_list):
    # insp_list が空でない場合に備えて、プレースホルダの数だけ '?' を作成
    placeholders = ', '.join(['%s'] * len(insp_list))
    query = f"""
        SELECT DISTINCT t1.lot_no 
        FROM prass_lot t1
        LEFT JOIN prass_lot_inspection t2 ON t2.prass_lot_no = t1.lot_no
        WHERE t2.inspection_no IN ({placeholders})
        ORDER BY t1.lot_no
    """
    return query
#temp_lot_numbers一覧の取得
def select_temp_lot_numbers():
    return """
        SELECT lot_no FROM "temp_lot_numbers"
    """
#巻線ロット一覧の取得
def select_wire_lot_no_list():
    return """
        SELECT   
            t1.material_lot_no AS wire_lot_no
        FROM prass_process_material t1
        INNER JOIN (SELECT lot_no FROM "temp_lot_numbers") t2 ON t2.lot_no = t1.lot_no
        WHERE t1.material_class_code >= '2110'
            AND t1.material_class_code <= '2113'
    """
#タブレット成型ロット一覧の取得
def select_tablet_lot_no_list():
    return """
        SELECT   
            t1.material_lot_no AS tab_lot_no
        FROM prass_process_material t1
        INNER JOIN (SELECT lot_no FROM "temp_lot_numbers") t2 ON t2.lot_no = t1.lot_no   
        WHERE t1.material_class_code >= '0300'
            AND t1.material_class_code < '0403'
    """
# #SL材工程データの取得
def select_sl_process_data():
    return """
        WITH product_sl_comb AS (
            SELECT 
                t1.lot_no AS product_lot_no
            FROM 
                prass_process_material t1
            LEFT JOIN prass_process_material t2 ON t1.material_lot_no = t2.lot_no
            WHERE EXISTS (SELECT 1 FROM temp_lot_numbers t4 WHERE t4.lot_no = t1.lot_no)
            GROUP BY
                t1.lot_no
        )
        SELECT 
            pl.product_lot_no,
            pl.sl_lot_no,
            sp.sl_p1_user,
            sp.sl_p1_start_date,
            sp.sl_p1_end_date,
            sp.sl_p1_m1_item,
            sp.sl_p1_m1_lot,
            sp.sl_p1_m1_weight,
            sp.sl_p1_m1_unit,
            sp.sl_p1_m2_item,
            sp.sl_p1_m2_lot,
            sp.sl_p1_m2_weight,
            sp.sl_p1_m2_unit,
            sp.sl_p1_m3_item,
            sp.sl_p1_m3_lot,
            sp.sl_p1_m3_weight,
            sp.sl_p1_m3_unit,
            sp.sl_p1_m4_item,
            sp.sl_p1_m4_lot,
            sp.sl_p1_m4_weight,
            sp.sl_p1_m4_unit,
            sp.sl_p1_m5_item,
            sp.sl_p1_m5_lot,
            sp.sl_p1_m5_weight,
            sp.sl_p1_m5_unit,
            sp.sl_p1_c1_item,
            sp.sl_p1_c1_lot,
            sp.sl_p1_c1_weight,
            sp.sl_p1_c1_unit,
            sp.sl_p1_confirm,
            sp.sl_p1_memo,
            sp.sl_p2_machine,
            sp.sl_p2_user,
            sp.sl_p2_start_date,
            sp.sl_p2_end_date,
            sp.sl_p2_n2_date,
            sp.sl_p2_end_weight,
            sp.sl_p2_confirm,
            sp.sl_p2_memo,
            sp.sl_p2_kiln_temp,
            sp.sl_p2_n2_flow_g_axis,
            sp.sl_p2_n2_flow_m_axis,
            sp.sl_p3_machine,
            sp.sl_p3_user,
            sp.sl_p3_start1_date,
            sp.sl_p3_start2_date,
            sp.sl_p3_start3_date,
            sp.sl_p3_start4_date,
            sp.sl_p3_start5_date,
            sp.sl_p3_start6_date,
            sp.sl_p3_start7_date,
            sp.sl_p3_start8_date,
            sp.sl_p3_start9_date,
            sp.sl_p3_start10_date,
            sp.sl_p3_end_date,
            sp.sl_p3_end_weight,
            sp.sl_p3_dispose_weight,
            sp.sl_p3_memo,
            sp.sl_p4_machine,
            sp.sl_p4_user,
            sp.sl_p4_start_date,
            sp.sl_p4_end_date,
            sp.sl_p4_bat1_weight,
            sp.sl_p4_bat2_weight,
            sp.sl_p4_bat3_weight,
            sp.sl_p4_bat4_weight,
            sp.sl_p4_end_weight,
            sp.sl_p4_confirm,
            sp.sl_p4_hardness,
            sp.sl_p4_memo,
            sp.sl_p5_machine,
            sp.sl_p5_user,
            sp.sl_p5_start_date,
            sp.sl_p5_end_date,
            sp.sl_p5_cnt,
            sp.sl_p5_end_weight,
            sp.sl_p5_dispose_weight,
            sp.sl_p5_memo,
            sp.sl_p6_machine,
            sp.sl_p6_user,
            sp.sl_p6_start_date,
            sp.sl_p6_end_date,
            sp.sl_p6_end_weight,
            sp.sl_p6_m1_item,
            sp.sl_p6_m1_lot,
            sp.sl_p6_m1_weight,
            sp.sl_p6_m1_unit,
            sp.sl_p6_memo,
            sp.sl_p7_user,
            sp.sl_p7_start_date,
            sp.sl_p7_end_date,
            sp.sl_p7_p1_weight,
            sp.sl_p7_p1_unit,
            sp.sl_p7_p2_weight,
            sp.sl_p7_p2_unit,
            sp.sl_p7_samp1_weight,
            sp.sl_p7_samp1_unit,
            sp.sl_p7_samp2_weight,
            sp.sl_p7_samp2_unit,
            sp.sl_p7_memo
        FROM 
            product_sl_comb pl
        LEFT JOIN 
            sl_process sp ON pl.sl_lot_no = sp.sl_lot_no;
    """
# #SL材冷凍、解凍データの取得
# def select_sl_unfreezelog_data():
#     return """
#         WITH product_sl_comb AS (
#             SELECT 
#                 t1.lot_no AS product_lot_no,
#                 t3.mlt_vendor_lot_no AS sl_lot_no
#             FROM 
#                 prass_process_material t1
#             LEFT JOIN prass_process_material t2 ON t1.material_lot_no = t2.lot_no
#             LEFT JOIN material_lot t3 ON t3.mlt_material_lot_no = t2.material_lot_no 
#             WHERE EXISTS (SELECT 1 FROM temp_lot_numbers t4 WHERE t4.lot_no = t1.lot_no)
#                 AND  t1.material_class_code >= 'G122'
#                 AND t1.material_class_code < 'G130'
#             GROUP BY
#                 t1.lot_no, t3.mlt_vendor_lot_no
#         )
#         SELECT 
#             pl.product_lot_no,
#             su.sl_lot_no,
#             su.unfreeze_lot_no As sl_u_lot_no,
#             su.ware_housing_time AT TIME ZONE 'Asia/Shanghai' As sl_u_ware_housing_time,
#             su.weight As sl_u_weight,
#             su.datetime_out_of_fridge AT TIME ZONE 'Asia/Shanghai' As sl_u_datetime_out_of_fridge,
#             ROUND(CAST(EXTRACT(EPOCH FROM (su.datetime_out_of_fridge - su.ware_housing_time)) / 3600 AS numeric), 2) AS sl_u_freezing_hours,
#             su.unfreeze_user As sl_u_unfreeze_user,
#             CASE 
#                 WHEN assigned_group1 IS NULL OR assigned_group1 = '' THEN NULL
#                 ELSE 'BCJ_' || assigned_group1 
#             END As sl_u_assigned_machine1,
#             CASE 
#                 WHEN assigned_group2 IS NULL OR assigned_group2 = '' THEN NULL
#                 ELSE 'BCJ_' || assigned_group2 
#             END As sl_u_assigned_machine2,
#             CASE 
#                 WHEN assigned_group3 IS NULL OR assigned_group3 = '' THEN NULL
#                 ELSE 'BCJ_' || assigned_group3 
#             END As sl_u_assigned_machine3,
#             su.assigned_time AT TIME ZONE 'Asia/Shanghai' As sl_u_assigned_time,
#             CASE 
#                 WHEN su.assigned_time IS NULL OR su.datetime_out_of_fridge IS NULL THEN NULL
#                 ELSE ROUND(CAST(EXTRACT(EPOCH FROM (su.assigned_time - su.datetime_out_of_fridge)) / 3600 AS numeric), 2)
#             END AS sl_u_unfreezing_hours,
#             su.assigned_user As sl_u_assigned_user
#         FROM 
#             product_sl_comb pl
#         LEFT JOIN 
#             sl_unfreezelog su ON su.sl_lot_no = pl.sl_lot_no;
#     """
# LOT NOに関する基礎的情報の取得
def select_lot_base_info(category):
    query = """
        SELECT   
            t1.lot_no,
            t1.toko_type,
            t1.murata_type,
            t1.lot_flag,
            t1.input_qty,
            COALESCE(t2.defect_qty,0) AS all_defect_qty,
            COALESCE(ROUND(t2.defect_qty / NULLIF(t1.input_qty, 0) * 100, 2), 0) AS failer_ratio, 
            t1.start_datetime,
            t1.finish_datetime
        FROM prass_lot t1
        LEFT JOIN (
            SELECT 
                lot_no,
                SUM(defect_qty) AS defect_qty
            FROM prass_process_defect
            GROUP BY lot_no
        ) t2 ON t2.lot_no = t1.lot_no
    """
    if category == 'FG' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_lot_numbers t3 WHERE t3.lot_no = t1.lot_no) 
        """
    elif category == 'WIRE' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_wire_lots t3 WHERE t3.lot_no = t1.lot_no); 
        """
    elif category == 'TABLET' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_tablet_lots t3 WHERE t3.lot_no = t1.lot_no); 
        """
    return query
# 検印番号、PSロットNo（製造伝票番号）情報の取得
def select_inspection_info(category):
    query = """
        SELECT   
            t1.prass_lot_no,
            t1.ps_lot_no,
            t1.inspection_no,
            t1.mix_qty,
            t1.line_no,
            t1.process_flow
        FROM prass_lot_inspection t1
    """
    if category == 'FG' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_lot_numbers t2 WHERE t2.lot_no = t1.prass_lot_no) 
        """
    elif category == 'WIRE' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_wire_lots t2 WHERE t2.lot_no = t1.lot_no); 
        """
    elif category == 'TABLET' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_tablet_lots t2 WHERE t2.lot_no = t1.lot_no); 
        """
    return query
# ロット全体の不良情報の取得
def select_lot_defect_info(category):
    query = """
        SELECT   
            t1.lot_no,
            t1.defect_code,
            SUM(t1.defect_qty) as all_defect_qty
        FROM prass_process_defect t1
        WHERE t1.defect_qty is not null
    """
    if category == 'FG' :
        query = query + """
            AND EXISTS (SELECT 1 FROM temp_lot_numbers t2 WHERE t2.lot_no = t1.lot_no) 
        """
    elif category == 'WIRE' :
        query = query + """
            AND EXISTS (SELECT 1 FROM temp_wire_lots t2 WHERE t2.lot_no = t1.lot_no)
        """
    elif category == 'TABLET' :
        query = query + """
            AND EXISTS (SELECT 1 FROM temp_tablet_lots t2 WHERE t2.lot_no = t1.lot_no)
        """
    query = query + """
        GROUP BY
        t1.lot_no,
        t1.defect_code
    """
    return query
# 工程情報の取得
def select_process_info(category):
    query = """
        SELECT   
            t1.lot_no,
            t1.process_code,
            t1.start_datetime,
            t1.finish_datetime,
            ROUND(CAST(EXTRACT(EPOCH FROM (t1.finish_datetime - t1.start_datetime)) / 60 AS numeric), 2) AS duration_minutes,
            t1.input_qty,
            t1.output_qty
        FROM prass_lot_process t1
    """
    if category == 'FG' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_lot_numbers t2 WHERE t2.lot_no = t1.lot_no);
        """
    elif category == 'WIRE' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_wire_lots t2 WHERE t2.lot_no = t1.lot_no); 
        """
    elif category == 'TABLET' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_tablet_lots t2 WHERE t2.lot_no = t1.lot_no)
        """
    return query
# 工程別不良別情報の取得
def select_process_defect_info(category):
    query = """
        SELECT   
            t1.lot_no,
            t2.process_code || '_' || t1.defect_code AS process_defect_mode,
            SUM(t1.defect_qty) AS defect_qty
        From prass_process_defect t1
        LEFT JOIN prass_lot_process t2 ON t2.process_key = t1.process_key
    """
    if category == 'FG' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_lot_numbers t3 WHERE t3.lot_no = t1.lot_no)  
        """
    elif category == 'WIRE' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_wire_lots t3 WHERE t3.lot_no = t1.lot_no)
        """
    elif category == 'TABLET' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_tablet_lots t3 WHERE t3.lot_no = t1.lot_no)
        """
    query = query + """
        GROUP BY
            t1.lot_no,
            t2.process_code || '_' || t1.defect_code
    """
    return query
# 工程別設備情報の取得
def select_process_machine_info(category):
    query = """
        SELECT 
            t1.lot_no, 
            t2.process_code,
            t1.machine_code
        FROM prass_process_machine t1
        LEFT JOIN prass_lot_process t2 On t2.process_key = t1.process_key
    """
    if category == 'FG' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_lot_numbers t3 WHERE t3.lot_no = t1.lot_no);
        """
    elif category == 'WIRE' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_wire_lots t3 WHERE t3.lot_no = t1.lot_no); 
        """
    elif category == 'TABLET' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_tablet_lots t3 WHERE t3.lot_no = t1.lot_no)
        """
    return query
 
# # 使用材料情報の取得
def select_material_info(category) :
    if category == 'TABLET' :
        query = """
            SELECT 
                lot_no, 
                material_class_code
            FROM prass_process_material t1
        """
    else :
        query = """
            SELECT 
                lot_no, 
                material_class_code,
                material_lot_no
            FROM prass_process_material t1
        """
    if category == 'FG' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_lot_numbers t2 WHERE t2.lot_no = t1.lot_no);
        """
    elif category == 'WIRE' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_wire_lots t2 WHERE t2.lot_no = t1.lot_no); 
        """
    elif category == 'TABLET' :
        query = query + """
            WHERE EXISTS (SELECT 1 FROM temp_tablet_lots t3 WHERE t3.lot_no = t1.lot_no)
        """
    return query
# 工程別作業者の取得
def select_process_worker_info(category) :
    query = """
        SELECT 
            t1.lot_no, 
            t2.process_code,
            t1.worker_code || ' : ' || t1.worker_name AS worker_info
        FROM prass_process_worker t1
        LEFT JOIN prass_lot_process t2 On t2.process_key = t1.process_key
        WHERE t1.worker_code is not null
    """
    if category == 'FG' :
        query = query + """
            AND EXISTS (SELECT 1 FROM temp_lot_numbers t3 WHERE t3.lot_no = t1.lot_no)
        """
    elif category == 'WIRE' :
        query = query + """
            AND EXISTS (SELECT 1 FROM temp_wire_lots t3 WHERE t3.lot_no = t1.lot_no); 
        """
    elif category == 'TABLET' :
        query = query + """
            AND EXISTS (SELECT 1 FROM temp_tablet_lots t3 WHERE t3.lot_no = t1.lot_no); 
        """
    return query
