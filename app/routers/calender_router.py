from fastapi import APIRouter, HTTPException
import mysql.connector
from app.database import get_db_connection
from app.models.calender_model import EventModel
from datetime import datetime, date

router = APIRouter()

# ==========================================
# EVENTS — Read All
# ==========================================
@router.get("/events")
def get_all_events():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM events ORDER BY start_datetime DESC")
        return {"status": "success", "data": cursor.fetchall()}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# EVENTS — Read One
# ==========================================
@router.get("/events/{id}")
def get_event_by_id(id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM events WHERE id = %s", (id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลการจอง")
        return {"status": "success", "data": event}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# EVENTS — Create
# ==========================================
@router.post("/events", status_code=201)
def create_event(event: EventModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # เช็ค conflict ห้องซ้ำช่วงเวลาเดียวกัน
        conflict_sql = """
            SELECT id FROM events
            WHERE room_name = %s
              AND status != 'CANCELLED'
              AND start_datetime < %s
              AND end_datetime > %s
        """
        cursor.execute(conflict_sql, (event.room_name, event.end_datetime, event.start_datetime))
        if cursor.fetchone():
            return {"status": "fail", "message": "ห้องนี้ถูกจองในช่วงเวลาดังกล่าวแล้ว"}

        sql = """
            INSERT INTO events (title, room_name, start_datetime, end_datetime, status, created_by, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        val = (
            event.title,
            event.room_name,
            event.start_datetime,
            event.end_datetime,
            event.status,
            event.created_by,
            event.note
        )
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": "จองห้องสำเร็จ", "id": cursor.lastrowid}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# EVENTS — Update
# ==========================================
@router.put("/events/{id}")
def update_event(id: int, event: EventModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM events WHERE id = %s", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลการจอง")

        # เช็ค conflict ยกเว้น record ตัวเอง
        conflict_sql = """
            SELECT id FROM events
            WHERE room_name = %s
              AND id != %s
              AND status != 'CANCELLED'
              AND start_datetime < %s
              AND end_datetime > %s
        """
        cursor.execute(conflict_sql, (event.room_name, id, event.end_datetime, event.start_datetime))
        if cursor.fetchone():
            return {"status": "fail", "message": "ห้องนี้ถูกจองในช่วงเวลาดังกล่าวแล้ว"}

        sql = """
            UPDATE events
            SET title=%s, room_name=%s, start_datetime=%s, end_datetime=%s,
                status=%s, created_by=%s, note=%s
            WHERE id=%s
        """
        val = (
            event.title,
            event.room_name,
            event.start_datetime,
            event.end_datetime,
            event.status,
            event.created_by,
            event.note,
            id
        )
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": f"แก้ไขการจอง ID {id} สำเร็จ"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# EVENTS — Delete
# ==========================================
@router.delete("/events/{id}")
def delete_event(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM events WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลที่ต้องการลบ")
        return {"status": "success", "message": f"ลบการจอง ID {id} สำเร็จ"}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()


@router.delete("/events-cleanup")
def cleanup_past_events():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        today = date.today().strftime('%Y-%m-%d')
        cursor.execute("DELETE FROM events WHERE DATE(end_datetime) < %s", (today,))
        conn.commit()
        return {"status": "success", "deleted": cursor.rowcount}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()