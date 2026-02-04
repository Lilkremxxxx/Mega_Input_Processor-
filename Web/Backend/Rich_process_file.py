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
from Web.Backend.pgconpool import get_db, _pool


# Tắt các log không cần thiết
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



async def process_uploaded_files(file_info_list, username):
    """
    Hàm xử lý các file đã upload.
    Tham số: list các dict chứa {'path': file_path, 'name': filename}.
    """
    for file_info in file_info_list:
        file_path = file_info['path']
        filename = file_info['name']
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".xlsx":
            await xlsx_process_rich(file_path, username, filename)

        elif ext == '.docx' or ext == '.txt' or ext == '.pdf':
            await docx_text_pdf_process(file_path, username, filename)

        elif ext in [".jpg", ".png"]:
            from PIL import Image
            img = Image.open(file_path)
            print(f"Processed image: {file_path}, size: {img.size}")
            
        else:
            print(f"File {file_path} uploaded but no specific processing defined.")


async def xlsx_process_rich(file_path, username, filename):
    """Xử lý file xlsx cho RichInfo - tạo bảng dữ liệu 
    và embedding để lưu vào vector store"""
    start_time = datetime.now()
    embed_name = filename + "_richinfo"

    #Lấy conn từ pool
    async for conn in get_db():
        try:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
            await conn.execute(f'CREATE TABLE IF NOT EXISTS "{embed_name}" (id SERIAL PRIMARY KEY, question TEXT, answer TEXT, note TEXT, vector_embedded VECTOR); ')
            original_level = logging.getLogger().getEffectiveLevel()
            logging.getLogger().setLevel(logging.WARNING)

            excel = pd.read_excel(file_path)
            questions = list(excel["question"])
            answers = list(excel["answer"])
            notes = list(excel["note"])
            embedding_list = []
            print("Embedding...")

            for i, question in enumerate(questions):
                try:
                    if pd.isna(question):
                        vector = await asyncio.to_thread(embeddings.embed_query, "")
                    else:
                        vector = await asyncio.to_thread(embeddings.embed_query, str(question))
                    embedding_list.append(str(vector))
                    if (i + 1) % 10 == 0:
                        print(f"Embedded {i + 1}/{len(questions)} questions...")
                except Exception as e:
                    print(f"❌ Error embedding question {i}: {e}")
                    raise

            print("Storing vectors...")
            for i in range(len(embedding_list)):
                question_embedded = embedding_list[i]
                question = str(questions[i]) if not pd.isna(questions[i]) else ""
                answer = str(answers[i]) if not pd.isna(answers[i]) else ""
                note = str(notes[i]) if not pd.isna(notes[i]) else None
                await conn.execute(f"INSERT INTO \"{embed_name}\" (question, answer, note, vector_embedded) VALUES ($1, $2, $3, $4)", 
                            question, answer, note, question_embedded)
            
            # Insert vào bảng Manager
            await conn.execute(
                'INSERT INTO "Manager" ("username", "fileName", "documentType", "tableName") VALUES ($1, $2, $3, $4)',
                username, filename, 'richinfo', embed_name
            )
            
            print(f"✅ Created table {embed_name} and embedded {len(questions)} rows.")

            end_time = datetime.now()
            duration = end_time - start_time
            print("Thời gian xử lý:", duration.total_seconds())
            # Khôi phục level log
            logging.getLogger().setLevel(original_level)
        finally:
            pass
    
    
                
def clean_text(text):
    """Clean và normalize text trước khi xử lý"""
    if not text or not text.strip():
        return ""
    text = ' '.join(text.split())
    import re
    text = re.sub(r'\n+', '\n', text)
    text = text.strip()
    return text


async def load_pdf_content(file_path):
    """Load PDF với nhiều phương pháp fallback"""
    from langchain_core.documents import Document
    
    # Method 1: PyPDFLoader
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        total_chars = sum(len(doc.page_content) for doc in docs)
        
        if total_chars > 0:
            print(f"✓ PyPDFLoader: {len(docs)} pages, {total_chars} chars")
            return docs
    except Exception as e:
        print(f"PyPDFLoader failed: {e}")
    
    # Method 2: pymupdf
    try:
        import fitz
        pdf_doc = fitz.open(file_path)
        docs = []
        
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            text = page.get_text("text")  # Explicitly use text mode
            
            if text.strip():
                docs.append(Document(page_content=text, metadata={"page": page_num}))
        
        pdf_doc.close()
        
        if docs:
            total_chars = sum(len(doc.page_content) for doc in docs)
            print(f"✓ pymupdf: {len(docs)} pages, {total_chars} chars")
            return docs
    except Exception as e:
        print(f"pymupdf failed: {e}")
    
    # Method 3: pdfplumber
    try:
        import pdfplumber
        docs = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                
                if text and text.strip():
                    docs.append(Document(page_content=text, metadata={"page": page_num}))
        
        if docs:
            total_chars = sum(len(doc.page_content) for doc in docs)
            print(f"✓ pdfplumber: {len(docs)} pages, {total_chars} chars")
            return docs
    except ImportError:
        print("pdfplumber not installed (optional)")
    except Exception as e:
        print(f"pdfplumber failed: {e}")
    
    print("❌ All PDF extraction methods failed")
    return []


async def docx_text_pdf_process(file_path, username, filename):
    """Xử lý file document: tách thành chunks, embedding và lưu vào database"""
    start_time = datetime.now()
    embed_name = f"{filename}_richinfo"
    async for conn in get_db():
        try:
            
            await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
            await conn.execute(
                f'CREATE TABLE IF NOT EXISTS "{embed_name}" '
                f'(id SERIAL PRIMARY KEY, question TEXT, answer TEXT, note TEXT, vector_embedded VECTOR);'
            )
            
            print(f"Đang đọc tài liệu: {filename}")
            original_level = logging.getLogger().getEffectiveLevel()
            
            # Load document theo loại file
            from langchain_core.documents import Document

            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.pdf':
                docs = await load_pdf_content(file_path)
            elif ext == '.docx':
                loader = Docx2txtLoader(file_path)
                docs = loader.load()
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                docs = [Document(page_content=content)]
            else:
                raise ValueError(f"Unsupported file type: {ext}")
            
            if not docs:
                print("⚠️ Không thể đọc được nội dung từ file!")
                await conn.close()
                return
            
            # Clean text trong tất cả documents
            for doc in docs:
                doc.page_content = clean_text(doc.page_content)
            
            # Loại bỏ documents rỗng sau khi clean
            docs = [doc for doc in docs if doc.page_content]
            
            total_chars = sum(len(doc.page_content) for doc in docs)
            print(f"Đã load {len(docs)} documents, {total_chars} ký tự")
            
            if total_chars == 0:
                print("⚠️ Documents rỗng sau khi clean!")
                await conn.close()
                return
            
            # Tách thành chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=150,
                separators=["\n\n", "\n", ". ", " ", ""],
                length_function=len
            )
            chunks = text_splitter.split_documents(docs)
            
            # Fallback: nếu không tách được, dùng documents gốc
            if not chunks:
                print("Không tách được chunks, sử dụng documents gốc")
                chunks = docs
            
            # Clean và filter chunks
            chunk_texts = []
            for chunk in chunks:
                cleaned = clean_text(chunk.page_content)
                if cleaned and len(cleaned) > 10:  # Chỉ lấy chunks có ít nhất 10 ký tự
                    chunk_texts.append(cleaned)
            
            print(f"Đã tách thành {len(chunk_texts)} chunks")
            
            if not chunk_texts:
                print("⚠️ Không có chunks hợp lệ sau khi xử lý!")
                await conn.close()
                return
            
            # Embedding từng chunk
            print("Đang embedding...")
            embedding_list = []
            for i, text in enumerate(chunk_texts):
                try:
                    vector = await asyncio.to_thread(embeddings.embed_query, text)
                    embedding_list.append(str(vector))
                    
                    if (i + 1) % 10 == 0:
                        print(f"  {i + 1}/{len(chunk_texts)} chunks")
                except Exception as e:
                    print(f"❌ Error embedding chunk {i}: {e}")
                    raise
            
            # Lưu vào database
            print("Đang lưu vào database...")
            db_user_name = await asyncpg.connect(
                host=PG_HOST,
                port=int(PG_PORT),
                database=username,
                user=PG_USER,
                password=PG_PASSWORD
            )
            for i, (text, vector) in enumerate(zip(chunk_texts, embedding_list)):
                await db_user_name.execute(
                    f'INSERT INTO "{embed_name}" (question, answer, note, vector_embedded) '
                    f'VALUES ($1, $2, $3, $4)',
                    text, text, "", vector
                )
            
            await conn.execute(
                'INSERT INTO "Manager" ("username", "fileName", "documentType", "tableName") '
                'VALUES ($1, $2, $3, $4)',
                username, filename, 'richinfo', embed_name
            )
            await conn.close()
            
            duration = (datetime.now() - start_time).total_seconds()
            print(f"✅ Hoàn thành: {len(chunk_texts)} chunks trong {duration:.2f}s")
            
            logging.getLogger().setLevel(original_level)
            
        finally:
            await conn.close()
