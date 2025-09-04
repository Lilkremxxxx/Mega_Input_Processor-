import os
from Web.Backend.shortinfo_upload import router as shortinfo_router
from Web.Backend.richinfo_upload import router as richinfo_router
import asyncio
from fastapi import File, UploadFile, HTTPException, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from process_files import process_uploaded_files

app = FastAPI(title="Mega Input Processor", description="File Upload API", version="1.0.0")
app.include_router(shortinfo_router)
app.include_router(richinfo_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files
app.mount("/static", StaticFiles(directory="Web/Frontend"), name="static")

# thư mục gốc để lưu file upload
BASE_UPLOAD_DIR = "uploads"
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main upload page"""
    try:
        with open("Web/Frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Upload page not found</h1>", status_code=404)


@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    saved_files = []

    for file in files:
        try:
            # lấy phần mở rộng (vd: ".csv", ".jpg")
            _, ext = os.path.splitext(file.filename)
            ext = ext.lower().lstrip(".")

            # tạo thư mục con theo định dạng
            subdir = os.path.join(BASE_UPLOAD_DIR, ext)
            os.makedirs(subdir, exist_ok=True)

            # đường dẫn đầy đủ
            file_path = os.path.join(subdir, file.filename)

            # đọc file (async)
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)

            saved_files.append(file_path)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi upload {file.filename}: {str(e)}")
        finally:
            await file.close()

    # Sau khi upload xong, gọi hàm xử lý async
    try:
        await process_uploaded_files(saved_files)
    except Exception as e:
        print(f"Error while processing files: {e}")

    return {"message": f"Successfully uploaded {len(saved_files)} files", "files": saved_files}
