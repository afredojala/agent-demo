# ABOUTME: FastAPI backend for the mini-CRM system
# ABOUTME: Provides REST API endpoints for customers, tickets, notes, and emails
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3
import os
import httpx

app = FastAPI(title="MiniCRM", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.getenv("DB_PATH", "backend/db.sqlite3")
AGENT_API_BASE = os.getenv("AGENT_API_BASE", "http://localhost:8001")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class Customer(BaseModel):
    id: str
    name: str
    email: Optional[str] = None


class Ticket(BaseModel):
    id: str
    customer_id: str
    title: str
    status: str = Field(pattern="^(open|closed)$")
    created_at: str


class NoteIn(BaseModel):
    ticket_id: str
    body: str


class Note(BaseModel):
    id: str
    ticket_id: str
    body: str
    created_at: str


class EmailIn(BaseModel):
    to: str
    subject: str
    body: str


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    view_change: Optional[str] = None


def rows(conn, q, args=()):
    cur = conn.execute(q, args)
    return [dict(r) for r in cur.fetchall()]


@app.get("/customers", response_model=List[Customer])
def list_customers(name: Optional[str] = None):
    conn = db()
    if name:
        return rows(
            conn,
            "SELECT * FROM customers WHERE name LIKE ? ORDER BY name",
            (f"%{name}%",),
        )
    return rows(conn, "SELECT * FROM customers ORDER BY name")


@app.get("/tickets", response_model=List[Ticket])
def list_tickets(customer_id: str, status: Optional[str] = None):
    conn = db()
    if status:
        return rows(
            conn,
            "SELECT * FROM tickets WHERE customer_id=? AND status=? ORDER BY created_at",
            (customer_id, status),
        )
    return rows(
        conn,
        "SELECT * FROM tickets WHERE customer_id=? ORDER BY created_at",
        (customer_id,),
    )


@app.post("/notes", response_model=Note)
def create_note(note: NoteIn):
    if not note.ticket_id:
        raise HTTPException(
            status_code=400,
            detail={"error_code": "MISSING_FIELD", "message": "ticket_id required"},
        )
    conn = db()
    cur = conn.execute(
        "INSERT INTO notes(ticket_id, body, created_at) VALUES(?,?,strftime('%Y-%m-%dT%H:%M:%SZ','now'))",
        (note.ticket_id, note.body),
    )
    conn.commit()
    nid = cur.lastrowid
    (row,) = rows(
        conn, "SELECT id,ticket_id,body,created_at FROM notes WHERE id=?", (nid,)
    )
    row["id"] = str(row["id"])
    return row


@app.post("/emails")
def send_email(payload: EmailIn):
    return {"status": "sent", "to": payload.to, "subject": payload.subject}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    try:
        # Forward the message to the agent
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AGENT_API_BASE}/process",
                json={"message": message.message},
                timeout=30,
            )
            if response.status_code == 200:
                agent_response = response.json()
                return ChatResponse(
                    response=agent_response.get("response", "Task completed"),
                    view_change=agent_response.get("view_change"),
                )
            else:
                raise HTTPException(status_code=500, detail="Agent request failed")

    except httpx.RequestError:
        # Fallback response when agent is not available
        view_change = None
        response_text = "Agent is not available right now."

        # Simple keyword-based responses for demo purposes
        msg_lower = message.message.lower()
        if "acme" in msg_lower and ("ticket" in msg_lower or "show" in msg_lower):
            view_change = "triage"
            response_text = "Showing Acme Corp's open tickets in triage view."
        elif "note" in msg_lower:
            response_text = (
                "I would add a note to the ticket, but the agent is offline."
            )
        elif "email" in msg_lower:
            response_text = (
                "I would send you an email summary, but the agent is offline."
            )

        return ChatResponse(response=response_text, view_change=view_change)


@app.get("/healthz")
def healthz():
    return {"ok": True}
