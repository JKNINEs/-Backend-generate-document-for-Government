from fastapi import APIRouter, HTTPException
import mysql.connector
from app.config.database import get_db_connection
from app.models.locations_model import locationsModel

router = APIRouter()

# ==========================================
# [C] Create: เพิ่มข้อมูลสถานที่
# ==========================================
@router.post("/locations", status_code=201)
def create_location(location: locationsModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO master_locations 
            (name, address_no, sub_district, district, province, zipcode)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        val = (
            location.name,
            location.address_no,
            location.sub_district,
            location.district,
            location.province,
            location.zipcode
        )
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": "เพิ่มข้อมูลสถานที่สำเร็จ", "id": cursor.lastrowid}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# [R] Read All: อ่านข้อมูลทั้งหมด
# ==========================================
@router.get("/locations")
def get_all_locations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM master_locations ORDER BY id DESC"
        cursor.execute(sql)
        results = cursor.fetchall()
        return {"status": "success", "data": results}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# [R] Read One: อ่านข้อมูลรายชิ้น (ต้องอยู่ก่อน PUT/DELETE)
# ==========================================
@router.get("/locations/{id}")
def get_location_by_id(id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM master_locations WHERE id = %s", (id,))
        location = cursor.fetchone()
        if not location:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลสถานที่นี้")
        return {"status": "success", "data": location}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# [U] Update: แก้ไขข้อมูล (ตาม ID)
# ==========================================
@router.put("/locations/{id}")
def update_location(id: int, location: locationsModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM master_locations WHERE id = %s", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลสถานที่นี้")

        sql = """
            UPDATE master_locations 
            SET name=%s, address_no=%s, sub_district=%s, 
                district=%s, province=%s, zipcode=%s
            WHERE id=%s
        """
        val = (
            location.name,
            location.address_no,
            location.sub_district,
            location.district,
            location.province,
            location.zipcode,
            id
        )
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": f"แก้ไขข้อมูลสถานที่ ID {id} สำเร็จ"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# [D] Delete: ลบข้อมูล (ตาม ID)
# ==========================================
@router.delete("/locations/{id}")
def delete_location(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM master_locations WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลที่ต้องการลบ")
        return {"status": "success", "message": f"ลบข้อมูลสถานที่ ID {id} เรียบร้อยแล้ว"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()
