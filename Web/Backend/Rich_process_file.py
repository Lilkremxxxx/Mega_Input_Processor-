import os
import asyncio
import logging
import time
import pandas as pd
import asyncpg
import ollama
from datetime import datetime
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import CharacterTextSplitter

# Tắt các log không cần thiết
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

load_dotenv()
PG_HOST=os.getenv("PG_HOST")
PG_PORT=os.getenv("PG_PORT")
PG_DBNAME=os.getenv("PG_DBNAME")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")
OLLAMA_HOST=os.getenv("OLLAMA_HOST")

embeddings = OllamaEmbeddings(model = "bge-m3:latest",
                              base_url = OLLAMA_HOST)

async def process_uploaded_files(file_paths, groupId):
    """
    Hàm xử lý các file đã upload.
    Tham số: list các đường dẫn file.
    """
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".xlsx":
            await xlsx_process_rich(file_path, groupId)

        elif ext == '.docx' or ext == '.txt' or ext == '.pdf':
            await docx_text_pdf_process(file_path, groupId)

        elif ext in [".jpg", ".png"]:
            from PIL import Image
            img = Image.open(file_path)
            print(f"Processed image: {file_path}, size: {img.size}")
            
        else:
            print(f"File {file_path} uploaded but no specific processing defined.")


async def xlsx_process_rich(file_path, groupId):
    """Xử lý file xlsx cho RichInfo - tạo bảng dữ liệu 
    và embedding để lưu vào vector store"""
    start_time = datetime.now()
    
    #base_name = os.path.splitext(os.path.basename(file_path))[0]
    embed_name = groupId + "rag_qa"
    conn = await asyncpg.connect(
        host=PG_HOST, 
        port=int(PG_PORT),
        database="Richinfo_dtb", 
        user=PG_USER, 
        password=PG_PASSWORD
    )
    await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    await conn.execute(f'DROP TABLE IF EXISTS "{embed_name}";')
    await conn.execute(f'CREATE TABLE "{embed_name}" (id SERIAL PRIMARY KEY, question TEXT, answer TEXT, note TEXT, vector_embedded VECTOR);')
    original_level = logging.getLogger().getEffectiveLevel()
    logging.getLogger().setLevel(logging.WARNING)

    excel = pd.read_excel(file_path)
    questions = list(excel["question"])
    answers = list(excel["answer"])
    notes = list(excel["note"])
    embedding_list = []
    print("Embedding...")

    for question in questions:
        if pd.isna(question):
            vector = str(embeddings.embed_query(""))
        else:
            vector = str(embeddings.embed_query(str(question)))
        embedding_list.append(vector)

    print("Storing vectors...")
    for i in range(len(embedding_list)):
        question_embedded = embedding_list[i]
        question = str(questions[i]) if not pd.isna(questions[i]) else ""
        answer = str(answers[i]) if not pd.isna(answers[i]) else ""
        note = str(notes[i]) if not pd.isna(notes[i]) else None
        await conn.execute(f"INSERT INTO \"{embed_name}\" (question, answer, note, vector_embedded) VALUES ($1, $2, $3, $4)", 
                    question, answer, note, question_embedded)
    print(f"✅ Created table {embed_name} and embedded {len(questions)} rows.")

    end_time = datetime.now()
    duration = end_time - start_time
    print("Thời gian xử lý:", duration.total_seconds())
    # Khôi phục level log
    logging.getLogger().setLevel(original_level)
    await conn.close()
    
    
                
async def docx_text_pdf_process(file_path, groupId):
    '''Tách doc thành các chunk text nhỏ, sau đó embedding và lưu 
    vào bảng bao gồm cả text gốc và vector  '''
    start_time = datetime.now()

    #base_name = os.path.splitext(os.path.basename(file_path))[0]
    embed_name = groupId + "rag_qa"
    conn = await asyncpg.connect(
        host=PG_HOST, 
        port=int(PG_PORT),
        database="Richinfo_dtb", 
        user=PG_USER, 
        password=PG_PASSWORD
    )
    await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    print(f"Đang tạo bảng {embed_name}")
    await conn.execute(f'CREATE TABLE IF NOT EXISTS "{embed_name}" (id SERIAL PRIMARY KEY, question TEXT, answer TEXT, note TEXT, vector_embedded VECTOR); ')
    #await conn.execute(f'DROP TABLE IF EXISTS "{embed_name}";')
    #await conn.execute(f'CREATE TABLE "{embed_name}" (id SERIAL PRIMARY KEY, Original_Text TEXT, vector_embedded VECTOR);')

    print(f"Đang đọc tài liệu")
    original_level = logging.getLogger().getEffectiveLevel()
    logging.getLogger().setLevel(logging.WARNING)
    
    # Chọn loader phù hợp với từng loại file
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        loader = PyPDFLoader(file_path)
    elif ext == '.docx':
        loader = Docx2txtLoader(file_path)
    elif ext == '.txt':
        # Đọc file text thông thường
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        from langchain_core.documents import Document
        docs = [Document(page_content=content)]
        loader = None
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    print(f"Đang tách và embedding")
    
    if loader:
        docs = loader.load()
    
    text_splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=150,
    )
    texts = text_splitter.split_documents(docs)
    
    # Lấy text gốc từ các chunks
    Original = [doc.page_content for doc in texts]

    embedding_list = []
    for org in Original:
        if pd.isna(org):
            vector = str(embeddings.embed_query(""))
        else:
            vector = str(embeddings.embed_query(org))
        embedding_list.append(vector)

    print("Storing vectors...")
    for i in range(len(embedding_list)):
        text_embedded = embedding_list[i]
        text = str(Original[i]) if not pd.isna(Original[i]) else ""

        await conn.execute(f"INSERT INTO \"{embed_name}\" (question, answer, note, vector_embedded) VALUES ($1, $2, $3, $4)", 
                    text, text,text, text_embedded)
    print(f"✅ Created table {embed_name} and embedded {len(Original)} rows.")

    end_time = datetime.now()
    duration = end_time - start_time
    print("Thời gian xử lý:", duration.total_seconds())
    logging.getLogger().setLevel(original_level)
    await conn.close()
