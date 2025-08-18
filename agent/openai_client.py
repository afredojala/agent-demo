# ABOUTME: OpenAI client configuration with function calling tool schemas
# ABOUTME: Defines structured tool definitions for the agent's capabilities
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://litellm.platform.datadrivet.ai",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "tool_search_customers",
            "description": "Search customers by (partial) name.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_list_tickets",
            "description": "List tickets for a given customer id and status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["open", "closed"]},
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_create_note",
            "description": "Create a note on a ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["ticket_id", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_send_email",
            "description": "Send an email with subject and body.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_emit_view_intent",
            "description": "Control the UI by setting a view or adding/removing panels.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["set_view", "add_panel", "remove_panel"],
                    },
                    "view_id": {
                        "type": "string",
                        "enum": ["customer-list", "customer-detail", "triage"],
                    },
                    "panel": {"type": "string", "enum": ["NotesPanel"]},
                },
                "required": ["type"],
            },
        },
    },
]
