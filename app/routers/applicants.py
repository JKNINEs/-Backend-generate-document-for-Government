from fastapi import APIRouter, HTTPException
import mysql.connector
from app.database import get_db_connection
from app.models.applicant_model import (
    ApplicantBaseModel, 
    BulkApplicantCreateModel, 
    BulkUpdateResultModel
)

router = APIRouter()

# 1. [CREATE] - เพิ่มผู้สมัครแบบชุด โดยใช้ batch_code
@router.post("/applicants/bulk", status_code=201)
def create_bulk_applicants(data: BulkApplicantCreateModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 🔥 หา training_batch_id จาก batch_code ก่อน
        cursor.execute(
            "SELECT id FROM training_batches WHERE batch_code = %s", 
            (data.batch_code,)
        )
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"ไม่พบรุ่นฝึกอบรม รหัส {data.batch_code}"
            )
        
        training_batch_id = result[0]
        
        # เพิ่มผู้สมัคร
        values = [
            (a.name, a.gender, a.result, training_batch_id) 
            for a in data.applicants
        ]
        sql = "INSERT INTO applicants (name, gender, result, training_batch_id) VALUES (%s, %s, %s, %s)"
        cursor.executemany(sql, values)
        conn.commit()
        
        return {
            "status": "success", 
            "message": f"เพิ่มผู้สมัครรุ่น {data.batch_code} จำนวน {cursor.rowcount} คนเรียบร้อย"
        }
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()


# 3. [READ] - ดึงรายชื่อผู้สมัครทั้งหมดพร้อม batch_code
@router.get("/applicants")
def get_all_applicants():
    """
    ดึงผู้สมัครทั้งหมดพร้อมแสดงรหัสรุ่น (batch_code)
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT 
                a.id,
                a.name,
                a.gender,
                a.result,
                a.training_batch_id,
                tb.batch_code
            FROM applicants a
            INNER JOIN training_batches tb ON a.training_batch_id = tb.id
            ORDER BY tb.batch_code DESC, a.id ASC
        """
        cursor.execute(sql)
        data = cursor.fetchall()
        
        return {"status": "success", "data": data}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.get("/applicants/{id}")
def get_applicant_by_id(id: int):
    """
    ดึงข้อมูลผู้สมัครเฉพาะ ID (สำหรับแก้ไข)
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT 
                a.id, a.name, a.gender, a.result,
                a.training_batch_id,
                tb.batch_code
            FROM applicants a
            LEFT JOIN training_batches tb ON a.training_batch_id = tb.id
            WHERE a.id = %s
        """
        cursor.execute(sql, (id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้สมัคร")
        
        return {"status": "success", "data": result}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()


# 4. [UPDATE] - อัปเดตสถานะผู้ผ่านการอบรมแบบกลุ่ม
@router.put("/applicants/bulk-update-result")
def bulk_update_result(data: BulkUpdateResultModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if not data.ids:
            raise HTTPException(status_code=400, detail="กรุณาเลือกรายชื่อ")
        
        format_strings = ','.join(['%s'] * len(data.ids))
        sql = f"UPDATE applicants SET result = %s WHERE id IN ({format_strings})"
        val = (data.result, *data.ids)
        
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": f"อัปเดตสถานะ {cursor.rowcount} คนเรียบร้อย"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# 5. [UPDATE] - แก้ไขข้อมูลรายคน
@router.put("/applicants/{id}")
def update_applicant(id: int, applicant: ApplicantBaseModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "UPDATE applicants SET name=%s, gender=%s, result=%s WHERE id=%s"
        cursor.execute(sql, (applicant.name, applicant.gender, applicant.result, id))
        conn.commit()
        return {"status": "success", "message": "แก้ไขข้อมูลเรียบร้อย"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()


@router.get("/applicants/batch/{batch_code}")
def get_applicants_by_batch_code(batch_code: str):
    """
    ดึงรายชื่อผู้สมัครตามรหัสรุ่น (สำหรับ Bulk Edit)
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT 
                a.id, a.name, a.gender, a.result,
                a.training_batch_id,
                tb.batch_code
            FROM applicants a
            INNER JOIN training_batches tb ON a.training_batch_id = tb.id
            WHERE tb.batch_code = %s
            ORDER BY a.id ASC
        """
        cursor.execute(sql, (batch_code,))
        data = cursor.fetchall()
        
        return {"status": "success", "data": data}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# 6. [DELETE] - ลบผู้สมัครรายคน
@router.delete("/applicants/{id}")
def delete_applicant(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM applicants WHERE id = %s"
        cursor.execute(sql, (id,))
        conn.commit()
        
        # ✅ เช็คว่าลบได้จริงไหม (กรณี id ไม่มีในระบบ)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้สมัคร")
        
        return {"status": "success", "message": "ลบข้อมูลเรียบร้อย"}
    
    except mysql.connector.Error as err:
        conn.rollback()  # ✅ rollback เมื่อเกิด error
        
        # ✅ แยก error FK ออกมาให้ชัดเจน
        if err.errno == 1451:
            return {
                "status": "fail", 
                "message": "ไม่สามารถลบได้ เนื่องจากข้อมูลนี้ถูกใช้งานอยู่ในระบบ"
            }
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()