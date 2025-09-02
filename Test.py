from langchain_community.document_loaders import CSVLoader
import os
from dotenv import load_dotenv
import pandas as ps
import asyncio

load_dotenv()
PG_HOST=os.getenv("PG_HOST")
PG_DBNAME=os.getenv("PG_DBNAME")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")
OLLAMA_HOST=os.getenv("OLLAMA_HOST")

loader = CSVLoader(file_path='DIM_DATE.csv')
docs = await loader.aload()
print(docs[0].page_content[:100])
print(docs[0].metadata)