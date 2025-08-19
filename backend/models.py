# ABOUTME: Pydantic models and database schema for the comprehensive CRM system
# ABOUTME: Defines data structures for customers, tickets, notes, team members, and interactions
from pydantic import BaseModel, Field
from typing import Optional


class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    plan_type: Optional[str] = None
    region: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None


class Customer(CustomerBase):
    id: str
    created_at: Optional[str] = None
    last_activity: Optional[str] = None
    health_score: Optional[int] = 75
    mrr: Optional[float] = 0
    lifecycle_stage: Optional[str] = "prospect"


class TicketBase(BaseModel):
    customer_id: str
    title: str
    description: Optional[str] = None
    status: str = Field(default="open", pattern="^(open|in_progress|waiting_customer|resolved|closed)$")
    priority: Optional[str] = Field(default="medium", pattern="^(low|medium|high|critical)$")
    category: Optional[str] = None
    assigned_to: Optional[str] = None


class Ticket(TicketBase):
    id: str
    created_at: str
    updated_at: Optional[str] = None
    resolved_at: Optional[str] = None
    first_response_at: Optional[str] = None
    sla_breach: Optional[bool] = False
    satisfaction_rating: Optional[int] = None


class NoteCreate(BaseModel):
    ticket_id: str
    body: str
    author: Optional[str] = "system"
    note_type: Optional[str] = "internal"


class Note(BaseModel):
    id: str
    ticket_id: str
    body: str
    author: str
    note_type: str
    created_at: str


class TeamMember(BaseModel):
    id: str
    name: str
    role: str
    email: Optional[str] = None
    department: Optional[str] = None
    timezone: Optional[str] = "UTC"
    active: Optional[bool] = True


class Interaction(BaseModel):
    id: int
    customer_id: str
    interaction_type: str
    subject: Optional[str] = None
    details: Optional[str] = None
    created_at: str
    created_by: Optional[str] = None


class EmailCreate(BaseModel):
    to: str
    subject: str
    body: str


class WorkflowRun(BaseModel):
    id: int
    name: str
    status: str
    started_at: str
    finished_at: Optional[str] = None
    result: Optional[str] = None


class WorkflowRunCreate(BaseModel):
    name: str


class WorkflowStep(BaseModel):
    id: int
    run_id: int
    name: str
    status: str
    started_at: str
    finished_at: Optional[str] = None
    result: Optional[str] = None


class WorkflowStepCreate(BaseModel):
    name: str
    status: str
    result: Optional[str] = None
