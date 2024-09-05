import pandas as pd
import sqlite3

file = 'grafik.csv'
db = 'database.db'
tableName = 'grafik'

df = pd.read_csv(file, delimiter=';')

print(df.head())

df['Role'] = df['Role'].str.replace(';', ',') 

conn = sqlite3.connect(db)

df.to_sql(tableName, conn, if_exists='replace', index=False)

conn.close()

print(f"Data dari {file} telah berhasil disimpan ke tabel {tableName} dalam database {db}")
