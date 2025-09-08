from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import asyncpg
import os
from os import getenv

router = APIRouter()

load_dotenv()
PG_HOST=os.getenv("PG_HOST")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")
OLLAMA_HOST=os.getenv("OLLAMA_HOST")

class SignInRequest(BaseModel):
    username: str
    password: str

@router.post("/signin")
async def signin(data: SignInRequest):
    username = data.username.strip()
    password = data.password
    conn = await asyncpg.connect(host=PG_HOST, user=PG_USER, password=PG_PASSWORD, database="postgres")
    user = await conn.fetchrow("SELECT * FROM users WHERE username=$1", username)
    if not user:
        await conn.close()
        return {"success": False, "detail": "User không tồn tại!"}
    if user['password'] != password:
        await conn.close()
        return {"success": False, "detail": "Sai mật khẩu!"}
    dtbase = user.get('dtbase') or ""
    await conn.close()
    return {"success": True, "username": username, "dtbase": dtbase}
