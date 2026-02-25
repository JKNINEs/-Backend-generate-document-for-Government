from fastapi import APIRouter, HTTPException
import mysql.connector
from app.database import get_db_connection
from app.models.loan_model import LoanUpdateModel

router = APIRouter()

# Helper: แปลง batch_code → training_batch_id
def get_batch_id_from_code(cursor, batch_code: str) -> int:
    cursor.execute(
        "SELECT id FROM training_batches WHERE batch_code = %s",
        (batch_code,)
    )
    result = cursor.fetchone()
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"ไม่พบรุ่นฝึกอบรม รหัส {batch_code}"
        )
    return result[0]

# ==========================================
# [C/U] Create หรือ Update — ON DUPLICATE KEY
# ==========================================
@router.post("/loan/update-clearance")
def update_loan_clearance(loan: LoanUpdateModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        training_batch_id = get_batch_id_from_code(cursor, loan.batch_code)

        sql = """
            INSERT INTO loan_records 
            (training_batch_id, contract_no, loan_head_count, loan_date, clearance_date, clearance_head_day1, clearance_head_day2)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            contract_no         = VALUES(contract_no),
            loan_head_count     = VALUES(loan_head_count),
            loan_date           = VALUES(loan_date),
            clearance_date      = VALUES(clearance_date),
            clearance_head_day1 = VALUES(clearance_head_day1),
            clearance_head_day2 = VALUES(clearance_head_day2)
        """
        val = (
            training_batch_id,
            loan.contract_no,
            loan.clearance_head,
            loan.loan_date,
            loan.clearance_date,
            loan.clearance_head_day1,
            loan.clearance_head_day2
        )
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": f"บันทึกข้อมูลรุ่น {loan.batch_code} เรียบร้อย"}
    except HTTPException as http_err:
        raise http_err
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# [R] Read All
# ==========================================
@router.get("/loans")
def get_all_loans():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                lr.id,
                lr.training_batch_id,
                tb.batch_code,
                lr.contract_no,
                lr.loan_head_count,
                lr.loan_date,
                lr.clearance_date,
                lr.clearance_head_day1,
                lr.clearance_head_day2
            FROM loan_records lr
            INNER JOIN training_batches tb ON lr.training_batch_id = tb.id
            ORDER BY tb.batch_code DESC
        """
        cursor.execute(sql)
        return {"status": "success", "data": cursor.fetchall()}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# [R] Read One by batch_code
# ==========================================
@router.get("/loan/batch/{batch_code}")
def get_loan_by_batch_code(batch_code: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                lr.id,
                lr.training_batch_id,
                tb.batch_code,
                lr.contract_no,
                lr.loan_head_count,
                lr.load_date,
                lr.clearance_date,
                lr.clearance_head_day1,
                lr.clearance_head_day2
            FROM loan_records lr
            INNER JOIN training_batches tb ON lr.training_batch_id = tb.id
            WHERE tb.batch_code = %s
        """
        cursor.execute(sql, (batch_code,))
        result = cursor.fetchone()
        if not result:
            return {"status": "success", "data": None, "message": f"ยังไม่มีข้อมูลรุ่น {batch_code}"}
        return {"status": "success", "data": result}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()

# ==========================================
# [D] Delete by batch_code
# ==========================================
@router.delete("/loan/batch/{batch_code}")
def delete_loan_by_batch_code(batch_code: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        training_batch_id = get_batch_id_from_code(cursor, batch_code)

        cursor.execute("DELETE FROM loan_records WHERE training_batch_id = %s", (training_batch_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return {"status": "fail", "message": "ไม่พบข้อมูลที่ต้องการลบ"}

        return {"status": "success", "message": f"ลบข้อมูลรุ่น {batch_code} เรียบร้อยแล้ว"}
    except HTTPException as http_err:
        raise http_err
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()
