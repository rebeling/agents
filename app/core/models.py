from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.core.utils import name_to_pastel_hex


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    agent_name: str


class Message(BaseModel):
    content: str
    sender: str | None = None


class ChatMessage(BaseModel):
    """Format of messages sent to the browser."""

    type: str
    sender: str
    role: Literal["user", "model"]
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    color: str = Field(default_factory=lambda: "#e3f2fd")

    def __init__(self, **data):
        super().__init__(**data)
        self.color = name_to_pastel_hex(self.sender)
