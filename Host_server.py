import os
import asyncio
from typing import List
from fastapi import File, UploadFile, HTTPException, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from Web.Backend.shortinfo_upload import router as shortinfo_router
from Web.Backend.richinfo_upload import router as richinfo_router
from Web.Backend.signin_api import router as signin_router
from Web.Backend.create_delete_dtb_api import router as create_db_router

app = FastAPI(title="Mega Input Processor", description="File Upload API", version="1.0.0")
app.include_router(signin_router)
app.include_router(create_db_router)
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


