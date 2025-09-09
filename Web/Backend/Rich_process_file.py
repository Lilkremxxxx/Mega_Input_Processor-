import os
import asyncio
import pandas as pd
from langchain_community.document_loaders import CSVLoader
from langchain_unstructured import UnstructuredLoader
from dotenv import load_dotenv
from os import getenv
import asyncpg
from langchain_ollama import OllamaEmbeddings


load_dotenv()
PG_HOST=os.getenv("PG_HOST")
PG_DBNAME=os.getenv("PG_DBNAME")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")
OLLAMA_HOST=os.getenv("OLLAMA_HOST")

embedding = OllamaEmbeddings(model = "bge-m3:latest",
                              base_url = OLLAMA_HOST)

async def process_uploaded_files(file_paths, dt_base):
    """
    Hàm xử lý các file đã upload.
    Tham số: list các đường dẫn file.
    """
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".xlsx":
           await xlsx_process_rich(file_path, dt_base)

        elif ext == '.docx' or ext == '.txt' or ext == '.pdf':
            print('hello')
        

        elif ext in [".jpg", ".png"]:
            from PIL import Image
            img = Image.open(file_path)
            print(f"Processed image: {file_path}, size: {img.size}")
            
        else:
            print(f"File {file_path} uploaded but no specific processing defined.")
            # Có thể thêm xử lý chung cho text files, etc.


async def xlsx_process_rich(file_path, dt_base):
    """Xử lý file xlsx cho RichInfo - tạo bảng dữ liệu và embedding để lưu vào vector store"""
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    # Đọc tất cả sheet names
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    conn = await asyncpg.connect(host=PG_HOST, database=dt_base, user=PG_USER, password=PG_PASSWORD)
    # Xử lý từng sheet
    columns = df.columns.tolist()
    columns_def = ", ".join([f'"{col}" text' for col in columns])
    print(columns.lower())

        
        
            
    


            
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
