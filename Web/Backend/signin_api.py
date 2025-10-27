import os
import asyncpg
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
PG_HOST=os.getenv("PG_HOST")
PG_PORT=os.getenv("PG_PORT")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")
OLLAMA_HOST=os.getenv("OLLAMA_HOST")

class SignInRequest(BaseModel):
    username: str
    password: str

@router.post("/signin")
async def signin(data: SignInRequest):
    try:
        username = data.username.strip()
        password = data.password
        print(f"Đang đăng nhập: {username}")
        conn = await asyncpg.connect(
            host=PG_HOST, 
            port=int(PG_PORT),
            user=PG_USER, 
            password=PG_PASSWORD, 
            database="ai_db"
        )
        user = await conn.fetchrow("SELECT * FROM users WHERE username=$1", username)
        if not user:
            await conn.close()
            print(f"Không tìm thấy user: {username}")
            return {"success": False, "detail": "User không tồn tại!"}
        if user['password'] != password:
            await conn.close()
            print(f"Sai mật khẩu cho user: {username}")
            return {"success": False, "detail": "Sai mật khẩu!"}
        database = user.get('database') or ""
        await conn.close()
        
        print(f"Đăng nhập thành công: {username}, database: {database}")
        return {"success": True, "username": username, "database": database}
    except Exception as e:
        print(f"Lỗi đăng nhập: {str(e)}")
        return {"success": False, "detail": f"Lỗi server: {str(e)}"}
