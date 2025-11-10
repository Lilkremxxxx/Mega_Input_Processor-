import os
import asyncio
import pandas as pd
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders.image import UnstructuredImageLoader
from dotenv import load_dotenv
import asyncpg
import openpyxl
from PIL import Image
from datetime import datetime
import time


load_dotenv()
PG_HOST=os.getenv("PG_HOST")
PG_PORT=os.getenv("PG_PORT")
PG_DBNAME=os.getenv("PG_DBNAME")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")


async def process_uploaded_files(file_info_list, groupId):
    """
    Hàm xử lý các file đã upload.
    Tham số: list các dict chứa {'path': file_path, 'name': filename}.
    """
    for file_info in file_info_list:
        file_path = file_info['path']
        filename = file_info['name']
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".csv":
            await csv_process(file_path, groupId, filename)
        elif ext == '.xlsx':
            await xlsx_process(file_path, groupId, filename)
        elif ext in [".jpg", ".png"]:
            print('Hiện tại web chưa hỗ trợ định dạng ảnh')
        else:
            print(f"File {file_path} uploaded but no specific processing defined.")
           

async def csv_process(file_path, groupId, filename):
    ''' Xử lý file csv: parse dữ liệu (columns + data)
    Sau đó insert vào database '''

    start_time = datetime.now()
    name_tb = filename + "_shortinfo"
    df = pd.read_csv(file_path, nrows=0, delimiter=',', encoding="utf-8-sig")
    # Lấy toàn bộ columns
    columns = df.columns.tolist()
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
        host=PG_HOST, 
        port=int(PG_PORT),
        database="Documents",
        user=PG_USER, 
        password=PG_PASSWORD
    )
    #Nếu bảng tồn tại thì xóa
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    await conn.execute(f'DROP TABLE IF EXISTS "{name_tb}";')

    columns_def = ", ".join([f'"{col}" text' for col in columns])
    await conn.execute(f'CREATE TABLE IF NOT EXISTS "{name_tb}" ({columns_def});')
    Contents = [doc.page_content for doc in docs]
    for item in Contents:
        # Parse lại theo cấu trúc của CSVLoader
        # Format: "row: 0\ncolumn1: value1\ncolumn2: value2"
        lines = item.split('\n')
        values = []
        for line in lines[1:]:  # Bỏ qua dòng "row: X"
            if ':' in line:
                _, value = line.split(':', 1)
                values.append(value.strip())
        
        placeholders = ','.join([f'${i+1}' for i in range(len(columns))])
        columns_sql = ', '.join(f'"{col}"' for col in columns)
        insert_sql = f'INSERT INTO "{name_tb}" ({columns_sql}) VALUES ({placeholders})'
        await conn.execute(insert_sql, *values)
    # Insert vào bảng Manager
    await conn.execute(
        'INSERT INTO "Manager" ("groupId", "fileName", "documentType", "tableName") VALUES ($1, $2, $3, $4)',
        groupId, filename, 'shortinfo', name_tb
    )
    await conn.close()
    print(f"✅ Created table {name_tb} and inserted {len(docs)} rows.")
    end_time = datetime.now()
    duration = end_time - start_time
    print("Thời gian xử lý:", duration.total_seconds())




async def xlsx_process(file_path, groupId, filename):
    ''' Xử lý file xlsx: parse dữ liệu (columns + data) từ sheet đầu tiên'''
    start_time = datetime.now()
    df = pd.read_excel(file_path, sheet_name=0)  # sheet_name=0 để lấy sheet đầu tiên
    table_name = f"{filename}_shortinfo"
    conn = await asyncpg.connect(
        host=PG_HOST, 
        port=int(PG_PORT),
        database="Documents", 
        user=PG_USER, 
        password=PG_PASSWORD
    )
    # Lấy columns từ DataFrame
    columns = df.columns.tolist()
    columns_def = ", ".join([f'"{col}" text' for col in columns])
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    await conn.execute(f'DROP TABLE IF EXISTS "{table_name}";')
    await conn.execute(f'CREATE TABLE "{table_name}" ({columns_def});')
    # Insert data
    for _, row in df.iterrows():
        values = [None if pd.isna(row[col]) else str(row[col]) for col in df.columns]
        placeholders = ','.join([f'${i+1}' for i in range(len(columns))])
        columns_sql = ', '.join(f'"{col}"' for col in columns)
        insert_sql = f'INSERT INTO "{table_name}" ({columns_sql}) VALUES ({placeholders})'
        await conn.execute(insert_sql, *values)
    
    # Insert vào bảng Manager
    await conn.execute(
        'INSERT INTO "Manager" ("groupId", "fileName", "documentType", "tableName") VALUES ($1, $2, $3, $4)',
        groupId, filename, 'shortinfo', table_name
    )

    print(f"✅ Created table {table_name} and inserted {len(df)} rows from first sheet.")
    await conn.close()
    end_time = datetime.now()
    duration = end_time - start_time
    print("Thời gian xử lý:", duration.total_seconds())

    # Xử lý nhiều sheets nhưng ...
    '''
    # Xử lý từng sheet
    for sheet_name in sheet_names:
        # Tên bảng = tên file + tên sheet
        table_name = f"{dt_base}_shortinfo"
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        columns = df.columns.tolist()
        columns_def = ", ".join([f'"{col}" text' for col in columns])
        
        #await conn.execute(f'DROP TABLE IF EXISTS "{table_name}";')
        await conn.execute(f'CREATE TABLE "{table_name}" ({columns_def});')
        # Insert data
        for _, row in df.iterrows():
            values = tuple(None if pd.isna(row[col]) else str(row[col]) for col in columns)
            placeholders = ','.join([f'${i+1}' for i in range(len(columns))])
            columns_sql = ', '.join(f'"{col}"' for col in columns)
            insert_sql = f'INSERT INTO "{table_name}" ({columns_sql}) VALUES ({placeholders})'
            await conn.execute(insert_sql, *values)
        print(f"✅ Created table {table_name} and inserted {len(df)} rows.")
   ''' 

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

    