import sqlite3

print("Checking SQLite db.sqlite3:")
try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM auth_user")
    users = cursor.fetchall()
    print("Users in SQLite:", [u[0] for u in users])
except Exception as e:
    print("Error checking SQLite:", e)
