import os
from typing import Annotated, TypedDict, Union, List
from fastapi import FastAPI
from pydantic import BaseModel

# LangGraph & LangChain Imports
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

# 1. Define the Tools
@tool
def check_order_status(order_id: str):
    """Checks the status of a customer order using the order ID."""
    return "STATUS: Order 123 is DELAYED. Delivery: Tomorrow."

@tool
def check_product_inventory(product_name: str):
    """Checks stock. MUST call this for any product availability question."""
    inventory = {
        "solar panel": "15 units",
        "battery pack": "0 units",
        "inverter": "5 units"
    }
    item = product_name.lower().strip()
    count = inventory.get(item, "0 units (not in catalog)")
    # We use a very loud prefix to wake up the small model
    return f"CRITICAL_INVENTORY_DATA: Currently {count} of {item} in stock."

tools = [check_order_status, check_product_inventory]
tool_node = ToolNode(tools)

# 2. Setup the Brain
llm = ChatOllama(
    model="llama3.2", 
    base_url="http://100.84.103.76:11434",
    temperature=0
)
llm_with_tools = llm.bind_tools(tools)

# 3. Define Graph State
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 4. Logic Nodes
def call_llama(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def should_continue(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# 5. Build Workflow
workflow = StateGraph(State)
workflow.add_node("agent", call_llama)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")
app_graph = workflow.compile()

# 6. FastAPI Webhook
app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/webhook")
async def handle_webhook(request: ChatRequest):
    # Short, punchy instructions work better for small models
    system_prompt = SystemMessage(
        content=(
            "You are a factual support bot. "
            "Rule 1: Always use tools for orders and stock. "
            "Rule 2: Report tool numbers exactly. If a tool says '5 units', say '5 units'."
        )
    )
    
    initial_state = {"messages": [system_prompt, HumanMessage(content=request.message)]}
    
    try:
        result = app_graph.invoke(initial_state)
        final_message = result["messages"][-1].content
        return {
            "status": "success",
            "ai_resolution": final_message
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
