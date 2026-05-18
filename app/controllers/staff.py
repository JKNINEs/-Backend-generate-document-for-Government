from fastapi import APIRouter, HTTPException
import mysql.connector
from app.config.database import get_db_connection
from app.models.staff_model import staffModel

router = APIRouter()

# ==========================================
# [C] Create: เพิ่มข้อมูลบุคลากร
# ==========================================
@router.post("/staff", status_code=201)
def create_staff(staff: staffModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # SQL สำหรับ Insert
        sql = """
            INSERT INTO master_staff (name, position, work_group, job_desc, tel)
            VALUES (%s, %s, %s, %s, %s)
        """
        val = (
            staff.name,
            staff.position,
            staff.work_group,
            staff.job_desc,
            staff.tel
        )
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": "เพิ่มข้อมูลบุคลากรสำเร็จ"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# [R] Read: อ่านข้อมูลทั้งหมด
# ==========================================
@router.get("/staff")
def get_all_staff():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM master_staff ORDER BY id DESC"
        cursor.execute(sql)
        results = cursor.fetchall()
        return {"status": "success", "data": results}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()


@router.get("/staff/{id}")
def get_staff_by_id(id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM master_staff WHERE id = %s", (id,))
        staff = cursor.fetchone()
        if not staff:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลเจ้าหน้าที่นี้")
        return {"status": "success", "data": staff}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# [U] Update: แก้ไขข้อมูล (ตาม ID)
# ==========================================
@router.put("/staff/{id}")
def update_staff(id: int, staff: staffModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. เช็คก่อนว่ามี ID นี้ไหม
        check_sql = "SELECT * FROM master_staff WHERE id = %s"
        cursor.execute(check_sql, (id,))
        if not cursor.fetchone():
             raise HTTPException(status_code=404, detail="ไม่พบข้อมูลบุคลากรนี้")

        # 2. SQL สำหรับ Update
        sql = """
            UPDATE master_staff 
            SET name=%s, position=%s, work_group=%s, job_desc=%s, tel=%s
            WHERE id=%s
        """
        val = (
            staff.name,
            staff.position,
            staff.work_group,
            staff.job_desc,
            staff.tel,
            id  # ID สำหรับ WHERE อยู่ท้ายสุด
        )
        
        cursor.execute(sql, val)
        conn.commit()
        
        return {"status": "success", "message": f"แก้ไขข้อมูลบุคลากร ID {id} สำเร็จ"}
        
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# [D] Delete: ลบข้อมูล (ตาม ID)
# ==========================================
@router.delete("/staff/{id}")
def delete_staff(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM master_staff WHERE id = %s"
        cursor.execute(sql, (id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลที่ต้องการลบ")
            
        return {"status": "success", "message": f"ลบข้อมูลบุคลากร ID {id} เรียบร้อยแล้ว"}
        
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()