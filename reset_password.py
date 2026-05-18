# reset_password.py
import bcrypt
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # ← แก้ตรงนี้
    database="training_db"       # ← แก้ตรงนี้
)

new_password = "123456"
hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

cursor = conn.cursor()
cursor.execute("UPDATE users SET password = %s WHERE role = 'admin'", (hashed,))
conn.commit()

print(f"✅ Reset สำเร็จ! {cursor.rowcount} row(s) updated")

cursor.close()
conn.close()