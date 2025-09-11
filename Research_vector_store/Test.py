from pymilvus import MilvusClient
from pymilvus import model
from pymilvus import connections
from dotenv import load_dotenv
import os
import asyncio
import asyncpg
import pandas as pd



MILVUS_IP = "172.28.242.161"
MILVUS_PORT = "19530"
load_dotenv()
PG_HOST=os.getenv("PG_HOST")
PG_DBNAME="postgres"
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")
OLLAMA_HOST=os.getenv("OLLAMA_HOST")

connections.connect("default", host=MILVUS_IP, port=MILVUS_PORT)
print(f"✅ Connected to Milvus at {MILVUS_IP}:{MILVUS_PORT}!")

async def test():
    conn = await asyncpg.connect(
        host=PG_HOST, database=PG_DBNAME, user=PG_USER, password=PG_PASSWORD
    )

    await conn.execute(f'DROP TABLE IF EXISTS Test_embedding;')
    await conn.execute(f"""
        CREATE TABLE Test_embedding (
            id SERIAL PRIMARY KEY,
            question TEXT,
            answer TEXT,
            vector_embedded TEXT,
            collection_name TEXT
        );
    """)
    print("✅ Connected to PostgreSQL and created table Test_embedding")

    client = MilvusClient(alias="default")

    # Tạo và chèn dữ liệu vào nhiều collection
    collections = ["demo_collection", "example_collection"]
    embedding_fn = model.DefaultEmbeddingFunction()

    for collection_name in collections:
        if client.has_collection(collection_name=collection_name):
            client.drop_collection(collection_name=collection_name)

        client.create_collection(
            collection_name=collection_name,
            dimension=768,  # The vectors we will use in this demo has 768 dimensions
            vector_field="vector",  # Specify the vector field
            other_fields={"text": "str", "answer": "str", "subject": "str"},
        )

        # Input đầu vào

        #docs[]: là input để đánh embedding
        docs = [
            "where are you from ?.",
            "what are you doing for living ?.",
            "Do you love me ?.",
        ]

        #ans[]: là output của ans không đánh embedding mà sẽ cho vào data
        ans = [
            "I am from Vietnam.",
            "I am a internship without salary.",
            "Yes, I love you too.",
        ]

        # Tạo vector embeddings cho docs
        vectors = embedding_fn.encode_documents(docs)


        # Data này sẽ là 1 list làm dữ liệu cho collection( bao gồm cả vector_embedded và các trường khác)
        data = [
            {"id": i, "vector": vectors[i], "text": docs[i], "answer": ans[i], "subject": "history"}
            for i in range(len(vectors))
        ]

        # Insert data vào  Milvus
        client.insert(collection_name=collection_name, data=data)

        # Insert data vào PostgreSQL
        for i in range(len(docs)):
            question_embedded = str(vectors[i])
            question = docs[i]
            answer = ans[i]
            await conn.execute(
                f"INSERT INTO Test_embedding (question, answer, vector_embedded, collection_name) VALUES ($1, $2, $3, $4)",
                question, answer, question_embedded, collection_name
            )
        print(f"✅ Inserted {len(docs)} rows into PostgreSQL for collection {collection_name}")

    # Tìm kiếm dữ liệu từ tất cả các collection
    query_vectors = embedding_fn.encode_queries(["What is your salary ?"])

    # Lấy danh sách collection từ PostgreSQL
    rows = await conn.fetch("SELECT DISTINCT collection_name FROM Test_embedding;")
    collection_names = [row["collection_name"] for row in rows]

    for collection_name in collection_names:
        res = client.search(
            collection_name=collection_name,  # Tên của collection cần query
            data=query_vectors,  # query vectors
            limit=2,  # Số lượng output đầu ra,
            vector_field="vector",
            output_fields=["answer", "subject"],  # Custom ở đoạn này, muốn lấy trường nào thì thêm vào phần này( lưu ý phải được khái báo biến Data)
        )

        # Lấy giá trị của answer trong kết quả đầu tiên
        if res and res[0]:
            output = res[0][0]['entity']['answer']
            print(f"Output from collection {collection_name}: {output}")

asyncio.run(test())

