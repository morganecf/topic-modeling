import sqlite3
import pandas as pd

db = sqlite3.connect('/Users/morgane/Library/Application Support/Google/Chrome/Default/History')
cursor = db.cursor()
cursor.execute('select name from sqlite_master where type="table";')
tables = cursor.fetchall()
for table in tables:
  table_name = table[0]
  df = pd.read_sql_query('select * from %s' % table_name, db)
  df.to_csv(table_name + '.csv', index_lable='index', encoding='utf-8')