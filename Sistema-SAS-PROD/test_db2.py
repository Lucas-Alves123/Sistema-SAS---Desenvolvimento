import sys
sys.path.append('/var/src/src/SAS-PROD/Sistema-SAS-PROD/backend')
import pymysql

conn = pymysql.connect(host="localhost", user="root", passwd="", db="sas")
cursor = conn.cursor(pymysql.cursors.DictCursor)
cursor.execute("DESCRIBE agendamentos")
for row in cursor.fetchall():
    print(row['Field'])
