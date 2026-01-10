import sqlite3

conn = sqlite3.connect("support_calls.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM support_calls")
rows = cursor.fetchall()

print(f"Total records: {len(rows)}\n")

for row in rows:
    print(row)

conn.close()
