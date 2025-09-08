from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncpg
import psycopg2
import os

router = APIRouter()
PG_HOST = os.getenv("PG_HOST")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

class CreateDbRequest(BaseModel):
    username: str

@router.post("/create_database")
async def create_database(data: CreateDbRequest):
    dbname = data.username.strip()

    conn = psycopg2.connect(
        host=PG_HOST,dbname="postgres",
        user=PG_USER, password=PG_PASSWORD
    )
    
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f'DROP DATABASE IF EXISTS "{dbname}"')
    cur.execute(f'CREATE DATABASE "{dbname}"')
    cur.close()
    conn.close()

    conn1 = await asyncpg.connect(
        host=PG_HOST, database=dbname,
        user=PG_USER, password=PG_PASSWORD
    )
    await conn1.close()
