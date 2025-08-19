# ABOUTME: Main agent crew system for task execution
# ABOUTME: Handles OpenAI function calling loop and tool execution
import json
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.openai_client import client, tools
from agent.tools import (
    search_customers,
    list_tickets,
    create_note,
    send_email,
    emit_intent,
    get_customer_stats,
    bulk_update_tickets,
    generate_report,
    execute_workflow,
    workflow_decision,
    set_workflow_state,
    get_workflow_state,
    create_customer,
    schedule_followup,
    check_sla_status,
    assign_ticket,
    create_visualization,
)



async def call_tool(name: str, args: dict):
    """Execute a tool function based on its name and arguments."""
    # Handle async tools
    if name == "tool_emit_view_intent":
        return await emit_intent(args)
    elif name == "tool_create_visualization":
        return await create_visualization(**args)
    
    # Handle sync tools
    elif name == "tool_search_customers":
        return search_customers(**args)
    elif name == "tool_list_tickets":
        return list_tickets(**args)
    elif name == "tool_create_note":
        return create_note(**args)
    elif name == "tool_send_email":
        return send_email(**args)
    elif name == "tool_get_customer_stats":
        return get_customer_stats(**args)
    elif name == "tool_bulk_update_tickets":
        return bulk_update_tickets(**args)
    elif name == "tool_generate_report":
        return generate_report(**args)
    elif name == "tool_execute_workflow":
        return execute_workflow(**args)
    elif name == "tool_workflow_decision":
        return workflow_decision(**args)
    elif name == "tool_set_workflow_state":
        return set_workflow_state(**args)
    elif name == "tool_get_workflow_state":
        return get_workflow_state(**args)
    elif name == "tool_create_customer":
        return create_customer(**args)
    elif name == "tool_schedule_followup":
        return schedule_followup(**args)
    elif name == "tool_check_sla_status":
        return check_sla_status(**args)
    elif name == "tool_assign_ticket":
        return assign_ticket(**args)
    else:
        raise ValueError(f"Unknown tool {name}")


async def run_task(user_goal: str) -> str:
    """Execute a task using OpenAI function calling."""
    messages = [
        {
            "role": "system",
            "content": """You are an operations agent for a mini-CRM system. You help users manage customers, tickets, and execute complex business workflows.

Available capabilities:
- Search and manage customers
- View and manage support tickets  
- Create notes on tickets
- Send emails (mock)
- Generate analytics and reports
- Perform bulk operations on tickets
- Execute multi-step workflows with decision points
- Control UI views (triage, customer-list, dashboard, analytics, timeline, calendar)
- CREATE DYNAMIC VISUALIZATIONS: Generate charts and graphs based on user queries

VISUALIZATION CAPABILITIES: When users ask for charts, graphs, trends, or visual data representation, use the create_visualization tool:
- Bar charts for comparing categories (customer activity, ticket counts)
- Line charts for trends over time (ticket trends, performance metrics)  
- Pie/Doughnut charts for distributions (ticket status, customer segments)
- Examples: "show me a bar chart of customer activity", "create a pie chart of ticket status", "visualize ticket trends over time"

WORKFLOWS: You can execute sophisticated business processes:
- customer_onboarding: Full onboarding with premium/standard paths
- ticket_escalation: SLA checking with escalation decisions  
- weekly_report: Comprehensive reporting with trend analysis
- customer_health_check: Proactive customer health monitoring

For UI control, always use view intents to show relevant views:
- "triage" for ticket management
- "customer-list" for customer browsing  
- "dashboard" for overview/summary
- "analytics" for statistics and reports
- "timeline" for chronological views
- "calendar" for scheduled items

WORKFLOW EXECUTION: When users request complex processes like "onboard a customer", "run escalation workflow", or "generate weekly report", use the execute_workflow tool. These workflows include decision points and branching logic.

VISUALIZATION STRATEGY: When appropriate, automatically create visualizations to enhance your responses. For example:
- Customer questions → Create customer activity charts
- Ticket analysis → Create ticket status distributions  
- Performance queries → Create trend line charts
- Always choose the most appropriate chart type for the data being presented

Always start by setting an appropriate view, then execute the requested task. For workflows, explain each step as you progress. Be conversational and show your decision-making process.""",
        },
        {"role": "user", "content": user_goal},
    ]

    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            response = client.chat.completions.create(
                model="openrouter/openai/gpt-4o",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0,
            )

            choice = response.choices[0]
            messages.append(choice.message.model_dump())
            
            print(f"DEBUG: Agent response has tool_calls: {choice.message.tool_calls is not None}")
            if choice.message.tool_calls:
                print(f"DEBUG: Number of tool calls: {len(choice.message.tool_calls)}")

            if choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments or "{}")
                    
                    print(f"DEBUG: Calling tool {tool_name} with args: {args}")

                    try:
                        tool_result = await call_tool(tool_name, args)
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(tool_result),
                            }
                        )
                    except Exception as e:
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"error": str(e)}),
                            }
                        )
                continue

            return choice.message.content or "Task completed"

        except Exception as e:
            return f"Error during task execution: {str(e)}"

    return "Task execution exceeded maximum iterations"


if __name__ == "__main__":
    task = "Show Acme's open tickets in a triage view; for the oldest one, add a follow-up note and email me a short summary."
    print("Starting task execution...")
    result = asyncio.run(run_task(task))
    print(f"Task result: {result}")
