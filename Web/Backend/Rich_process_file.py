from csv import excel
import os
import asyncio
import ollama
import pandas as pd
from langchain_community.document_loaders import CSVLoader
from langchain_unstructured import UnstructuredLoader
from dotenv import load_dotenv
from os import getenv
import asyncpg
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore



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

        elif ext == '.docx' or ext == '.txt' :
            await docx_text_process(file_path, dt_base)

        elif  ext == '.pdf':
            await pdf_process(file_path, dt_base)

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
    embed_name = base_name + "_embeddings"
    conn = await asyncpg.connect(host=PG_HOST, database=dt_base, user=PG_USER, password=PG_PASSWORD)

    await conn.execute(f'DROP TABLE IF EXISTS "{embed_name}";')
    await conn.execute(f'CREATE TABLE "{embed_name}" (id SERIAL PRIMARY KEY, question TEXT, answer TEXT, note TEXT, question_embedded TEXT);')

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
        await conn.execute(f"INSERT INTO \"{embed_name}\" (question, answer, note, question_embedded) VALUES ($1, $2, $3, $4)", 
                    question, answer, note, question_embedded)
    print(f"✅ Created table {embed_name} and embedded {len(questions)} rows.")
    await conn.close()
    
                
async def docx_text_process(file_path, dt_base):

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    conn = await asyncpg.connect(host=PG_HOST, database=dt_base, user=PG_USER, password=PG_PASSWORD)

    loader = UnstructuredLoader(
    file_path=file_path, mode="elements", strategy="fast",
)
    docs = loader.load()
    doccc = []
    for doc in docs:
        lines = doc.page_content
        doccc.append(lines)
    
    vectorstore = InMemoryVectorStore.from_texts(
    doccc,
    embedding=embeddings,)
    a = ollama.embed(
    model='bge-m3:latest',
    input=doccc,
    )
    b=[]
    for a1 in a:
        b.append(a1)
    print(b)



async def pdf_process(file_path, dt_base):
    conn = await asyncpg.connect(host=PG_HOST, database=dt_base, user=PG_USER, password=PG_PASSWORD)
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    loader = PyPDFLoader(file_path)
    pages = []
    async for doc in loader.alazy_load():
        lines = doc.page_content
        pages.append(lines)
    pages = [Text.replace("\n", "") for Text in pages]
    pages = [Text.replace("  ", " ") for Text in pages]
    print(pages)