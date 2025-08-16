import sqlite3

conn = sqlite3.connect('shopify_insights.db')
cursor = conn.cursor()

print('Database Schema:')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f'\n{table_name.upper()} TABLE:')
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[1]} ({col[2]})')

conn.close()
