import os
from typing import Annotated, TypedDict
from fastapi import FastAPI
from pydantic import BaseModel

# LangGraph & LangChain Imports
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

# 1. THE TOOLS (Optimized for small model accuracy)
@tool
def check_order_status(order_id: str):
    """USE THIS whenever a customer asks about order status or tracking."""
    return "STATUS_REPORT: Order 123 is DELAYED due to weather. Expected delivery: Tomorrow."

@tool
def check_product_inventory(product_name: str):
    """USE THIS for any question about stock. IT IS THE ONLY SOURCE OF TRUTH."""
    inventory = {
        "solar panel": "15 units", 
        "battery pack": "0 units", 
        "inverter": "5 units"
    }
    item = product_name.lower().strip()
    count = inventory.get(item, "0 units")
    return f"STRICT_CONFIRMED_DATA: Warehouse count for {item} is EXACTLY {count}. DO NOT report any other number."

@tool
def lookup_suncoast_policy(topic: str):
    """CRITICAL TOOL: Use this for ALL questions about Suncoast company rules, returns, and shipping."""
    topic_clean = topic.lower()
    policies = {
        "return": "Suncoast offers a 30-day money-back guarantee. Items must be in original packaging.",
        "shipping": "Standard Suncoast shipping is free for orders over $500 and takes 3-5 days.",
    }
    
    # Keyword matching for better reliability
    for key, value in policies.items():
        if key in topic_clean:
            return f"POLICY_MANUAL_EXCERPT: {value}"
            
    return "POLICY_MANUAL_EXCERPT: Specific policy not found. Please contact Suncoast management."

tools = [check_order_status, check_product_inventory, lookup_suncoast_policy]
tool_node = ToolNode(tools)

# 2. THE BRAIN
# Connecting to Ollama via Tailscale IP
llm = ChatOllama(
    model="llama3.2", 
    base_url="http://100.84.103.76:11434", 
    temperature=0
)
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def call_llama(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def should_continue(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# 3. THE WORKFLOW
workflow = StateGraph(State)
workflow.add_node("agent", call_llama)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")
app_graph = workflow.compile()

# 4. API SETUP
app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/webhook")
async def handle_webhook(request: ChatRequest):
    system_prompt = SystemMessage(
        content=(
            "You are the Suncoast Customer Support Agent. "
            "You MUST use tools for any factual data regarding orders, inventory, or policies. "
            "If a tool says we have 5 units, report EXACTLY 5 units. "
            "Never guess or apologize for stock levels that exist in the tool."
        )
    )
    initial_state = {"messages": [system_prompt, HumanMessage(content=request.message)]}
    
    try:
        result = app_graph.invoke(initial_state)
        return {"ai_resolution": result["messages"][-1].content}
    except Exception as e:
        return {"ai_resolution": f"Infrastructure Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
