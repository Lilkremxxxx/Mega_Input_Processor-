from pymilvus import MilvusClient
from pymilvus import model
from pymilvus import connections
from dotenv import load_dotenv
import os
import asyncio
import asyncpg


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
    con = await asyncpg.connect(
        host=PG_HOST, database=PG_DBNAME, user=PG_USER, password=PG_PASSWORD
    )
    print("kết nối thành công pg")

    client = MilvusClient(alias="default")
    if client.has_collection(collection_name="demo_collection"):
        client.drop_collection(collection_name="demo_collection")

    # Tạo collection với vector_field được chỉ định
    client.create_collection(
        collection_name="demo_collection",
        dimension=768,  # The vectors we will use in this demo has 768 dimensions
        vector_field="vector",  # Specify the vector field
        other_fields={"text": "str", "answer": "str", "subject": "str"},
    )

    embedding_fn = model.DefaultEmbeddingFunction()

    # Text strings to search from.
    docs = [
        "where are you from ?.",
        "what are you doing for living ?.",
        "Do you love me ?.",
    ]

    ans = [
        "I am from Vietnam.",
        "I am a internship without salary.",
        "Yes, I love you too.",
    ]

    vectors = embedding_fn.encode_documents(docs)

    data = [
        {"id": i, "vector": vectors[i], "text": docs[i], "answer": ans[i], "subject": "history"}
        for i in range(len(vectors))
    ]

    res = client.insert(collection_name="demo_collection", data=data)
    # print(vectors)


    # Tìm kiếm dữ liệu
    query_vectors = embedding_fn.encode_queries(["What is your salary ?"])

    res = client.search(
        collection_name="demo_collection",  # target collection
        data=query_vectors,  # query vectors
        limit=2,  # number of returned entities,
        vector_field="vector",
        output_fields=["answer", "subject"],  # specifies fields to be returned
        )
    # print("✅ Search results:", res)

    # Lấy giá trị của answer trong kết quả đầu tiên
    output = res[0][0]['entity']['answer']
    print("Output:", output)

asyncio.run(test())

