import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from qdrant_client.models import Distance, VectorParams

load_dotenv()

client = QdrantClient(
    url="https://9384a587-1ea8-44cf-a559-4205cc83e00c.us-west-2-0.aws.cloud.qdrant.io:6333",
    api_key=os.environ.get("NEBIUS_API_KEY"),
)


client.create_collection(
    collection_name="expensynth_collection_test",
    vectors_config=VectorParams(size=100, distance=Distance.COSINE),
)
