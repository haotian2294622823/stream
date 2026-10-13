import psycopg2
#import oracledb

# # PRASS prass_dfecへ接続
# def connect_to_prass_dfec():
#    params = oracledb.ConnectParams(host="tok-prassdb02aSCN.murata.co.jp", port=1521, service_name="orcltvs")
#    return oracledb.connect(user="prassdfec", password="prassdfec123", params=params)

# # PRASS prass_dfecへ接続
# def connect_to_spirits_euc():
#    params = oracledb.ConnectParams(host="m1tahb.murata.co.jp", port=11540, service_name="prd_china_euc")
#    return oracledb.connect(user="SCHM_EUC_TZH", password="nwuWQT1N", params=params)

# # tok-bi02 へ接続
# def connect_to_bi02_dfec():
#    server = 'tok-bi02.co.murata.local'
#    user = 'refer'
#    password = 'refer123'
#    database = "prass_dfec"

#    connection_string = f"mssql+pymssql://{user}:{password}@{server}/{database}"
#    return connection_string


# # データ基盤用postgreSQLへ接続(local)
# def connect_to_postgresql():
#    return psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format( 			
#                user="postgres",        #ユーザ			
#                password="postgres",  #パスワード			
#                host="localhost",       #ホスト名			
#                port="5432",            #ポート			
#                dbname="tzh_dfegh"))    #データベース名	  

# データ基盤用postgreSQLへ接続(TEST DB)
# def connect_to_postgresql():
#    return psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format( 			
#                user="tc1114",        #ユーザ			
#                password="Tok2408",  #パスワード			
#                host="10.65.48.57",       #ホスト名			
#                port="5432",            #ポート			
#                dbname="testtok240801"))    #データベース名	  

def connect_to_postgresql():
    return psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format( 			
                user="tok2026",        #ユーザ			
                password="Saitama2026",  #パスワード			
                host="10.65.48.57",       #ホスト名			
                port="5432",            #ポート			
                dbname="dfectest26"))    #データベース名	

# #データ基盤用postgreSQLへ接続(tzh_server)
# def connect_to_postgresql():
#     return psycopg2.connect(
#         user="tokdfegh",
#         password="Tok@202501",
#         host="TZH-LXDB1.co.murata.local",
#         port="5432",
#         dbname="dfegh2024"
#     )
