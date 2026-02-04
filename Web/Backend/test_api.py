import requests
from dotenv import load_dotenv
import os
from langchain_ollama import OllamaEmbeddings

load_dotenv()
PG_HOST=os.getenv("PG_HOST")
PG_PORT=os.getenv("PG_PORT")
PG_DBNAME=os.getenv("PG_DBNAME")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")
OLLAMA_HOST=os.getenv("OLLAMA_HOST")

# Test kết nối Ollama
try:
    response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=10)
    print(f"✅ Ollama connection OK: {response.status_code}")
    print(f"Available models: {response.json()}")
except Exception as e:
    print(f"❌ Cannot connect to Ollama: {e}")

embeddings = OllamaEmbeddings(
    model="bge-m3:latest",
    base_url=OLLAMA_HOST
)

# Test embedding
try:
    test_vector = embeddings.embed_query("test")
    print(f"✅ Embedding works! Vector dimension: {len(test_vector)}")
except Exception as e:
    print(f"❌ Embedding failed: {e}")