import sqlite3

conn = sqlite3.connect('base.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE chat(
   id INT PRIMARY KEY,
   user_id INT,
   message TEXT,
   file_path TEXT);
""")

conn.commit()