from fastapi import File, UploadFile, HTTPException, APIRouter
from typing import List
import os

router = APIRouter()
BASE_UPLOAD_DIR = "../../uploads/richinfo"
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

@router.post("/upload_richinfo")
async def upload_richinfo(files: List[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        try:
            _, ext = os.path.splitext(file.filename)
            ext = ext.lower().lstrip(".")
            if ext not in ["csv", "xlsx", "docx", "txt", "pdf", "jpg", "png"]:
                raise HTTPException(status_code=400, detail=f"File {file.filename} không đúng định dạng richinfo!")
            subdir = os.path.join(BASE_UPLOAD_DIR, ext)
            os.makedirs(subdir, exist_ok=True)
            file_path = os.path.join(subdir, file.filename)
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            saved_files.append(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi upload {file.filename}: {str(e)}")
        finally:
            await file.close()
    # Gọi xử lý file richinfo
    from Web.Backend.Rich_process_file import process_uploaded_files as rich_process
    import asyncio
    await rich_process(saved_files)
    return {"message": f"Successfully uploaded {len(saved_files)} richinfo files and processed", "files": saved_files}
