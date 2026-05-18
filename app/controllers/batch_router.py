from fastapi import APIRouter, HTTPException
import mysql.connector
from app.config.database import get_db_connection
from app.models.batch_model import BatchCreateModel

router = APIRouter()

@router.post("/training_batches", status_code=201)
def create_training_batch(batch: BatchCreateModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO training_batches 
            (batch_code, request_doc_no, request_date, system_code, activity_id, 
             course_id, location_id, instructor_id, start_date, end_date, 
             training_dates_text, borrow_date, training_time, duration_days, 
             target_group, budget_speaker, budget_material, budget_food, 
             budget_snack, controller_id, coordinator_1_id, coordinator_2_id, 
             coordinator_3_id, borrow_staff_id, cert_announce_date, number_of_snacks) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (
            batch.batch_code, batch.request_doc_no, batch.request_date, batch.system_code,
            batch.activity_id, batch.course_id, batch.location_id, batch.instructor_id,
            batch.start_date, batch.end_date, batch.training_dates_text, batch.borrow_date,
            batch.training_time, batch.duration_days, batch.target_group, batch.budget_speaker,
            batch.budget_material, batch.budget_food, batch.budget_snack, batch.controller_id,
            batch.coordinator_1_id, batch.coordinator_2_id, batch.coordinator_3_id,
            batch.borrow_staff_id, batch.cert_announce_date, batch.number_of_snacks
        )
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": "สร้างรุ่นการอบรมสำเร็จ", "id": cursor.lastrowid}
    except mysql.connector.Error as err:
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()


@router.get("/training_batches")
def get_all_batches():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT id, batch_code FROM training_batches ORDER BY id DESC"
        cursor.execute(sql)
        return {"status": "success", "data": cursor.fetchall()}
    finally:
        conn.close()


@router.get("/training_batches/detail/{batch_code}")
def get_batch_detail(batch_code: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """ 
        SELECT
            tb.id           AS batch_id,
            tb.batch_code,
            tb.training_dates_text,
            tb.training_time,
            tb.target_group,
            tb.system_code  AS code_system,
            tb.cert_announce_date AS announce_date,
            tb.request_date,
            tb.request_doc_no,
            tb.borrow_date,
            tb.duration_days,
            tb.number_of_snacks,
            tb.budget_speaker,
            tb.budget_material,
            tb.budget_food,
            tb.budget_snack,

            -- ✅ FK IDs ที่จำเป็นสำหรับ PUT (เดิมไม่ได้ SELECT มา!)
            tb.activity_id,
            tb.course_id,
            tb.location_id,
            tb.instructor_id,
            tb.controller_id,
            tb.coordinator_1_id,
            tb.coordinator_2_id,
            tb.coordinator_3_id,
            tb.borrow_staff_id,

            -- Course
            mc.name         AS course_name,
            mc.code         AS course_code,
            mc.course_type  AS training_type,
            mc.hours        AS duration,
            (tb.budget_speaker * mc.hours) AS total_inst,

            -- Activity
            pa.activity_name,
            pa.activity,
            pa.sub_activity_name  AS sub_activity,
            pa.target_goal        AS activity_goal,
            pa.kind_of_fiscal,
            pa.fiscal_year        AS kind_of_year,
            pa.expenses,

            -- Plan / Project
            pj.name AS project_name,
            pl.name AS plan_name,

            -- Location
            loc.name AS location_name,

            -- Instructor
            inst.name    AS instructor_name,
            inst.id_card AS instructor_id_card,

            -- Staff
            s_ctrl.name     AS controller_name,
            s_ctrl.position AS controller_pos,
            s_c1.name       AS coord1_name,
            s_c1.position   AS coord1_position,
            s_c2.name       AS coord2_name,
            s_c2.position   AS coord2_position,
            s_c3.name       AS coord3_name,
            s_c3.position   AS coord3_position,
            s_c4.name       AS borrow_name,
            s_c4.position   AS coord4_position,

            -- Loan
            la.loan_date,
            la.contract_no,
            la.clearance_head_day1 AS head_day1,
            la.clearance_head_day2 AS head_day2,
            la.clearance_date

        FROM training_batches tb
        LEFT JOIN master_courses mc      ON tb.course_id       = mc.id
        LEFT JOIN master_locations loc   ON tb.location_id     = loc.id
        LEFT JOIN master_instructors inst ON tb.instructor_id  = inst.id
        LEFT JOIN project_activities pa  ON tb.activity_id     = pa.id
        LEFT JOIN master_projects pj     ON pa.project_id      = pj.id
        LEFT JOIN master_plans pl        ON pa.plan_id         = pl.id
        LEFT JOIN master_staff s_ctrl    ON tb.controller_id   = s_ctrl.id
        LEFT JOIN master_staff s_c1      ON tb.coordinator_1_id = s_c1.id
        LEFT JOIN master_staff s_c2      ON tb.coordinator_2_id = s_c2.id
        LEFT JOIN master_staff s_c3      ON tb.coordinator_3_id = s_c3.id
        LEFT JOIN master_staff s_c4      ON tb.borrow_staff_id = s_c4.id
        LEFT JOIN loan_records la        ON tb.id              = la.training_batch_id
        WHERE tb.batch_code = %s 
        """
        cursor.execute(sql, (batch_code,))
        result = cursor.fetchone()
        if not result:
            return {"status": "fail", "message": "ไม่พบข้อมูลรุ่นนี้"}

        # นับจำนวนผู้สมัคร
        cursor.execute(
            "SELECT COUNT(*) AS total FROM applicants WHERE training_batch_id = %s",
            (result['batch_id'],)
        )
        count_res = cursor.fetchone()
        applicant_count = count_res['total'] if count_res else 0

        # รายชื่อผู้สมัคร
        cursor.execute(
            "SELECT name, gender FROM applicants WHERE training_batch_id = %s",
            (result['batch_id'],)
        )
        applicants_list = cursor.fetchall()

        # รายชื่อผู้ผ่าน
        cursor.execute(
            "SELECT name, gender, result FROM applicants WHERE training_batch_id = %s AND result = 'ผ่าน'",
            (result['batch_id'],)
        )
        passed_list = cursor.fetchall()

        # คำนวณค่าใช้จ่าย
        raw_budget_material = float(result.get('budget_material') or 0)
        raw_budget_food     = float(result.get('budget_food') or 0)
        raw_budget_snack    = float(result.get('budget_snack') or 0)
        number_of_snacks    = float(result.get('number_of_snacks') or 0)
        duration_days       = float(result.get('duration_days') or 0)
        total_inst_value    = float(result.get('total_inst') or 0)
        head_day1           = int(result.get('head_day1') or 0)
        head_day2           = int(result.get('head_day2') or 0)

        total_material_value = raw_budget_material * applicant_count
        total_food_value     = raw_budget_food * applicant_count * duration_days
        total_snack_value    = raw_budget_snack * applicant_count * number_of_snacks
        total_all_budget     = total_inst_value + total_material_value + total_food_value + total_snack_value

        food_last_day  = (raw_budget_food  * head_day1) + (raw_budget_food  * head_day2 * (duration_days - 1))
        snack_last_day = (raw_budget_snack * head_day1 * 2) + (raw_budget_snack * head_day2 * (number_of_snacks - 2))
        total_used     = food_last_day + snack_last_day
        remaining      = (total_food_value + total_snack_value) - total_used

        result['applicant_count'] = applicant_count
        result['applicants_list'] = applicants_list
        result['passed_list']     = passed_list
        result['calculated'] = {
            'total_material':    total_material_value,
            'total_food':        total_food_value,
            'total_food_snack':  total_food_value + total_snack_value,
            'total_all_budget':  total_all_budget,
            'total_used_actual': total_used,
            'remaining':         remaining,
        }

        return {"status": "success", "data": result}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.put("/training_batches/{id}")
def update_training_batch(id: int, batch: BatchCreateModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print(f">>> PUT called: id={id}, batch_code={batch.batch_code}")

        cursor.execute("SELECT id FROM training_batches WHERE id = %s", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="ไม่พบรุ่นการอบรมที่ต้องการแก้ไข")

        cursor.execute(
            "SELECT id FROM training_batches WHERE batch_code = %s AND id != %s",
            (batch.batch_code, id)
        )
        if cursor.fetchone():
            return {"status": "fail", "message": f"รุ่น '{batch.batch_code}' มีอยู่แล้วในระบบ"}

        sql = """
            UPDATE training_batches 
            SET batch_code=%s, request_doc_no=%s, request_date=%s, system_code=%s, activity_id=%s, 
                course_id=%s, location_id=%s, instructor_id=%s, start_date=%s, end_date=%s, 
                training_dates_text=%s, borrow_date=%s, training_time=%s, duration_days=%s, 
                target_group=%s, budget_speaker=%s, budget_material=%s, budget_food=%s, 
                budget_snack=%s, controller_id=%s, coordinator_1_id=%s, coordinator_2_id=%s, 
                coordinator_3_id=%s, borrow_staff_id=%s, cert_announce_date=%s, number_of_snacks=%s
            WHERE id=%s
        """
        val = (
            batch.batch_code, batch.request_doc_no, batch.request_date, batch.system_code,
            batch.activity_id, batch.course_id, batch.location_id, batch.instructor_id,
            batch.start_date, batch.end_date, batch.training_dates_text, batch.borrow_date,
            batch.training_time, batch.duration_days, batch.target_group, batch.budget_speaker,
            batch.budget_material, batch.budget_food, batch.budget_snack, batch.controller_id,
            batch.coordinator_1_id, batch.coordinator_2_id, batch.coordinator_3_id,
            batch.borrow_staff_id, batch.cert_announce_date, batch.number_of_snacks, id
        )
        cursor.execute(sql, val)
        conn.commit()
        return {"status": "success", "message": f"แก้ไขรุ่นการอบรม ID {id} สำเร็จ"}

    except mysql.connector.Error as err:
        print(f">>> MySQL Error: {err}")
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()


@router.delete("/training_batches/{id}")
def delete_training_batch(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM training_batches WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลที่ต้องการลบ")
        return {"status": "success", "message": f"ลบรุ่นการอบรม ID {id} เรียบร้อยแล้ว"}
    except mysql.connector.Error as err:
        if err.errno == 1451:
            return {"status": "fail", "message": "ไม่สามารถลบได้เนื่องจากมีการกรอกรายชื่อผู้สมัครหรือข้อมูลการเงินไว้แล้ว"}
        return {"status": "fail", "message": str(err)}
    finally:
        conn.close()