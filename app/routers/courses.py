from fastapi import APIRouter, HTTPException
import mysql.connector
from app.database import get_db_connection
from app.models.course_model import CourseModel

router = APIRouter()

@router.post("/master_courses", status_code=201)
def create_course(course: CourseModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO master_courses (code, name, hours, course_type, sub_type) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (course.code, course.name, course.hours, course.course_type, course.sub_type))
        conn.commit()
        return {"status": "success", "message": "เพิ่มหลักสูตรสำเร็จ"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.get("/master_courses")
def get_all_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM master_courses ORDER BY id DESC")
        return {"status": "success", "data": cursor.fetchall()}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()


@router.get("/master_courses/{id}")
def get_course_by_id(id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM master_courses WHERE id = %s", (id,))
        course = cursor.fetchone()
        if not course:
            raise HTTPException(status_code=404, detail="ไม่พบหลักสูตรนี้")
        return {"status": "success", "data": course}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()


@router.put("/master_courses/{id}")
def update_course(id: int, course: CourseModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # เช็คว่ามีไหม
        cursor.execute("SELECT * FROM master_courses WHERE id = %s", (id,))
        if not cursor.fetchone():
             raise HTTPException(status_code=404, detail="ไม่พบหลักสูตรนี้")
             
        sql = "UPDATE master_courses SET code=%s, name=%s, hours=%s, course_type=%s, sub_type=%s WHERE id=%s"
        cursor.execute(sql, (course.code, course.name, course.hours, course.course_type, course.sub_type, id))
        conn.commit()
        return {"status": "success", "message": f"แก้ไขหลักสูตร ID {id} สำเร็จ"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.delete("/master_courses/{id}")
def delete_course(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM master_courses WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลให้ลบ")
        return {"status": "success", "message": f"ลบหลักสูตร ID {id} สำเร็จ"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()