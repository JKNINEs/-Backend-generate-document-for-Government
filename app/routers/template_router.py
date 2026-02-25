from fastapi import APIRouter, HTTPException, Request, Depends, UploadFile, File
from fastapi.responses import FileResponse
from app.database import get_db_connection
import os
import shutil

router = APIRouter()

# Path to templates directory (adjust as needed)
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../../templates")

# Allowed template filenames (whitelist for security)
ALLOWED_TEMPLATES = {
    "Template.docx",
    "announce_date.docx",
    "applicant.docx",
    "food_borrow.docx",
    "food_snack_borrow.docx",
    "inst_borrow.docx",
    "material.docx",
    "refund_summary.docx",
}

TEMPLATE_DISPLAY_NAMES = {
    "Template.docx" : "ประกาศฝึก",
    "announce_date.docx":     "ประกาศจบ",
    "applicant.docx":         "ผู้มีสิทธิ์เข้าร่วมอบรม",
    "food_borrow.docx":       "ยืมอาหาร",
    "food_snack_borrow.docx": "ยืมอาหารว่าง",
    "inst_borrow.docx":       "ยืมค่าวิทยากร",
    "material.docx":          "วัสดุ",
    "refund_summary.docx":    "สรุปการคืนเงิน",
}


def require_admin(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="กรุณาเข้าสู่ระบบ")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE session_token = %s", (token,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Session ไม่ถูกต้อง")
        if user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึง (Admin เท่านั้น)")
        return user
    finally:
        cursor.close()
        conn.close()


@router.get("/admin/templates")
def list_templates(admin: dict = Depends(require_admin)):
    """List all template files with their status (exists/missing)."""
    templates = []
    for filename in sorted(ALLOWED_TEMPLATES):
        filepath = os.path.join(TEMPLATES_DIR, filename)
        exists = os.path.isfile(filepath)
        size = os.path.getsize(filepath) if exists else 0
        mtime = os.path.getmtime(filepath) if exists else None

        templates.append({
            "filename": filename,
            "display_name": TEMPLATE_DISPLAY_NAMES.get(filename, filename),
            "exists": exists,
            "size_bytes": size,
            "updated_at": mtime,
        })
    return {"status": "success", "templates": templates}


@router.get("/admin/templates/{filename}/download")
def download_template(filename: str, admin: dict = Depends(require_admin)):
    if filename not in ALLOWED_TEMPLATES:
        raise HTTPException(status_code=400, detail="ไม่อนุญาตให้ดาวน์โหลดไฟล์นี้")

    filepath = os.path.join(TEMPLATES_DIR, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f"ไม่พบไฟล์ template '{filename}'")

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",  # ← เพิ่ม
            "Pragma": "no-cache",
        }
    )


@router.post("/admin/templates/{filename}/upload")
async def upload_template(
    filename: str,
    file: UploadFile = File(...),
    admin: dict = Depends(require_admin),
):
    """Replace a template file with an uploaded .docx file."""
    if filename not in ALLOWED_TEMPLATES:
        raise HTTPException(status_code=400, detail="ไม่อนุญาตให้อัปโหลดไฟล์นี้")

    # Validate uploaded file is .docx
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="อัปโหลดได้เฉพาะไฟล์ .docx เท่านั้น")

    # Check MIME type (basic check)
    allowed_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if file.content_type and file.content_type not in (allowed_mime, "application/octet-stream"):
        raise HTTPException(status_code=400, detail="ประเภทไฟล์ไม่ถูกต้อง")

    filepath = os.path.join(TEMPLATES_DIR, filename)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)

    # Save to a temp file first, then replace atomically
    tmp_path = filepath + ".tmp"
    try:
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        os.replace(tmp_path, filepath)
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"บันทึกไฟล์ไม่สำเร็จ: {str(e)}")
    finally:
        await file.close()

    size = os.path.getsize(filepath)
    return {
        "status": "success",
        "message": f"อัปโหลด template '{filename}' สำเร็จ",
        "filename": filename,
        "size_bytes": size,
    }