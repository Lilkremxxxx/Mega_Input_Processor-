import os
import asyncio
import pandas as pd
from langchain_community.document_loaders import CSVLoader
from langchain_unstructured import UnstructuredLoader
from dotenv import load_dotenv
from os import getenv
import asyncpg
import openpyxl
from PIL import Image
from langchain_community.document_loaders.image import UnstructuredImageLoader


load_dotenv()
PG_HOST=os.getenv("PG_HOST")
PG_DBNAME=os.getenv("PG_DBNAME")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")


async def process_uploaded_files(file_paths, dt_base):
    """
    Hàm xử lý các file đã upload.
    Tham số: list các đường dẫn file.
    """
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".csv":
            await csv_process(file_path, dt_base)
        elif ext == '.xlsx':
            await xlsx_process(file_path, dt_base)
        elif ext in [".jpg", ".png"]:
            print('Hiện tại web chưa hỗ trợ định dạng ảnh')
        else:
            print(f"File {file_path} uploaded but no specific processing defined.")
           

async def csv_process(file_path, dt_base):
    ''' Xử lý file csv: parse dữ liệu (columns + data)
    Sau đó insert vào database '''
    
    name_dtb = os.path.splitext(os.path.basename(file_path))[0]
    df = pd.read_csv(file_path, nrows=0, delimiter=',', encoding="utf-8-sig")
    columns = df.columns.tolist()[0].split(",") 
    # Loader
    loader = CSVLoader(
        file_path=file_path,
        encoding="utf-8-sig",
        csv_args={'delimiter': ','}
    )
    docs = []
    async for doc in loader.alazy_load():
        docs.append(doc)
    conn = await asyncpg.connect(
        host=PG_HOST, database=dt_base,
        user=PG_USER, password=PG_PASSWORD
    )
    #Nếu bảng tồn tại thì xóa
    await conn.execute(f'DROP TABLE IF EXISTS "{name_dtb}";')

    columns_def = ", ".join([f'"{col}" text' for col in columns])
    await conn.execute(f'CREATE TABLE IF NOT EXISTS "{name_dtb}" ({columns_def});')
    Contents = [doc.page_content for doc in docs]
    for item in Contents:
        _, value_part = item.split(":", 1)
        values = [v.strip() for v in value_part.split(",")]
        placeholders = ','.join([f'${i+1}' for i in range(len(columns))])
        columns_sql = ', '.join(f'"{col}"' for col in columns)
        insert_sql = f'INSERT INTO "{name_dtb}" ({columns_sql}) VALUES ({placeholders})'
        await conn.execute(insert_sql, *values)
    await conn.close()
    print(f"✅ Created table {name_dtb} and inserted {len(docs)} rows.")




async def xlsx_process(file_path, dt_base):
    ''' Xử lý file xlsx: parse dữ liệu (columns + data) từ tất cả sheets
    Mỗi sheet sẽ thành một bảng riêng biệt'''
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    # Đọc tất cả sheet names
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    conn = await asyncpg.connect(host=PG_HOST, database=dt_base, user=PG_USER, password=PG_PASSWORD)
    # Xử lý từng sheet
    for sheet_name in sheet_names:
        # Tên bảng = tên file + tên sheet
        table_name = f"{base_name}_{sheet_name}"
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        columns = df.columns.tolist()
        columns_def = ", ".join([f'"{col}" text' for col in columns])
        
        await conn.execute(f'DROP TABLE IF EXISTS "{table_name}";')
        await conn.execute(f'CREATE TABLE "{table_name}" ({columns_def});')
        # Insert data
        for _, row in df.iterrows():
            values = tuple(None if pd.isna(row[col]) else str(row[col]) for col in columns)
            placeholders = ','.join([f'${i+1}' for i in range(len(columns))])
            columns_sql = ', '.join(f'"{col}"' for col in columns)
            insert_sql = f'INSERT INTO "{table_name}" ({columns_sql}) VALUES ({placeholders})'
            await conn.execute(insert_sql, *values)
        print(f"✅ Created table {table_name} and inserted {len(df)} rows.")
    await conn.close()

async def img_process(file_path):
    """Xử lý ảnh đơn giản - chỉ đọc và hiển thị thông tin cơ bản"""
    try:
        img = Image.open(file_path)
        print(f"✅ Processed image: {os.path.basename(file_path)}")
        print(f"   - Size: {img.size}")
        print(f"   - Format: {img.format}")
        print(f"   - Mode: {img.mode}")

    except Exception as e:
        print(f"❌ Error processing image {file_path}: {str(e)}")

    