from fastapi import File, UploadFile, HTTPException, APIRouter, Form
from typing import List
import os

router = APIRouter()
BASE_UPLOAD_DIR = "../../uploads/shortinfo"
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

@router.post("/upload_shortinfo")
async def upload_shortinfo(files: List[UploadFile] = File(...), dt_base: str = Form(...)):
    saved_files = []
    for file in files:
        try:
            _, ext = os.path.splitext(file.filename)
            ext = ext.lower().lstrip(".")
            if ext not in ["csv", "xlsx", "jpg", "png"]:
                raise HTTPException(status_code=400, detail=f"File {file.filename} không đúng định dạng shortinfo!")
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
    # Gọi xử lý file shortinfo
    from Web.Backend.Short_process_file import process_uploaded_files as short_process
    await short_process(saved_files, dt_base)
    return {"message": f"Successfully uploaded {len(saved_files)} shortinfo files and processed", "files": saved_files}
