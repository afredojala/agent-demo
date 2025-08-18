# ABOUTME: Tool functions for the agent system
# ABOUTME: HTTP clients for API calls and WebSocket intent emitter for UI control
import httpx
import json
import websockets
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
AGENT_WS = os.getenv("AGENT_WS", "ws://localhost:8765")


def search_customers(name: str):
    with httpx.Client() as client:
        response = client.get(
            f"{API_BASE}/customers", params={"name": name}, timeout=10
        )
        response.raise_for_status()
        return response.json()


def list_tickets(customer_id: str, status: str = "open"):
    with httpx.Client() as client:
        response = client.get(
            f"{API_BASE}/tickets",
            params={"customer_id": customer_id, "status": status},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()


def create_note(ticket_id: str, body: str):
    with httpx.Client() as client:
        response = client.post(
            f"{API_BASE}/notes", json={"ticket_id": ticket_id, "body": body}, timeout=10
        )
        if response.status_code >= 400:
            raise RuntimeError(response.json())
        return response.json()


def send_email(to: str, subject: str, body: str):
    with httpx.Client() as client:
        response = client.post(
            f"{API_BASE}/emails",
            json={"to": to, "subject": subject, "body": body},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()


async def emit_intent(intent: dict):
    try:
        async with websockets.connect(AGENT_WS) as ws:
            await ws.send(json.dumps(intent))
            return {"status": "sent", "intent": intent}
    except Exception as e:
        return {"status": "error", "message": str(e)}
