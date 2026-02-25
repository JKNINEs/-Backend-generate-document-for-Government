from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import date
from app.database import get_db_connection
from app.routers import (applicants,
                         courses,instructors,locations,staff,allow_practice,can_applicant,material,borrow_food
                         ,borrow_food_snack,complete_std,borrow_inst,Summary_of_the_loan,GenWord,activity_router
                         ,batch_router,loan_router,auth_router,calender_router,admin_router,template_router)


# ✅ ลบ events เก่าตอน server เริ่ม
def run_cleanup():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        today = date.today().strftime('%Y-%m-%d')
        cursor.execute("DELETE FROM events WHERE DATE(end_datetime) < %s", (today,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        print(f"✅ Cleanup: ลบ {deleted} events ที่หมดอายุแล้ว")
    except Exception as e:
        print(f"❌ Cleanup error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_cleanup()  # รันตอน startup
    yield          # server ทำงาน



app = FastAPI()

# 2. ตั้งค่า CORS (เพื่อให้หน้าเว็บ Frontend เรียก API ได้)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://27.254.144.167"], # หรือใส่เฉพาะ ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(template_router.router,prefix="/api/v1",tags=["Template"])
app.include_router(admin_router.router,prefix="/api/v1",tags=["Admin"])
app.include_router(calender_router.router,prefix="/api/v1",tags=["Calender"])
app.include_router(auth_router.router,prefix="/api/v1",tags=["Login"])
app.include_router(loan_router.router,prefix="/api/v1",tags=["Loan Record"])
app.include_router(batch_router.router,prefix="/api/v1",tags=["Training Batch"])
app.include_router(activity_router.router,prefix="/api/v1",tags=["Activity"])
app.include_router(GenWord.router,prefix="/api/v1",tags=["Gen-word"])
app.include_router(Summary_of_the_loan.router,prefix="/api/v1",tags=["Summary_of_load"])
app.include_router(borrow_inst.router,prefix="/api/v1",tags=["Allow Borrow Inst"])
app.include_router(complete_std.router,prefix="/api/v1",tags=["Announce date complete"])
app.include_router(borrow_food_snack.router,prefix="/api/v1",tags=["Allow Borrow Food Snack"])
app.include_router(borrow_food.router,prefix="/api/v1",tags=["Allow Borrow Food"])
app.include_router(material.router,prefix="/api/v1",tags=["Allow Material"])
app.include_router(can_applicant.router,prefix="/api/v1",tags=["Allow Applicant"])
app.include_router(allow_practice.router,prefix="/api/v1",tags=["Allow Practice"])
app.include_router(courses.router,prefix="/api/v1",tags=["Courses"])
app.include_router(applicants.router,prefix="/api/v1",tags=["Applicants"])
app.include_router(instructors.router,prefix="/api/v1",tags=["Instructors"])
app.include_router(locations.router,prefix="/api/v1",tags=["Locations"])
app.include_router(staff.router,prefix="/api/v1",tags=["Master Staff"]) # <--- และเพิ่มบรรทัดนี้
# 4. Route ทดสอบ (เอาไว้เช็คว่า Server รันอยู่ไหม)
@app.get("/")
def root():
    return {"message": "Server is running OK!"}