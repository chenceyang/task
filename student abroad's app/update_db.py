import sqlite3

conn = sqlite3.connect("app/instance/app.sqlite3")

cursor = conn.cursor()

cursor.execute(
    "ALTER TABLE vocab ADD COLUMN embedding TEXT"
)

conn.commit()

conn.close()

print("database updated")