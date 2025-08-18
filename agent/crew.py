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
)


def call_tool(name: str, args: dict):
    """Execute a tool function based on its name and arguments."""
    if name == "tool_search_customers":
        return search_customers(**args)
    elif name == "tool_list_tickets":
        return list_tickets(**args)
    elif name == "tool_create_note":
        return create_note(**args)
    elif name == "tool_send_email":
        return send_email(**args)
    elif name == "tool_emit_view_intent":
        return asyncio.run(emit_intent(args))
    else:
        raise ValueError(f"Unknown tool {name}")


def run_task(user_goal: str) -> str:
    """Execute a task using OpenAI function calling."""
    messages = [
        {
            "role": "system",
            "content": "You are an operations agent that completes tasks using tools and controls the app's views via view-intents. Always start by setting appropriate views for the task.",
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

            if choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments or "{}")

                    try:
                        tool_result = call_tool(tool_name, args)
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
    result = run_task(task)
    print(f"Task result: {result}")
