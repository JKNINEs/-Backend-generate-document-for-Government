from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from docxtpl import DocxTemplate
import os
from app.database import get_db_connection
from pythainlp import word_tokenize # อย่าลืม import
from bahttext import bahttext  # ✅ เพิ่มไว้ด้านบนสุดของไฟล์

router = APIRouter()

# --- 1. ฟังก์ชันช่วยงาน (Helper Functions) ---


def format_id_card(id_str):
    """แปลง 3219900004992.0 เป็น 3 2199 00004 99 2"""
    if id_str is None or id_str == "": 
        return ""
    
    # 1. แปลงเป็น String และตัด .0 ออกทันที
    s = str(id_str).strip()
    if s.endswith(".0"):
        s = s[:-2]
    
    # 2. ลบสิ่งที่ไม่ใช่ตัวเลขออก (ถ้ามี)
    s = "".join(filter(str.isdigit, s))
    
    # 3. ตรวจสอบความยาว 13 หลักก่อนจัดรูปแบบ
    if len(s) == 13:
        # ใช้ช่องว่างคั่นตามรูปแบบ x xxxx xxxxx xx x
        return f"{s[0]} {s[1:5]} {s[5:10]} {s[10:12]} {s[12]}"
    
    return s # ถ้าไม่ครบ 13 หลักให้คืนค่าเดิมที่สะอาดแล้ว
def clean_text(value):
    """ลบการขึ้นบรรทัดใหม่และช่องว่างส่วนเกิน (แก้ปัญหา Word ห่าง)"""
    if not value: return ''
    text = str(value)
    # เปลี่ยน Enter เป็นช่องว่าง
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    # ยุบช่องว่างซ้ำๆ ให้เหลือ 1 เคาะ
    text = ' '.join(text.split()) 
    return text

def clean_text_locked(value):
    """
    เปลี่ยนช่องว่างธรรมดา ให้เป็น Non-Breaking Space (\u00A0)
    (ผลลัพธ์เหมือนกด Ctrl+Shift+Space ใน Word)
    """
    if not value: return ''
    text = str(value)
    
    # 1. จัดระเบียบข้อความก่อน (ลบ Enter, ยุบวรรคซ้ำ)
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    text = ' '.join(text.split()) 
    
    # 2. 🔥 เปลี่ยนวรรคธรรมดา ' ' เป็นวรรค Shift+Space '\u00A0'
    text = text.replace(' ', '\u00A0')
    
    return text

def clean_decimal(value):
    """✨ ตัด .0 ออกจากตัวเลข (เช่น 320600.0 -> 320600)"""
    if not value: return 
    s = str(value).strip()
    if s.endswith(".0"):
        return s[:-2]
    return s

def remove_file(path: str):
    """ลบไฟล์ชั่วคราวหลังดาวน์โหลดเสร็จ"""
    try:
        os.remove(path)
    except Exception as e:
        print(f"Error deleting file: {e}")

def clean_text_strict(value):
    """
    ล้าง text ให้สะอาด:
    1. เปลี่ยน Non-Breaking Space (\u00A0) เป็น Space ธรรมดา (' ') เพื่อให้ Word ตัดคำได้
    2. ลบ Enter และยุบช่องว่างซ้ำ
    """
    if not value: return ''
    text = str(value)
    
    # 🔥 จุดสำคัญ: เปลี่ยนวรรค "ห้ามตัด" ให้เป็นวรรค "ตัดได้"
    text = text.replace('\u00A0', ' ') 
    
    # จัดการ Enter และ Space ส่วนเกิน
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    text = ' '.join(text.split()) 
    
    return text 

def format_money(value):
    """แปลงตัวเลขเป็นรูปแบบเงิน 18000 -> 18,000"""
    if value is None: return "0"
    try:
        # แปลงเป็น float ก่อน เผื่อกรณีเป็น string
        amount = float(value)
        # ใช้ format ให้มีคอมมาและไม่มีทศนิยม
        return "{:,.0f}".format(amount)
    except:
        return "0"
    
def format_month_year(date_val):
    """แปลงวันที่จาก DB เป็น 'เดือน พ.ศ.' เช่น ตุลาคม ๒๕๖๘"""
    if not date_val: 
        return ""
    
    months = [
        "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    
    try:
        month_name = months[date_val.month]
        year_thai = date_val.year + 543
        return f"{month_name} {year_thai}"
    except:
        return ""   
    
def format_day_month_year(date_val):
    """แปลงวันที่จาก DB เป็น 'เดือน พ.ศ.' เช่น ตุลาคม ๒๕๖๘"""
    if not date_val: 
        return ""
    
    months = [
        "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    
    try:
        day = date_val.day
        month_name = months[date_val.month]
        year_thai = date_val.year + 543
        return f"{day} {month_name} {year_thai}"
    except:
        return ""      
    

def wrap_location_at_snack(value):
    if not value: return ''
    text = str(value).strip()
    length = len(text)

    
    if length > 18 and length <= 90:
        return text[:51] + " " + text[51:]
    
    # ถ้าเกิน 70 (เช่น ศูนย์เรียนรู้ฯ ที่นับได้ 87) จะไม่ถูกวรรคครับ
    return text


def wrap_pos_at_snack(value):
    if not value: return ''
    text = str(value).strip()
    length = len(text)

    
    if length > 18 and length <= 40:
        return text[:15] + " " + text[15:]
    
    # ถ้าเกิน 70 (เช่น ศูนย์เรียนรู้ฯ ที่นับได้ 87) จะไม่ถูกวรรคครับ
    return text
# ----------------------------------------------

# ✅ รับ batch_code เป็น str (เผื่อบางทีส่งมาเป็น text)
@router.get("/generate-food/{batch_code}")
async def generate_document(batch_code: str, background_tasks: BackgroundTasks):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 2. SQL Query Main (เพิ่ม tb.id เพื่อเอาไปนับคน)
        sql_main = """ 
        SELECT 
            tb.id AS batch_id,  -- 👈 สำคัญ! ดึง ID มาด้วย
            tb.batch_code, tb.training_dates_text, tb.training_time, tb.target_group,
            mc.name AS course_name,
            mc.code AS course_code,
            tb.budget_speaker,
            tb.budget_material,
            tb.request_date,
            tb.request_doc_no,
            tb.borrow_date,
            tb.budget_food,
            tb.budget_snack,
            tb.duration_days,
            tb.number_of_snacks,
            (tb.budget_speaker * mc.hours) AS total_inst,
            mc.course_type AS training_type,
            mc.hours AS duration,
            pa.activity_name AS activity_name,
            pa.activity AS activity,
            pa.sub_activity_name AS sub_activity,
            pa.target_goal AS activity_goal,
            pa.kind_of_fiscal AS kind_of_fiscal,
            pa.fiscal_year AS kind_of_year,
            pa.expenses AS expenses,
            pj.name AS project_name,
            pl.name AS plan_name,
            loc.name AS location_name,
            inst.name AS instructor_name,
            inst.id_card AS instructor_id_card,
            s_ctrl.name AS controller_name, s_ctrl.position AS controller_pos,
            s_c1.name AS coord1_name, s_c1.position AS coord1_position,
            s_c2.name AS coord2_name,s_c2.position AS coord2_position,
            s_c3.name AS coord3_name,s_c3.position AS coord3_position,
            s_c4.name AS borrow_name,s_c4.position AS coord4_position
        FROM training_batches tb
        LEFT JOIN master_courses mc ON tb.course_id = mc.id
        LEFT JOIN master_locations loc ON tb.location_id = loc.id
        LEFT JOIN master_instructors inst ON tb.instructor_id = inst.id
        LEFT JOIN project_activities pa ON tb.activity_id = pa.id
        LEFT JOIN master_projects pj ON pa.project_id = pj.id
        LEFT JOIN master_plans pl ON pa.plan_id = pl.id
        LEFT JOIN master_staff s_ctrl ON tb.controller_id = s_ctrl.id
        LEFT JOIN master_staff s_c1 ON tb.coordinator_1_id = s_c1.id
        LEFT JOIN master_staff s_c2 ON tb.coordinator_2_id = s_c2.id
        LEFT JOIN master_staff s_c3 ON tb.coordinator_3_id = s_c3.id
        LEFT JOIN master_staff s_c4 ON tb.borrow_staff_id = s_c4.id
        WHERE tb.batch_code = %s 
        """
        
        cursor.execute(sql_main, (batch_code,))
        data = cursor.fetchone()

        if not data:
            raise HTTPException(status_code=404, detail=f"ไม่พบข้อมูลรุ่นรหัส {batch_code}")

        # 3. นับจำนวนผู้สมัคร (ใช้ ID ที่แม่นยำกว่า)
        # Logic: เอา batch_id (เลข 4) ไปค้นในตาราง applicants
        sql_count = """
                SELECT COUNT(*) AS total
                FROM applicants
                WHERE training_batch_id = %s
                
        """
        cursor.execute(sql_count, (data['batch_id'],)) 
        count_res = cursor.fetchone()
        applicant_count = count_res['total'] if count_res else 0
        raw_budget_material = float(data.get('budget_material') or 0)
        raw_budget_food = float(data.get('budget_food') or 0)
        raw_budget_snack = float(data.get('budget_snack') or 0)
        number_of_snacks = float(data.get('number_of_snacks') or 0)
        duration_days = float(data.get('duration_days') or 0)
        tatal_inst_value = float(data.get('total_inst') or 0)
        total_material_value = raw_budget_material * applicant_count
        total_food_value = raw_budget_food * applicant_count * duration_days
        total_snack_value = raw_budget_snack * applicant_count * number_of_snacks
        total_all_budget = ( tatal_inst_value + # ค่าวิทยากร (ถ้ามีตัวแปรเก็บค่าดิบไว้)
            total_material_value +  # ค่าวัสดุ
            total_food_value +      # ค่าอาหาร
            total_snack_value       # ค่าอาหารว่าง
        )
        total_all_food_snake = total_food_value + total_snack_value
        total_all_text = bahttext(total_all_budget)
        total_food_text = bahttext(total_food_value)
        total_f_s_text = bahttext(total_all_food_snake)
        # 4. สร้าง Context (ใช้ clean_decimal ตามที่ขอ)
        context = {
            'batch_code': data.get('batch_code'),
            'course_name': clean_text(data.get('course_name')),
            
            # ✅ ใช้ clean_decimal ตัด .0
            'course_code': clean_decimal(data.get('course_code')), 
            
            'plan_name': clean_text(data.get('plan_name')),
            'project_name': clean_text(data.get('project_name')),
            'activity_name': clean_text(data.get('activity_name')),
            'activity': clean_text_locked(data.get('activity')),
            'sub_activity_name': clean_text(data.get('sub_activity')),
            'goal': data.get('activity_goal'),
            'target_group': clean_text(data.get('target_group')),
            
            # ✅ จำนวนคนที่นับมาถูกต้อง
            'applicant_count': applicant_count,
            
            'training_type': clean_text(data.get('training_type')),
            
            # ✅ ใช้ clean_decimal กับระยะเวลาด้วย
            'duration': clean_decimal(data.get('duration')), 
            'request_date': format_month_year(data.get('request_date')), # วันเปิดฝึก
            'request_d_m_y': format_day_month_year(data.get('request_date')),
            'request_doc_no':data.get('request_doc_no'),
            'dates': clean_text(data.get('training_dates_text')),
            'borrow_date': format_month_year(data.get('borrow_date')), #วันขอยืม
            'time': clean_text(data.get('training_time')),
            'location': clean_text(data.get('location_name')),
            'location_snack': wrap_location_at_snack(data.get('location_name')),
            'instructor': clean_text(data.get('instructor_name')),
            'instructor_id': format_id_card(data.get('instructor_id_card')),
            'expenses': clean_text(data.get('expenses')),
            'kind_of_fiscal': clean_text(data.get('kind_of_fiscal')),
            'fiscal_year': clean_decimal(data.get('kind_of_year')),
            #ชื่อผู้ควบคุม
            'controller_name': clean_text(data.get('controller_name')),
            'controller_pos': clean_text(data.get('controller_pos')),
            #ชื่อผู้ประสานงาน
            'coord1_name': clean_text(data.get('coord1_name')),
            'coord1_pos': clean_text(data.get('coord1_position')),
            'coord2_name': clean_text(data.get('coord2_name')),
            'coord2_pos': clean_text(data.get('coord2_position')),
            'coord3_name': clean_text(data.get('coord3_name')),
            'coord3_pos': clean_text(data.get('coord3_position')),
            #ชื่อผู้ยืมเงิน
            'borrow_name': clean_text(data.get('borrow_name')),
            'borrow_pos': clean_text(data.get('coord4_position')),
            'borrow_pos_warp': wrap_pos_at_snack(data.get('coord4_position')),
            # ค่าตอบแทนต่อชั่วโมง
            'budget_speaker': format_money(data.get('budget_speaker')),
            'duration': clean_decimal(data.get('duration')),
            'total_inst': format_money(data.get('total_inst')),
            #คน * ค่าวัสดุ
            'applicant_count': applicant_count,
            'budget_material': format_money(raw_budget_material),
            'total_material': format_money(total_material_value),
            # food * tatal people * days 
            'budget_food': format_money(raw_budget_food),
            'duration_days': clean_decimal(duration_days),
            'total_food': format_money(total_food_value),
            # snack * tatal people * numbers
            'snack_mue': clean_decimal(number_of_snacks),
            'budget_snack': format_money(raw_budget_snack),
            'total_snack': format_money(total_snack_value),

            # total
            'total_all': format_money(total_all_budget),
            'total_all_thai': total_all_text,
            'total_food_thai':total_food_text,
            'total_f_s_thai':total_f_s_text,
            'total_f_s' :format_money(total_all_food_snake)
        }

        # 5. Gen Word และ Save ไฟล์
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../"))
        template_path = os.path.join(project_root, "templates", "food_borrow.docx")
        
        if not os.path.exists(template_path):
             raise HTTPException(status_code=500, detail=f"หาไฟล์ Template ไม่เจอที่: {template_path}")
        
        output_filename = f"เบิกค่าอาหาร {data['batch_code']}.docx"
        
        doc = DocxTemplate(template_path)
        doc.render(context)
        doc.save(output_filename)

        # เพิ่ม Task ลบไฟล์ทิ้งหลังจากส่งเสร็จ
        background_tasks.add_task(remove_file, output_filename)

        return FileResponse(
            path=output_filename, 
            filename=output_filename, 
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cursor.close()
        conn.close()