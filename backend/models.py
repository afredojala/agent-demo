# ABOUTME: Pydantic models and database schema for the mini-CRM system
# ABOUTME: Defines data structures for customers, tickets, notes, and emails
from pydantic import BaseModel, Field
from typing import Optional


class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None


class Customer(CustomerBase):
    id: str


class TicketBase(BaseModel):
    customer_id: str
    title: str
    status: str = Field(default="open", pattern="^(open|closed)$")


class Ticket(TicketBase):
    id: str
    created_at: str


class NoteCreate(BaseModel):
    ticket_id: str
    body: str


class Note(BaseModel):
    id: str
    ticket_id: str
    body: str
    created_at: str


class EmailCreate(BaseModel):
    to: str
    subject: str
    body: str
