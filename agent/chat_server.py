# ABOUTME: Simple chat-based agent server
# ABOUTME: Handles chat messages and executes tasks using OpenAI function calling
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.crew import run_task

app = FastAPI(title="AgentChat", version="1.0.0")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    view_change: Optional[str] = None


@app.post("/process")
async def process_message(request: ChatRequest) -> ChatResponse:
    """Process a chat message and execute the corresponding task."""
    try:
        # Run the task using the agent
        result = run_task(request.message)

        # Determine view change based on the message content
        view_change = None
        msg_lower = request.message.lower()

        if "triage" in msg_lower or ("acme" in msg_lower and "ticket" in msg_lower):
            view_change = "triage"
        elif "customer" in msg_lower and "list" in msg_lower:
            view_change = "customer-list"
        elif "detail" in msg_lower:
            view_change = "customer-detail"

        return ChatResponse(response=result, view_change=view_change)

    except Exception as e:
        return ChatResponse(
            response=f"Sorry, I encountered an error: {str(e)}", view_change=None
        )


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
