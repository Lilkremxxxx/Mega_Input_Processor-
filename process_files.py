# process_files.py - Xử lý file sau khi upload
import os
import asyncio
import pandas as pd
from langchain_community.document_loaders import CSVLoader
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

        elif ext in [".jpg", ".png"]:
            from PIL import Image
            img = Image.open(file_path)
            print(f"Processed image: {file_path}, size: {img.size}")
            
        else:
            print(f"File {file_path} uploaded but no specific processing defined.")
            # Có thể thêm xử lý chung cho text files, etc.


async def csv_process(file_path):
    name_dtb = os.path.splitext(os.path.basename(file_path))[0]
    df = pd.read_csv(file_path,nrows=0)
    loader = CSVLoader(file_path=file_path, encoding="utf-8",csv_args={
    'delimiter': ',',
    'quotechar': '"',})
    # alazy_load là async generator → phải duyệt bằng async for
    docs = [doc async for doc in loader.alazy_load()]
    columns = df.columns.tolist()
    col_defs = ", ".join([f'"{col}" text' for col in columns])

    csv_process = await asyncpg.connect(host=PG_HOST, database=PG_DBNAME, user=PG_USER, password=PG_PASSWORD)
    rows = await csv_process.execute(
        f"create table if not exists {name_dtb}({col_defs})"
    )
    await csv_process.close()
    print(f"✅ Created table {name_dtb} with columns: {columns}")




    # class_info = {}
    # for row in rows:
    #     mos_version = row[0]
    #     class_name = row[1]
    #     language = row[2]
    #     if class_info.get(mos_version , 0) == 0:
    #         class_info[mos_version] = {"classes": [{'class_name': class_name, "language": language}]}
    #     else:
    #         class_info[mos_version]["classes"].append({'class_name': class_name, "language": language})
    # return json.dumps(class_info, ensure_ascii=False, indent=0)