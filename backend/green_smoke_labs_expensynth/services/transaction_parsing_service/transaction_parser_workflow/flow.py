import os

import yaml
from crewai.agent import Agent
from crewai.flow.flow import Flow, listen, router, start
from crewai.llm import LLM
from crewai_tools import MCPServerAdapter

from green_smoke_labs_expensynth.utils.types import TransactionCategory, TransactionType

from .types import ParsedTransactionData


class TransactionParserWorkflow(Flow):
    @start()
    async def initialize_workflow(self):
        self.llm = LLM(
            model=os.getenv("TRANSACTION_PARSER_LLM_MODEL"),
            api_key=os.getenv("TRANSACTION_PARSER_LLM_API_KEY"),
            base_url=os.getenv("TRANSACTION_PARSER_LLM_BASE_URL"),
            temperature=os.getenv("TRANSACTION_PARSER_LLM_TEMPERATURE"),
        )
        agents_config_path = os.path.join(
            os.path.dirname(__file__),
            "config",
            "agents.yaml",
        )
        self.agents_config = yaml.safe_load(open(agents_config_path))

    @listen(initialize_workflow)
    async def parse_transaction(self) -> dict:
        mcp_adapter = None
        try:
            mcp_server_params = {
                "url": os.getenv("WEB_SEARCH_MCP_SERVER_URL"),
            }
            mcp_adapter = MCPServerAdapter(mcp_server_params)
            tools = mcp_adapter.tools

            transaction_message = self.state.get("transaction_message", None)
            if not transaction_message:
                raise ValueError("Transaction message is not sent")

            financial_analyst_agent = Agent(
                role=self.agents_config["financial_analyst"]["role"],
                goal=self.agents_config["financial_analyst"]["goal"],
                backstory=self.agents_config["financial_analyst"]["backstory"],
                llm=self.llm,
                tools=[tools[1]],
            )

            user_msg = f"""
            # Transaction Types: {TransactionType.get_all()}
            # Transaction Categories: {TransactionCategory.get_all()}
            # Tavily API Key: {os.getenv("TAVILY_API_KEY")}
            # Transaction Message
            {transaction_message}
            """
            while True:
                try:
                    parsed_transaction_data = (
                        await financial_analyst_agent.kickoff_async(
                            user_msg,
                            response_format=ParsedTransactionData,
                        )
                    )
                    r = parsed_transaction_data.pydantic
                    if not r or r is None:
                        continue
                    break
                except Exception as e:
                    continue
            return {
                "success": True,
                "message": "Transaction parsed successfully",
                "data": parsed_transaction_data.pydantic,
            }
        except Exception as e:
            raise e
        finally:
            if mcp_adapter:
                mcp_adapter.stop()
