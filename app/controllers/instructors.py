from fastapi import APIRouter, HTTPException
import mysql.connector
from app.config.database import get_db_connection
from app.models.instructors_model import instructorsModel

router = APIRouter()

@router.post("/instructors", status_code=201)
def create_instructors(instructors: instructorsModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # สังเกตชื่อคอลัมน์ distruict ใน SQL (ถ้าในฐานข้อมูลชื่อ district อย่าลืมแก้ตรงนี้นะครับ)
        sql = """
            INSERT INTO master_instructors 
            (skill_field, name, id_card, address_no, moo, road, sub_district, district, province, zipcode, tel) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # ส่งค่าให้ครบ 11 ตัว
        val = (
            instructors.skill,
            instructors.name,
            instructors.in_card,
            instructors.address_no,
            instructors.moo,
            instructors.road,
            instructors.sub_distruict,
            instructors.district,  
            instructors.province,
            instructors.zipcode,
            instructors.tel
        )
        
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": "เพิ่มข้อมูลครูผู้สอนสำเร็จ"}
        
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.get("/instructors")
def get_all_instructors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM master_instructors ORDER BY id DESC")
        return {"status": "success", "data": cursor.fetchall()}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.get("/instructors/{id}")
def get_instructor_by_id(id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM master_instructors WHERE id = %s", (id,))
        instructor = cursor.fetchone()
        if not instructor:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลวิทยากรนี้")
        return {"status": "success", "data": instructor}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.put("/instructors/{id}")
def update_instructor(id: int, instructors: instructorsModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. เช็คก่อนว่ามี ID นี้ไหมในตาราง master_instructors
        check_sql = "SELECT * FROM master_instructors WHERE id = %s"
        cursor.execute(check_sql, (id,))
        if not cursor.fetchone():
             raise HTTPException(status_code=404, detail="ไม่พบข้อมูลครูผู้สอนนี้")

        # 2. SQL สำหรับ Update (แก้ให้ครบ 10 คอลัมน์ตามตาราง)
        sql = """
            UPDATE master_instructors 
            SET skill_field=%s, name=%s, id_card=%s, address_no=%s, moo=%s, 
                road=%s, sub_district=%s, province=%s, zipcode=%s, tel=%s
            WHERE id=%s
        """
        
        # 3. เตรียมข้อมูล (Value) ให้ตรงกับลำดับใน SQL
        # หมายเหตุ: ผมอิงชื่อตัวแปรตามที่คุณเขียนใน Create (เช่น in_card, sub_distruict)
        val = (
            instructors.skill, 
            instructors.name, 
            instructors.in_card, 
            instructors.address_no, 
            instructors.moo, 
            instructors.road, 
            instructors.sub_distruict, 
            instructors.province, 
            instructors.zipcode, 
            instructors.tel, 
            id  # ตัวสุดท้ายคือ id สำหรับ WHERE
        )
        
        cursor.execute(sql, val)
        conn.commit()
        
        return {"status": "success", "message": f"แก้ไขข้อมูลครูผู้สอน ID {id} สำเร็จ"}
        
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.delete("/instructors/{id}")
def delete_instructor(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # เปลี่ยนชื่อตารางเป็น master_instructors
        sql = "DELETE FROM master_instructors WHERE id = %s"
        cursor.execute(sql, (id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลที่ต้องการลบ")
            
        return {"status": "success", "message": f"ลบข้อมูลครูผู้สอน ID {id} สำเร็จ"}
        
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()