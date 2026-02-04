import os
import asyncpg
from fastapi import File, UploadFile, HTTPException, APIRouter, Form
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
PG_HOST = os.getenv("PG_HOST")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_PORT=os.getenv("PG_PORT")

router = APIRouter()
BASE_UPLOAD_DIR = "../../uploads/shortinfo"
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

class DeleteTableRequest(BaseModel):
    groupId: str

@router.post("/upload_shortinfo")
async def upload_shortinfo(files: List[UploadFile] = File(...), groupId: str = Form(...)):
    saved_files = []
    file_info = []  # Store both file_path and filename
    for file in files:
        try:
            filename, ext = os.path.splitext(file.filename)
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
            file_info.append({"path": file_path, "name": filename})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi upload {file.filename}: {str(e)}")
        finally:
            await file.close()
    # Gọi xử lý file shortinfo
    from Web.Backend.Short_process_file import process_uploaded_files as short_process
    await short_process(file_info, groupId)
    return {"message": f"Successfully uploaded {len(saved_files)} shortinfo files and processed", "files": saved_files}

@router.post("/delete_tb_shortinfo")
async def delete_tb_shortinfo(data: DeleteTableRequest):
    """Xóa table shortinfo của groupId"""
    try:
        groupId = data.groupId.strip()
        table_name = f"{groupId}_shortinfo"
        
        # Kết nối đến database của groupId
        conn = await asyncpg.connect(
            host=PG_HOST,
            port=int(PG_PORT),
            database="postgres",
            user=PG_USER,
            password=PG_PASSWORD
        )
        
        # Xóa table nếu tồn tại
        await conn.execute(f'DROP TABLE IF EXISTS "{table_name}";')
        await conn.close()
        print(f"Đã xóa table {table_name} thành công!")
        
        return {"success": True, "message": f"Đã xóa table {table_name} thành công!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa table: {str(e)}")
