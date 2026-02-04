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
BASE_UPLOAD_DIR = "../../uploads/richinfo"
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

class DeleteTableRequest(BaseModel):
    groupId: str

@router.post("/upload_richinfo")
async def upload_richinfo(files: List[UploadFile] = File(...), groupId: str = Form(...)):
    saved_files = []
    file_info = []  # Store both file_path and filename
    for file in files:
        try:
            filename, ext = os.path.splitext(file.filename)
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
            file_info.append({"path": file_path, "name": filename})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi upload {file.filename}: {str(e)}")
        finally:
            await file.close()
    # Gọi xử lý file richinfo
    from Web.Backend.Rich_process_file import process_uploaded_files as rich_process
    await rich_process(file_info, groupId)
    return {"message": f"Successfully uploaded {len(saved_files)} richinfo files and processed", "files": saved_files}

@router.post("/delete_tb_richinfo")
async def delete_tb_richinfo(data: DeleteTableRequest):
    """Xóa table richinfo của groupId"""
    try:
        groupId = data.groupId.strip()
        table_name = f"{groupId}rag_qa"
        
        # Kết nối đến database của groupId
        conn = await asyncpg.connect(
            host=PG_HOST,
            database="postgres",
            port=int(PG_PORT),
            user=PG_USER,
            password=PG_PASSWORD,

        )
        
        # Xóa table nếu tồn tại
        await conn.execute(f'DROP TABLE IF EXISTS "{table_name}";')
        await conn.close()
        print(f"Đã xóa table {table_name} thành công!")
        
        return {"success": True, "message": f"Đã xóa table {table_name} thành công!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa table: {str(e)}")
