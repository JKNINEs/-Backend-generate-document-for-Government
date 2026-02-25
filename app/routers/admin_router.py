from fastapi import APIRouter, HTTPException, Request, Depends
from app.database import get_db_connection
from app.models.auth_model import CreateUserModel, UpdateUserModel
import mysql.connector
import bcrypt

router = APIRouter()

def require_admin(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="กรุณาเข้าสู่ระบบ")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE session_token = %s", (token,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Session ไม่ถูกต้อง")
        if user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึง (Admin เท่านั้น)")
        return user
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/users")
def get_all_users(admin: dict = Depends(require_admin)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username, fullname, role, created_at FROM users ORDER BY id ASC")
        users = cursor.fetchall()
        return {"status": "success", "users": users}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/users")
def create_user(data: CreateUserModel, admin: dict = Depends(require_admin)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (data.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username นี้มีในระบบแล้ว")

        hashed_pw = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, password, fullname, role) VALUES (%s, %s, %s, %s)",
            (data.username, hashed_pw, data.fullname, data.role)
        )
        conn.commit()

        return {"status": "success", "message": f"เพิ่มผู้ใช้ '{data.username}' สำเร็จ", "user_id": cursor.lastrowid}
    except HTTPException:
        raise
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        conn.close()

@router.put("/admin/users/{user_id}")
def update_user(user_id: int, data: UpdateUserModel, admin: dict = Depends(require_admin)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งาน")

        fields, values = [], []

        if data.username is not None:
            cursor.execute("SELECT id FROM users WHERE username = %s AND id != %s", (data.username, user_id))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Username นี้มีในระบบแล้ว")
            fields.append("username = %s")
            values.append(data.username)

        if data.password is not None:
            hashed_pw = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            fields.append("password = %s")
            values.append(hashed_pw)

        if data.fullname is not None:
            fields.append("fullname = %s")
            values.append(data.fullname)

        if data.role is not None:
            fields.append("role = %s")
            values.append(data.role)

        if not fields:
            raise HTTPException(status_code=400, detail="ไม่มีข้อมูลที่ต้องการแก้ไข")

        values.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = %s", values)
        conn.commit()

        return {"status": "success", "message": f"แก้ไขข้อมูล user id {user_id} สำเร็จ"}
    except HTTPException:
        raise
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        conn.close()

@router.delete("/admin/users/{user_id}")
def delete_user(user_id: int, admin: dict = Depends(require_admin)):
    if admin['id'] == user_id:
        raise HTTPException(status_code=400, detail="ไม่สามารถลบบัญชีของตัวเองได้")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งาน")

        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

        return {"status": "success", "message": f"ลบผู้ใช้ '{user['username']}' สำเร็จ"}
    except HTTPException:
        raise
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        conn.close()