import psycopg2 
import sys, os 
def do():
    try: 
        dbname = 'sn_api'
        user = 'postgres'
        password = '111'
        conn = psycopg2.connect(f"dbname='{dbname}' user='{user}' password='{password}'") # perFecTpRomE 
        conn.set_isolation_level(0)
    except Exception as ex:
        print("Unable to connect to the database.")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    cur = conn.cursor()

    try:
        cur.execute("SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_schema,table_name")
        rows = cur.fetchall()
        for row in rows:
            print ("dropping table: ", row[1])
            cur.execute("drop table " + row[1] + " cascade")
        cur.close()
        conn.close()
    except:
        print ("Error: ", ex)

do()