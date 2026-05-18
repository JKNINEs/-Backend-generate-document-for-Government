from fastapi import APIRouter, HTTPException
import mysql.connector
from app.config.database import get_db_connection
from app.models.activity_model import ActivityModel, MasterData

router = APIRouter()

# ==========================================
# 1. PROJECT ACTIVITIES CRUD (ตารางหลัก)
# ==========================================

@router.post("/project_activities", status_code=201)
def create_activity(act: ActivityModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO project_activities 
            (activity_name, fiscal_year, kind_of_fiscal, activity, expenses, sub_activity_name, plan_id, project_id, target_goal) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (act.activity_name, act.fiscal_year, act.kind_of_fiscal, act.activity, 
               act.expenses, act.sub_activity_name, act.plan_id, act.project_id, act.target_goal)
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": "เพิ่มกิจกรรมสำเร็จ"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.get("/project_activities")
def get_all_activities():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT 
                a.*, 
                p.name as project_name, 
                pl.name as plan_name 
            FROM project_activities a
            LEFT JOIN master_projects p ON a.project_id = p.id
            LEFT JOIN master_plans pl ON a.plan_id = pl.id  -- ดึงผ่าน a.plan_id แทน p.plan_id
            ORDER BY a.id DESC
        """
        cursor.execute(sql)
        return {"status": "success", "data": cursor.fetchall()}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.get("/project_activities/{id}")
def get_activity_by_id(id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT 
                a.*, 
                p.name as project_name, 
                pl.name as plan_name 
            FROM project_activities a
            LEFT JOIN master_projects p ON a.project_id = p.id
            LEFT JOIN master_plans pl ON a.plan_id = pl.id -- แก้จุดนี้เช่นกัน
            WHERE a.id = %s
        """
        cursor.execute(sql, (id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูล")
        return {"status": "success", "data": result}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.put("/project_activities/{id}")
def update_activity(id: int, act: ActivityModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
            UPDATE project_activities 
            SET activity_name=%s, fiscal_year=%s, kind_of_fiscal=%s, activity=%s, 
                expenses=%s, sub_activity_name=%s, plan_id=%s, project_id=%s, target_goal=%s
            WHERE id=%s
        """
        val = (act.activity_name, act.fiscal_year, act.kind_of_fiscal, act.activity, 
               act.expenses, act.sub_activity_name, act.plan_id, act.project_id, act.target_goal, id)
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": f"แก้ไขกิจกรรม ID {id} สำเร็จ"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.delete("/project_activities/{id}")
def delete_activity(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM project_activities WHERE id = %s"
        cursor.execute(sql, (id,))
        conn.commit()
        return {"status": "success", "message": "ลบกิจกรรมสำเร็จ"}
    except mysql.connector.Error as err:
        if err.errno == 1451:
            return {"status": "fail", "message": "ไม่สามารถลบได้เนื่องจากถูกใช้งานในส่วนอื่น"}
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# 2. MASTER PLANS CRUD (จัดการแผนงาน)
# ==========================================

@router.post("/master_plans", status_code=201)
def create_plan(data: MasterData): # ใช้ MasterData เพื่อรับ {"name": "..."}
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO master_plans (name) VALUES (%s)", (data.name,))
        conn.commit()
        return {"status": "success", "message": "เพิ่มแผนงานสำเร็จ", "id": cursor.lastrowid}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.get("/master_plans")
def get_plans():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM master_plans ORDER BY id DESC")
    plans = cursor.fetchall()
    conn.close()
    return {"status": "success", "data": plans}

@router.put("/master_plans/{id}")
def update_plan(id: int, data: MasterData):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE master_plans SET name=%s WHERE id=%s", (data.name, id))
        conn.commit()
        return {"status": "success", "message": "แก้ไขแผนงานสำเร็จ"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.delete("/master_plans/{id}")
def delete_plan(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM master_plans WHERE id = %s", (id,))
        conn.commit()
        return {"status": "success", "message": "ลบแผนงานสำเร็จ"}
    except mysql.connector.Error as err:
        if err.errno == 1451:
            return {"status": "fail", "message": "ลบไม่ได้เนื่องจากข้อมูลถูกใช้งานอยู่"}
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# 3. MASTER PROJECTS CRUD (จัดการโครงการ)
# ==========================================

@router.post("/master_projects", status_code=201)
def create_project(data: MasterData):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO master_projects (name) VALUES (%s)", (data.name,))
        conn.commit()
        return {"status": "success", "message": "เพิ่มโครงการสำเร็จ", "id": cursor.lastrowid}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.get("/master_projects")
def get_projects():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # ระบุชื่อคอลัมน์ให้ชัดเจน (id, name) แทนการใช้ * # เพื่อป้องกันกรณีที่ระบบจำโครงสร้างตารางเก่าที่มี plan_id
        sql = "SELECT id, name FROM master_projects ORDER BY id DESC"
        cursor.execute(sql)
        projects = cursor.fetchall()
        return {"status": "success", "data": projects}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.put("/master_projects/{id}")
def update_project(id: int, data: MasterData):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE master_projects SET name=%s WHERE id=%s", (data.name, id))
        conn.commit()
        return {"status": "success", "message": "แก้ไขโครงการสำเร็จ"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

@router.delete("/master_projects/{id}")
def delete_project(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM master_projects WHERE id = %s", (id,))
        conn.commit()
        return {"status": "success", "message": "ลบโครงการสำเร็จ"}
    except mysql.connector.Error as err:
        if err.errno == 1451:
            return {"status": "fail", "message": "ลบไม่ได้เนื่องจากข้อมูลถูกใช้งานอยู่"}
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()