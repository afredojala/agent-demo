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
            "description": "Search customers by name, location, or other criteria.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "location": {"type": "string"},
                    "criteria": {"type": "string"}
                },
                "required": [],
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
                        "enum": ["customer-list", "customer-detail", "triage", "dashboard", "analytics", "timeline", "calendar", "workflow"],
                    },
                    "panel": {"type": "string", "enum": ["NotesPanel"]},
                },
                "required": ["type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_customer_stats",
            "description": "Get customer statistics and analytics data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "enum": ["ticket_count", "activity", "status_summary", "all"]
                    }
                },
                "required": ["metric"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_bulk_update_tickets",
            "description": "Perform bulk operations on tickets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["close_resolved", "escalate_old", "update_status"]
                    },
                    "criteria": {"type": "string"},
                    "new_status": {"type": "string", "enum": ["open", "closed"]}
                },
                "required": ["operation"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_generate_report",
            "description": "Generate various types of reports.",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["daily_summary", "weekly_summary", "customer_health", "ticket_analysis"]
                    },
                    "date_range": {"type": "string"}
                },
                "required": ["report_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_execute_workflow",
            "description": "Execute a predefined multi-step workflow with decision points.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_name": {
                        "type": "string",
                        "enum": ["customer_onboarding", "ticket_escalation", "weekly_report", "customer_health_check"]
                    },
                    "context": {"type": "object"}
                },
                "required": ["workflow_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_workflow_decision",
            "description": "Make a decision in a workflow based on conditions and data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "condition": {"type": "string"},
                    "data": {"type": "object"},
                    "options": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["condition", "options"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_set_workflow_state",
            "description": "Store workflow state data for multi-step processes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "object"}
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_workflow_state",
            "description": "Retrieve workflow state data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"}
                },
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_create_customer",
            "description": "Create a new customer in the system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "priority": {"type": "string", "enum": ["standard", "premium", "enterprise"]}
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_schedule_followup",
            "description": "Schedule a follow-up action for a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "days": {"type": "number"},
                    "task_type": {"type": "string", "enum": ["call", "email", "review", "check-in"]},
                    "description": {"type": "string"}
                },
                "required": ["customer_id", "days", "task_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_check_sla_status",
            "description": "Check if a ticket is compliant with SLA requirements.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"}
                },
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_assign_ticket",
            "description": "Assign a ticket to a team member.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "assignee": {"type": "string", "enum": ["support_team", "senior_support", "manager", "technical_lead"]}
                },
                "required": ["ticket_id", "assignee"],
            },
        },
    },
]
