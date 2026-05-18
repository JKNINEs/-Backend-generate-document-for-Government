from fastapi import APIRouter, HTTPException, Response
from app.config.database import get_db_connection
from app.models.auth_model import LoginModel
import mysql.connector
import secrets
import bcrypt

router = APIRouter()

@router.post("/auth/login")
def login(credentials: LoginModel, response: Response):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (credentials.username,))
        user = cursor.fetchone()

        if not user or not bcrypt.checkpw(
            credentials.password.encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            raise HTTPException(status_code=401, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

        token = secrets.token_hex(32)
        cursor.execute("UPDATE users SET session_token = %s WHERE id = %s", (token, user['id']))
        conn.commit()

        response.set_cookie(key="session_token", value=token, httponly=True, max_age=60 * 60 * 8)

        return {
            "status": "success",
            "message": "เข้าสู่ระบบสำเร็จ",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "full_name": user.get('fullname', ''),
                "role": user.get('role', 'user')
            }
        }
    except HTTPException:
        raise
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        cursor.close()
        conn.close()