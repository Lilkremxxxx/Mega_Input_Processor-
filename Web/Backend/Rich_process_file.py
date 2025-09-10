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
from langchain_unstructured import UnstructuredLoader

# Tắt các log không cần thiết
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)



# Tắt các log không cần thiết
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)




load_dotenv()
PG_HOST=os.getenv("PG_HOST")
PG_DBNAME=os.getenv("PG_DBNAME")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")
OLLAMA_HOST=os.getenv("OLLAMA_HOST")

embeddings = OllamaEmbeddings(model = "bge-m3:latest",
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
            await docx_text_pdf_process(file_path, dt_base)

        elif ext in [".jpg", ".png"]:
            from PIL import Image
            img = Image.open(file_path)
            print(f"Processed image: {file_path}, size: {img.size}")
            
        else:
            print(f"File {file_path} uploaded but no specific processing defined.")
            # Có thể thêm xử lý chung cho text files, etc.


async def xlsx_process_rich(file_path, dt_base):
    """Xử lý file xlsx cho RichInfo - tạo bảng dữ liệu 
    và embedding để lưu vào vector store"""
    start_time = datetime.now()
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    embed_name = base_name + "_embeddings"
    conn = await asyncpg.connect(host=PG_HOST, database=dt_base, user=PG_USER, password=PG_PASSWORD)

    await conn.execute(f'DROP TABLE IF EXISTS "{embed_name}";')
    await conn.execute(f'CREATE TABLE "{embed_name}" (id SERIAL PRIMARY KEY, question TEXT, answer TEXT, note TEXT, vector_embedded TEXT);')

    # Tắt thông báo console cho Ollama
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
    
    
                
async def docx_text_pdf_process(file_path, dt_base):
    '''Tách doc thành các chunk text nhỏ, sau đó embedding và lưu 
    vào bảng bao gồm cả text gốc và vector  '''
    start_time = datetime.now()

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    embed_name = base_name + "_embeddings"
    conn = await asyncpg.connect(host=PG_HOST, database=dt_base, user=PG_USER, password=PG_PASSWORD)

    print(f"Đang tạo bảng {embed_name}")
    await conn.execute(f'DROP TABLE IF EXISTS "{embed_name}";')
    await conn.execute(f'CREATE TABLE "{embed_name}" (id SERIAL PRIMARY KEY, Original_Text TEXT, vector_embedded TEXT);')

    print(f"Đang đọc tài liệu")
    # Tắt thông báo console cho Ollama
    original_level = logging.getLogger().getEffectiveLevel()
    logging.getLogger().setLevel(logging.WARNING)
    
    loader = UnstructuredLoader(
    file_path=file_path, mode="elements", strategy="fast",
)
    
    print(f"Đang tách và embedding")
    docs = loader.load()
    embedding_list = []    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=120,
    )
    texts = text_splitter.split_documents(docs)
    Original = []
    async for doc in loader.alazy_load():
        lines = doc.page_content
        Original.append(lines)

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

        await conn.execute(f"INSERT INTO \"{embed_name}\" (Original_Text, vector_embedded) VALUES ($1, $2)", 
                    text, text_embedded)
    print(f"✅ Created table {embed_name} and embedded {len(Original)} rows.")

    end_time = datetime.now()
    duration = end_time - start_time
    print("Thời gian xử lý:", duration.total_seconds())

    # Khôi phục level log
    logging.getLogger().setLevel(original_level)
    await conn.close()
