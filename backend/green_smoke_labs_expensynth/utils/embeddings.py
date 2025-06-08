import os
import uuid

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

from green_smoke_labs_expensynth.services.transaction_parsing_service.transaction_parser_workflow.types import (
    ParsedTransactionData,
)

# if not client.collection_exists("expensynth_transactions"):
#     client.create_collection(
#         collection_name="expensynth_transactions",
#         vectors_config=VectorParams(size=4096, distance=Distance.COSINE),
#     )


class TextFormatter:
    def __init__(self):
        self.nebius_url = "https://api.studio.nebius.com/v1/"
        self.embedding_model = "intfloat/e5-mistral-7b-instruct"
        
        self.qdrant_client_url = "https://9384a587-1ea8-44cf-a559-4205cc83e00c.us-west-2-0.aws.cloud.qdrant.io:6333"
        self.qdrant_collection_name = "expensynth_transactions"

        self.openai_client = OpenAI(
            base_url=self.nebius_url,
            api_key=os.environ.get("NEBIUS_API_KEY"),
        )

        self.qdrant_client = QdrantClient(
            url=self.qdrant_client_url,
            api_key=os.environ.get("QDRANT_API_KEY"),
        )
    
    def insert_into_vector_db(self, message: str, payload: ParsedTransactionData) -> bool:
        formatted_text = self._format_transaction_details(message, payload)
        print(f"Formatted text for embedding: {formatted_text}")
        try:
            embedding = self._get_embeddings(formatted_text)

            self.qdrant_client.upsert(
                collection_name=self.qdrant_collection_name,
                wait=True,
                points=[
                    PointStruct(id=str(uuid.uuid4()), vector=embedding, payload=payload.model_dump()),
                ]
            )

            return True
        except Exception as e:
            print(f"Error inserting into vector DB: {e}")
            return False

    def _format_transaction_details(self, message, payload: ParsedTransactionData) -> str:
        """
        Formats the transaction details text before embedding.
        """
        
        return f"""Transaction Details:
        Original transaction message: {message}
        Transaction Date: {payload.transaction_date}
        Transaction Amount: {payload.transaction_amount} AED.
        Card Number: {payload.card_number}
        Merchant Name: {payload.third_party_name},
        Merchant Type: {payload.transaction_category.value}, 
        Transaction Type (Debit/Credit): {payload.transaction_type.value}, 
        """
    # TODO:
    # --- Purpose: App Store Subscription Renewal.
    # --- Available balance: {available_balance} AED.

    def _get_embeddings(self, text: str) -> list[float]:
        response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )

        return response.data[0].embedding 