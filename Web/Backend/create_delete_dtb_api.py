import os
import asyncpg
import psycopg2
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()
router = APIRouter()
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

class CreateDbRequest(BaseModel):
    username: str


@router.post("/create_database")
async def create_database(data: CreateDbRequest):
    username = data.username.strip()
    dbname = username
    try:
        # Kiểm tra user đã có database chưa
        conn_check = await asyncpg.connect(
            host=PG_HOST, 
            port=int(PG_PORT),
            user=PG_USER, 
            password=PG_PASSWORD, 
            database="postgres"
        )
        
        user = await conn_check.fetchrow("SELECT * FROM users WHERE username=$1", username)
        if not user:
            await conn_check.close()
            return {"success": False, "detail": "User không tồn tại!"}
        if user.get('database'):
            await conn_check.close()
            return {"success": False, "detail": f"User đã có database: {user['database']}"}
        await conn_check.close()

        # Tạo database mới
        conn = psycopg2.connect(
            host=PG_HOST, 
            port=int(PG_PORT),
            dbname= "postgres",
            user=PG_USER, 
            password=PG_PASSWORD
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f'CREATE DATABASE "{dbname}"')
        cur.close()
        conn.close()

        # Kiểm tra kết nối database mới tạo
        conn1 = await asyncpg.connect(
            host=PG_HOST, 
            port=int(PG_PORT),
            database=dbname,
            user=PG_USER, 
            password=PG_PASSWORD
        )
        await conn1.execute('CREATE EXTENSION IF NOT EXISTS vector;')

        await conn1.close()

        # Cập nhật cột dtbase cho user
        conn2 = await asyncpg.connect(
            host=PG_HOST, 
            port=int(PG_PORT),
            user=PG_USER, 
            password=PG_PASSWORD, 
            database= "postgres"
        )
        await conn2.execute("UPDATE users SET database=$1 WHERE username=$2", dbname, username)
        await conn2.close()

        return {"success": True, "dbname": dbname}
    except Exception as e:
        return {"success": False, "detail": str(e)}

# Xóa database và cập nhật bảng users
class DeleteDbRequest(BaseModel):
    username: str

@router.post("/delete_database")
async def delete_database(data: DeleteDbRequest):
    username = data.username.strip()
    dbname = username
    try:
        conn = psycopg2.connect(
            host=PG_HOST, 
            port=int(PG_PORT),
            dbname="postgres",
            user=PG_USER, 
            password=PG_PASSWORD
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f'DROP DATABASE IF EXISTS "{dbname}"')
        cur.close()
        conn.close()

        # Cập nhật cột dtbase về trống cho user
        conn2 = await asyncpg.connect(
            host=PG_HOST, 
            port=int(PG_PORT),
            user=PG_USER, 
            password=PG_PASSWORD, 
            database="postgres"
        )
        await conn2.execute("UPDATE users SET database='' WHERE username=$1", username)
        await conn2.close()

        return {"success": True}
    except Exception as e:
        return {"success": False, "detail": str(e)}
