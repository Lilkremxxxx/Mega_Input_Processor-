# process_files.py - Xử lý file sau khi upload
import os
import asyncio
import pandas as pd
from langchain_community.document_loaders import CSVLoader
from langchain_unstructured import UnstructuredLoader
from dotenv import load_dotenv
from os import getenv
import asyncpg

load_dotenv()
PG_HOST=os.getenv("PG_HOST")
PG_DBNAME=os.getenv("PG_DBNAME")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")
OLLAMA_HOST=os.getenv("OLLAMA_HOST")

async def process_uploaded_files(file_paths):
    """
    Hàm xử lý các file đã upload.
    Tham số: list các đường dẫn file.
    """
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".csv":
           await csv_process(file_path)

        elif ext == '.docx' or ext == '.txt':
            await docx_text_process(file_path)
        

        elif ext in [".jpg", ".png"]:
            from PIL import Image
            img = Image.open(file_path)
            print(f"Processed image: {file_path}, size: {img.size}")
            
        else:
            print(f"File {file_path} uploaded but no specific processing defined.")
            # Có thể thêm xử lý chung cho text files, etc.


async def csv_process(file_path):

    ''' Xử lý file csv: parse dữ liệu (columns + data)
    Sau đó insert vào dtbase'''
    name_dtb = os.path.splitext(os.path.basename(file_path))[0]
    df = pd.read_csv(file_path,nrows=0)
    loader = CSVLoader(file_path=file_path, encoding="utf-8",csv_args={
    'delimiter': ',',
    'quotechar': '"',})
    docs = [doc async for doc in loader.alazy_load()]
    columns = df.columns.tolist()
    col_defs = ", ".join([f'"{col}" text' for col in columns])

    conn = await asyncpg.connect(host=PG_HOST, database=PG_DBNAME, user=PG_USER, password=PG_PASSWORD)
    await conn.execute(
        f"create table if not exists {name_dtb}({col_defs})"
    )
    # Parse và insert dữ liệu
    for doc in docs:
        # Parse page_content thành dict
        lines = doc.page_content.split('\n')
        row_dict = {}
        for line in lines:
            # Loại bỏ BOM nếu có ở đầu dòng
            if line.startswith('\ufeff'):
                line = line.replace('\ufeff', '', 1)
            if ':' in line:
                key, value = line.split(':', 1)
                row_dict[key.strip()] = value.strip()
        # Tạo tuple giá trị đúng thứ tự columns
        values = tuple(row_dict.get(col, None) for col in columns)
        
        # Insert vào bảng
        placeholders = ','.join(['$'+str(i+1) for i in range(len(columns))])
        columns_sql = ', '.join(f'"{col}"' for col in columns)
        insert_sql = f'INSERT INTO {name_dtb} ({columns_sql}) VALUES ({placeholders})'
        await conn.execute(insert_sql, *values)
    await conn.close()
    
    print(f"✅ Created table {name_dtb} and inserted {len(docs)} rows.")


async def docx_text_process(file_path):
    name_dtb = os.path.splitext(os.path.basename(file_path))[0]
    loader = UnstructuredLoader(
    file_path=file_path, mode="elements", strategy="fast",
)
    docs = loader.load()
    doccc = []
    for doc in docs:
        # Parse page_content thành dict
        lines = doc.page_content
        doccc.append(lines)
        
    print(doccc)
    