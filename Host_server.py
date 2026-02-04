import os
import asyncio
from typing import List
import time
from fastapi import File, UploadFile, HTTPException, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from Web.Backend.shortinfo_upload import router as shortinfo_router
from Web.Backend.richinfo_upload import router as richinfo_router
from Web.Backend.signin_api import router as signin_router
from Web.Backend.pgconpool import create_pool, close_pool
from Web.Backend.create_delete_dtb_api import router as create_db_router

app = FastAPI(title="Mega Input Processor", description="File Upload API", version="1.0.0")

# Exception handler cho validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"❌ Validation Error on {request.url.path}")
    print(f"   Errors: {exc.errors()}")
    print(f"   Body: {exc.body}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc.body)}
    )

app.include_router(signin_router)
app.include_router(create_db_router)
app.include_router(shortinfo_router)
app.include_router(richinfo_router)

#CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

#Middleware
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    # No cache cho static files
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# Mount static files
app.mount("/static", StaticFiles(directory="Web/Frontend"), name="static")

# thư mục gốc để lưu file upload
BASE_UPLOAD_DIR = "uploads"
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)


#Start + Stop server
@app.on_event("startup")
async def startup_event():
    """Chạy khi server khởi động"""
    print("🚀 Starting server...")
    await create_pool()
    print("✅ Server ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Chạy khi server shutdown"""
    print("🛑 Shutting down server...")
    await close_pool()
    print("✅ Server stopped!")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main upload page"""
    try:
        with open("Web/Frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Upload page not found</h1>", status_code=404)


