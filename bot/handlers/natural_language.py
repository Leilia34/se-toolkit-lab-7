"""Natural language handler with LLM-based intent routing."""
import asyncio
import json
import sys
from services.lms_client import LMSClient
from services.llm_client import LLMClient
from services.llm_tools import TOOLS
async def handle_natural_language(query: str) -> str:
    """
    Route natural language queries to backend via LLM tool calling.
    Supports multi-step reasoning with tool result feedback loop.
    """
    llm = LLMClient()
    lms = LMSClient()
    
    system_prompt = """You are an LMS assistant with access to backend tools.
CRITICAL: Always use tools to get REAL DATA before answering. Never guess.

For multi-step questions (e.g., "which lab has lowest pass rate"):
1. First call get_items to get all labs
2. Then call get_pass_rates for EACH lab
3. Compare the results
4. Return the answer with specific numbers

Tool usage guidelines:
- get_items: List all labs and tasks
- get_pass_rates(lab="lab-XX"): Get per-task scores with percentages
- get_scores(lab="lab-XX"): Get score distribution buckets
- get_groups(lab="lab-XX"): Compare group performance
- get_top_learners(lab="lab-XX", limit=N): Get top N students
- get_completion_rate(lab="lab-XX"): Get completion percentage
- get_timeline(lab="lab-XX"): Get submissions over time
- get_learners: Get all enrolled students

Lab ID format: "lab-01", "lab-02", "lab-03", "lab-04", "lab-05", "lab-06", "lab-07"

If the query is unclear or gibberish, ask for clarification politely."""


    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Call LLM
        response = await llm.chat(messages, tools=TOOLS)
        
        # Check if LLM returned content without tool calls
        if not response.get("tool_calls"):
            content = response.get("content", "")
            if content:
                return content
            return "I couldn't process that request. Try asking about labs, scores, or students."
        
        # Execute tool calls
        tool_results = []
        for tool_call in response["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])
            
            print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)
            
            result = await _execute_tool(tool_name, tool_args, lms)
            tool_results.append({
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "result": result
            })
            print(f"[tool] Result: {len(str(result))} chars", file=sys.stderr)
        
        print(f"[summary] Feeding {len(tool_results)} tool results back to LLM", file=sys.stderr)
        
        # Append assistant message
        messages.append(response)
        
        # Append tool results
        for tr in tool_results:
            messages.append({
                "role": "tool",
                "content": json.dumps(tr["result"], ensure_ascii=False),
                "tool_call_id": tr["tool_call_id"]
            })
    
    return "I need more iterations to answer this question."


async def _execute_tool(tool_name: str, arguments: dict, lms: LMSClient):
    """Execute a tool call and return result."""
    if tool_name == "get_items":
        return await lms.get_items()
    
    elif tool_name == "get_learners":
        return await lms.get_learners()
    
    elif tool_name == "get_scores":
        lab = arguments.get("lab", "")
        return await lms.get_scores(lab)
    
    elif tool_name == "get_pass_rates":
        lab = arguments.get("lab", "")
        return await lms.get_pass_rates(lab)
    
    elif tool_name == "get_timeline":
        lab = arguments.get("lab", "")
        return await lms.get_timeline(lab)
    
    elif tool_name == "get_groups":
        lab = arguments.get("lab", "")
        return await lms.get_groups(lab)
    
    elif tool_name == "get_top_learners":
        lab = arguments.get("lab", "")
        limit = arguments.get("limit", 10)
        return await lms.get_top_learners(lab, limit)
    
    elif tool_name == "get_completion_rate":
        lab = arguments.get("lab", "")
        return await lms.get_completion_rate(lab)
    
    elif tool_name == "trigger_sync":
        return await lms.trigger_sync()
    
    return {"error": f"Unknown tool: {tool_name}"}
