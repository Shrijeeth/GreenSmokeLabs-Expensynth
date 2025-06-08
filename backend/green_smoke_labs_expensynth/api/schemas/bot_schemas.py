from pydantic import BaseModel


class UserMessage(BaseModel):
    role: str = "user"
    content: str


class AssistantMessage(BaseModel):
    role: str = "assistant"
    content: str


class ChatHistory(BaseModel):
    messages: list[UserMessage | AssistantMessage]
