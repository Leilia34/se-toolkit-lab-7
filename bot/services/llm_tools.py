# services/llm_tools.py
from typing import List, Dict, Any, Callable
import json

# Определяем инструменты (functions) для LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_labs",
            "description": "Get the list of all available labs. Returns each lab's title and id.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get pass rates (scores) for a specific lab. Provide the lab title exactly as it appears.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab_title": {
                        "type": "string",
                        "description": "The exact title of the lab, e.g., 'Lab 01 – Products, Architecture & Roles'"
                    }
                },
                "required": ["lab_title"]
            }
        }
    }
]

async def call_tool(tool_name: str, arguments: Dict[str, Any], lms_client) -> str:
    """Execute a tool call and return a string result."""
    if tool_name == "get_labs":
        items = await lms_client.get_items()
        labs = [item for item in items if item.get("type") == "lab"]
        if not labs:
            return "No labs found."
        # Format nicely
        result = "Available labs:\n" + "\n".join(f"- {lab['title']}" for lab in labs)
        return result
    elif tool_name == "get_scores":
        lab_title = arguments.get("lab_title")
        if not lab_title:
            return "Please specify a lab title."
        # Find lab by title (case-insensitive)
        items = await lms_client.get_items()
        lab = None
        for item in items:
            if item.get("type") == "lab" and item.get("title", "").lower() == lab_title.lower():
                lab = item
                break
        if not lab:
            return f"Lab '{lab_title}' not found."
        pass_rates = await lms_client.get_pass_rates(str(lab["id"]))
        if not pass_rates:
            return f"No score data for {lab['title']}."
        lines = [f"Scores for {lab['title']}:"]
        for task in pass_rates:
            lines.append(f"- {task['task']}: avg score {task.get('avg_score', 0):.1f}, attempts {task.get('attempts', 0)}")
        return "\n".join(lines)
    else:
        return f"Unknown tool: {tool_name}"
