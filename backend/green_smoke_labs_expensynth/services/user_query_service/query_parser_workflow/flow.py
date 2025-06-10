import os
from typing import Optional

import yaml
from crewai.agent import Agent
from crewai.flow.flow import Flow, listen, router, start
from crewai.llm import LLM
from crewai.tools import BaseTool
from qdrant_client import QdrantClient

from green_smoke_labs_expensynth.utils.embeddings import TextFormatter

text_formatter = TextFormatter()


class QdrantSearchTool(BaseTool):
    qdrant_client: Optional[QdrantClient] = None
    text_formatter: Optional[TextFormatter] = None

    def __init__(self, qdrant_client, text_formatter):
        super().__init__(
            name="qdrant_search",
            description=(
                "Searches the user's transaction history in Qdrant and returns relevant transactions. "
                "Use this tool if the user query requires access to user-specific transaction data. "
                "Input should be the user query string."
            ),
        )
        self.qdrant_client = qdrant_client
        self.text_formatter = text_formatter

    def _run(self, query: str):
        search_results = self.qdrant_client.search(
            collection_name="expensynth_transactions",
            query_vector=self.text_formatter._get_embeddings(query),
            limit=10,
        )
        transactions = [hit.payload for hit in search_results]
        return str(transactions)


class FinancialAssistantWorkflow(Flow):
    @start()
    async def initialize_workflow(self):
        model = os.getenv("TRANSACTION_PARSER_LLM_MODEL")
        api_key = os.getenv("TRANSACTION_PARSER_LLM_API_KEY")
        base_url = os.getenv("TRANSACTION_PARSER_LLM_BASE_URL")
        temp_str = os.getenv("TRANSACTION_PARSER_LLM_TEMPERATURE")
        temperature = float(temp_str) if temp_str is not None else 0.7
        if not model:
            raise ValueError(
                "TRANSACTION_PARSER_LLM_MODEL environment variable is not set"
            )
        self.llm = LLM(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
        )
        agents_config_path = os.path.join(
            os.path.dirname(__file__),
            "config",
            "agents.yaml",
        )
        self.agents_config = yaml.safe_load(open(agents_config_path))
        self.qdrant_client_url = "https://9384a587-1ea8-44cf-a559-4205cc83e00c.us-west-2-0.aws.cloud.qdrant.io:6333"

        self.qdrant_client = QdrantClient(
            url=self.qdrant_client_url,
            api_key=os.environ.get("QDRANT_API_KEY"),
        )

    @listen(initialize_workflow)
    async def answer_user_query(self) -> dict:
        user_query = self.state.get("user_query", None)
        if not user_query:
            raise ValueError("User query is not provided")

        qdrant_tool = QdrantSearchTool(self.qdrant_client, text_formatter)

        financial_assistant_agent = Agent(
            role=self.agents_config["financial_assistant"]["role"],
            goal=self.agents_config["financial_assistant"]["goal"],
            backstory=self.agents_config["financial_assistant"]["backstory"],
            llm=self.llm,
            tools=[qdrant_tool],
        )

        prompt = f"User query: {user_query}"
        response = await financial_assistant_agent.kickoff_async(prompt)

        return {
            "success": True,
            "message": "Query answered",
            "data": response,
        }
