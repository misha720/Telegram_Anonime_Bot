import sqlite3

conn = sqlite3.connect('base.db')
cur = conn.cursor()

cur.execute("DELETE FROM users")
cur.execute("DELETE FROM user_in_search")
cur.execute("DELETE FROM chat")
cur.execute("DELETE FROM chats_list")

conn.commit()
