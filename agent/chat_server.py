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
        result = await run_task(request.message)

        # Determine view change based on message content and agent response
        view_change = None
        msg_lower = request.message.lower()
        result_lower = result.lower()

        # Check agent response for explicit view mentions
        if "view:" in result_lower:
            view_parts = result_lower.split("view:")
            if len(view_parts) > 1:
                view_change = view_parts[1].split()[0].strip()
        
        # Fallback to message-based view detection
        if not view_change:
            if "workflow" in msg_lower or ("onboard" in msg_lower or "escalation" in msg_lower or any(word in msg_lower for word in ["run", "execute"]) and any(word in msg_lower for word in ["workflow", "process"])):
                view_change = "workflow"
            elif "triage" in msg_lower or ("ticket" in msg_lower and any(word in msg_lower for word in ["show", "view", "display"])):
                view_change = "triage"
            elif "analytics" in msg_lower or "report" in msg_lower or "stats" in msg_lower:
                view_change = "analytics"
            elif "dashboard" in msg_lower or "summary" in msg_lower or "overview" in msg_lower:
                view_change = "dashboard"
            elif "customer" in msg_lower and any(word in msg_lower for word in ["list", "show", "browse"]):
                view_change = "customer-list"
            elif "timeline" in msg_lower:
                view_change = "timeline"
            elif "calendar" in msg_lower:
                view_change = "calendar"

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
