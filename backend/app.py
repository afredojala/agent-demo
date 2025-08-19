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


def init_workflow_tables():
    conn = db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS workflow_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT,
            started_at TEXT,
            finished_at TEXT,
            result TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS workflow_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER REFERENCES workflow_runs(id),
            name TEXT,
            status TEXT,
            started_at TEXT,
            finished_at TEXT,
            result TEXT
        )
        """
    )
    conn.commit()


init_workflow_tables()


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


class WorkflowStart(BaseModel):
    name: str


class WorkflowRun(BaseModel):
    id: int
    name: str
    status: str
    started_at: str
    finished_at: Optional[str] = None
    result: Optional[str] = None


class WorkflowStepIn(BaseModel):
    name: str
    status: str
    result: Optional[str] = None


class WorkflowStep(BaseModel):
    id: int
    run_id: int
    name: str
    status: str
    started_at: str
    finished_at: Optional[str] = None
    result: Optional[str] = None


def rows(conn, q, args=()):
    cur = conn.execute(q, args)
    return [dict(r) for r in cur.fetchall()]


@app.post("/workflows", response_model=WorkflowRun)
def start_workflow(payload: WorkflowStart):
    conn = db()
    cur = conn.execute(
        "INSERT INTO workflow_runs(name, status, started_at) VALUES(?, 'running', strftime('%Y-%m-%dT%H:%M:%SZ','now'))",
        (payload.name,),
    )
    conn.commit()
    run_id = cur.lastrowid
    (run,) = rows(conn, "SELECT * FROM workflow_runs WHERE id=?", (run_id,))
    return run


@app.post("/workflows/{run_id}/steps", response_model=WorkflowStep)
def add_workflow_step(run_id: int, step: WorkflowStepIn):
    conn = db()
    cur = conn.execute(
        "INSERT INTO workflow_steps(run_id, name, status, started_at, finished_at, result) VALUES(?,?,?,strftime('%Y-%m-%dT%H:%M:%SZ','now'), CASE WHEN ? IN ('completed','failed') THEN strftime('%Y-%m-%dT%H:%M:%SZ','now') END, ?)",
        (run_id, step.name, step.status, step.status, step.result),
    )
    if step.status in ("completed", "failed"):
        conn.execute(
            "UPDATE workflow_runs SET status=?, finished_at=strftime('%Y-%m-%dT%H:%M:%SZ','now'), result=? WHERE id=?",
            (step.status, step.result, run_id),
        )
    conn.commit()
    step_id = cur.lastrowid
    (row,) = rows(conn, "SELECT * FROM workflow_steps WHERE id=?", (step_id,))
    return row


@app.get("/workflows/{run_id}")
def get_workflow(run_id: int):
    conn = db()
    runs = rows(conn, "SELECT * FROM workflow_runs WHERE id=?", (run_id,))
    if not runs:
        raise HTTPException(status_code=404, detail="Workflow not found")
    run = runs[0]
    steps = rows(conn, "SELECT * FROM workflow_steps WHERE run_id=? ORDER BY id", (run_id,))
    run["steps"] = steps
    return run


@app.get("/workflows", response_model=List[WorkflowRun])
def list_workflows(limit: int = 20):
    conn = db()
    return rows(
        conn,
        "SELECT * FROM workflow_runs ORDER BY started_at DESC LIMIT ?",
        (limit,),
    )


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


@app.get("/team", response_model=List[dict])
def list_team_members():
    conn = db()
    return rows(conn, "SELECT * FROM team_members WHERE active = 1 ORDER BY name")


@app.get("/customers/{customer_id}/interactions", response_model=List[dict])
def get_customer_interactions(customer_id: str):
    conn = db()
    return rows(
        conn,
        "SELECT * FROM interactions WHERE customer_id = ? ORDER BY created_at DESC",
        (customer_id,)
    )


@app.get("/tickets/{ticket_id}/notes", response_model=List[dict])
def get_ticket_notes(ticket_id: str):
    conn = db()
    return rows(
        conn,
        "SELECT * FROM notes WHERE ticket_id = ? ORDER BY created_at ASC",
        (ticket_id,)
    )


@app.get("/analytics/summary")
def get_analytics_summary():
    conn = db()
    
    # Customer metrics
    customer_metrics = rows(conn, """
        SELECT 
            COUNT(*) as total_customers,
            AVG(health_score) as avg_health_score,
            SUM(mrr) as total_mrr,
            COUNT(CASE WHEN lifecycle_stage = 'trial' THEN 1 END) as trial_customers,
            COUNT(CASE WHEN lifecycle_stage = 'customer' THEN 1 END) as paying_customers,
            COUNT(CASE WHEN lifecycle_stage = 'churn_risk' THEN 1 END) as churn_risk_customers
        FROM customers
    """)[0]
    
    # Ticket metrics
    ticket_metrics = rows(conn, """
        SELECT 
            COUNT(*) as total_tickets,
            COUNT(CASE WHEN status = 'open' THEN 1 END) as open_tickets,
            COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed_tickets,
            COUNT(CASE WHEN priority = 'critical' THEN 1 END) as critical_tickets,
            COUNT(CASE WHEN sla_breach = 1 THEN 1 END) as sla_breaches,
            AVG(satisfaction_rating) as avg_satisfaction
        FROM tickets
    """)[0]
    
    # Recent activity
    recent_tickets = rows(conn, """
        SELECT t.*, c.name as customer_name 
        FROM tickets t 
        JOIN customers c ON t.customer_id = c.id 
        ORDER BY t.created_at DESC 
        LIMIT 10
    """)
    
    # Customer health distribution
    health_distribution = rows(conn, """
        SELECT 
            CASE 
                WHEN health_score >= 90 THEN 'Excellent'
                WHEN health_score >= 75 THEN 'Good'
                WHEN health_score >= 60 THEN 'Fair'
                ELSE 'Poor'
            END as health_category,
            COUNT(*) as count
        FROM customers
        GROUP BY health_category
    """)
    
    return {
        "customers": customer_metrics,
        "tickets": ticket_metrics,
        "recent_activity": recent_tickets,
        "health_distribution": health_distribution,
        "generated_at": "now"
    }


@app.get("/analytics/revenue")
def get_revenue_analytics():
    conn = db()
    
    # Revenue by plan type
    revenue_by_plan = rows(conn, """
        SELECT 
            plan_type,
            COUNT(*) as customer_count,
            SUM(mrr) as total_mrr,
            AVG(mrr) as avg_mrr
        FROM customers 
        WHERE lifecycle_stage = 'customer'
        GROUP BY plan_type
        ORDER BY total_mrr DESC
    """)
    
    # Revenue by region
    revenue_by_region = rows(conn, """
        SELECT 
            region,
            COUNT(*) as customer_count,
            SUM(mrr) as total_mrr
        FROM customers 
        WHERE lifecycle_stage = 'customer'
        GROUP BY region
        ORDER BY total_mrr DESC
    """)
    
    # Industry analysis
    industry_analysis = rows(conn, """
        SELECT 
            industry,
            COUNT(*) as customer_count,
            SUM(mrr) as total_mrr,
            AVG(health_score) as avg_health_score
        FROM customers 
        WHERE lifecycle_stage = 'customer'
        GROUP BY industry
        ORDER BY total_mrr DESC
    """)
    
    return {
        "revenue_by_plan": revenue_by_plan,
        "revenue_by_region": revenue_by_region, 
        "industry_analysis": industry_analysis
    }


@app.get("/analytics/support")
def get_support_analytics():
    conn = db()
    
    # Tickets by priority and status
    ticket_matrix = rows(conn, """
        SELECT 
            priority,
            status,
            COUNT(*) as count
        FROM tickets
        GROUP BY priority, status
        ORDER BY priority, status
    """)
    
    # Team performance
    team_performance = rows(conn, """
        SELECT 
            tm.name,
            tm.role,
            COUNT(t.id) as assigned_tickets,
            COUNT(CASE WHEN t.status = 'resolved' THEN 1 END) as resolved_tickets,
            AVG(t.satisfaction_rating) as avg_rating
        FROM team_members tm
        LEFT JOIN tickets t ON tm.id = t.assigned_to
        WHERE tm.active = 1
        GROUP BY tm.id, tm.name, tm.role
        ORDER BY assigned_tickets DESC
    """)
    
    # SLA compliance
    sla_compliance = rows(conn, """
        SELECT 
            COUNT(*) as total_tickets,
            COUNT(CASE WHEN sla_breach = 0 THEN 1 END) as compliant_tickets,
            ROUND(COUNT(CASE WHEN sla_breach = 0 THEN 1 END) * 100.0 / COUNT(*), 2) as compliance_rate
        FROM tickets
    """)[0]
    
    return {
        "ticket_matrix": ticket_matrix,
        "team_performance": team_performance,
        "sla_compliance": sla_compliance
    }


@app.get("/healthz")
def healthz():
    return {"ok": True}
