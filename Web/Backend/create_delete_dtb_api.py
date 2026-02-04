import os
import asyncpg
import psycopg2
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from Web.Backend.pgconpool import get_db
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
async def create_database(data: CreateDbRequest, 
                          db: asyncpg.Connection = Depends(get_db)):
    username = data.username.strip()
    dbname = username
    try:
        user = await db.fetchrow("SELECT * FROM users WHERE username=$1", username)
        if not user:
            await db.close()
            return {"success": False, "detail": "User không tồn tại!"}
        if user.get('database'):
            await db_check.close()
            return {"success": False, "detail": f"User đã có database: {user['database']}"}
        await db_check.close()

        # Tạo database mới
        conn = psycopg2.dbect(
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
        db1 = await asyncpg.dbect(
            host=PG_HOST, 
            port=int(PG_PORT),
            database=dbname,
            user=PG_USER, 
            password=PG_PASSWORD
        )
        await db1.execute('CREATE EXTENSION IF NOT EXISTS vector;')
        await db1.close()

        #Update user cho dtb
        await db.execute("UPDATE users SET database=$1 WHERE username=$2", dbname, username)
        await db.close()
        return {"success": True, "dbname": dbname}
    except Exception as e:
        return {"success": False, "detail": str(e)}

# Xóa database và cập nhật bảng users
class DeleteDbRequest(BaseModel):
    username: str

@router.post("/delete_database")
async def delete_database(data: DeleteDbRequest, 
                          db: asyncpg.Connection = Depends(get_db)):
    username = data.username.strip()
    dbname = username
    try:
        conn = psycopg2.dbect(
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
        await db.execute("UPDATE users SET database='' WHERE username=$1", username)
        await db.close()

        return {"success": True}
    except Exception as e:
        return {"success": False, "detail": str(e)}
