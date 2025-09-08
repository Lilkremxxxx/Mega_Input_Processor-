from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncpg
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()
router = APIRouter()
PG_HOST = os.getenv("PG_HOST")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

class CreateDbRequest(BaseModel):
    username: str



@router.post("/create_database")
async def create_database(data: CreateDbRequest):
    dbname = data.username.strip()
    try:
        conn = psycopg2.connect(
            host=PG_HOST, dbname="postgres",
            user=PG_USER, password=PG_PASSWORD
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f'DROP DATABASE IF EXISTS "{dbname}"')
        cur.execute(f'CREATE DATABASE "{dbname}"')
        cur.close()
        conn.close()

        # Kiểm tra kết nối database mới tạo
        conn1 = await asyncpg.connect(
            host=PG_HOST, database=dbname,
            user=PG_USER, password=PG_PASSWORD
        )
        await conn1.close()

        # Cập nhật cột dtbase cho user
        conn2 = await asyncpg.connect(host=PG_HOST, user=PG_USER, password=PG_PASSWORD, database="postgres")
        await conn2.execute("UPDATE users SET dtbase=$1 WHERE username=$2", dbname, dbname)
        await conn2.close()

        return {"success": True, "dbname": dbname}
    except Exception as e:
        return {"success": False, "detail": str(e)}

# Xóa database và cập nhật bảng users
class DeleteDbRequest(BaseModel):
    username: str

@router.post("/delete_database")
async def delete_database(data: DeleteDbRequest):
    dbname = data.username.strip()
    try:
        conn = psycopg2.connect(
            host=PG_HOST, dbname="postgres",
            user=PG_USER, password=PG_PASSWORD
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f'DROP DATABASE IF EXISTS "{dbname}"')
        cur.close()
        conn.close()

        # Cập nhật cột dtbase về trống cho user
        conn2 = await asyncpg.connect(host=PG_HOST, user=PG_USER, password=PG_PASSWORD, database="postgres")
        await conn2.execute("UPDATE users SET dtbase='' WHERE username=$1", dbname)
        await conn2.close()

        return {"success": True}
    except Exception as e:
        return {"success": False, "detail": str(e)}
