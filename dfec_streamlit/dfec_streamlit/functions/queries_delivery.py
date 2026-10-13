
# #条件にみあう出荷情報覧の取得
# def select_delivery_list():
#     return  """
#         SELECT
#             murata_type,
#             sales_date,
#             inspection_no,
#             osa_code,
#             customer_code,
#             customer_name,
#             customer_part_no,
#             shipping_qty,
#             invoice_no,
#             invoice_item_no,
#             card_no,
#             customer_purchase_order_no,
#             toko_type,
#             h40,
#             h50
#         FROM 
#             delivery_history
#         WHERE
#             (murata_type LIKE %s OR %s = '')
#             AND inspection_no BETWEEN %s AND %s 
#             AND sales_date >= %s 
#             AND sales_date <= %s 
#         ORDER BY sales_date, inspection_no
#     """
