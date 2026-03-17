from typing import Annotated, TypedDict, Union, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import os
from dotenv import load_dotenv

load_dotenv()

# Import our custom search tool
from tools import search_wikipedia

# Define the state of the graph
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]

# Initialize the LLM with AI Tunnel base URL to bypass regional restrictions
llm = ChatOpenAI(
    model="gpt-4o", 
    temperature=0,
    base_url="https://api.aitunnel.ru/v1"
)

# System prompt to guide the model to use tools manually
SYSTEM_PROMPT = """You are a helpful assistant with access to a Wikipedia search tool.
If you need to search Wikipedia, you MUST output a JSON object in the following format:
{"tool": "search_wikipedia", "query": "Your search query"}

Always be specific with your search queries.
If you receive an ERROR from the tool, try to fix the query and call it again.
If you have enough information, provide the final answer."""

# Define the nodes
def call_model(state: AgentState):
    messages = state['messages']
    
    # Add system prompt if it's the first message
    if not any(isinstance(m, HumanMessage) and m.content == SYSTEM_PROMPT for m in messages):
        messages = [HumanMessage(content=SYSTEM_PROMPT)] + messages
        
    response = llm.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    
    # Check if the model is trying to call a tool via raw text JSON
    if '{"tool": "search_wikipedia"' in last_message.content:
        return "continue"
    return "end"

def call_tools(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    import json
    import re
    
    # Extract JSON from content
    tool_outputs = []
    try:
        match = re.search(r'\{.*\}', last_message.content, re.DOTALL)
        if match:
            tool_call = json.loads(match.group(0))
            if tool_call.get("tool") == "search_wikipedia":
                query = tool_call.get("query")
                result = search_wikipedia(query)
                
                # We return as a HumanMessage (or SystemMessage) to feed back into the model
                # since we aren't using native ToolMessages here for simplicity/compatibility
                feedback = HumanMessage(content=f"TOOL RESULT for '{query}':\n{result}")
                tool_outputs.append(feedback)
    except Exception as e:
        tool_outputs.append(HumanMessage(content=f"ERROR parsing tool call: {str(e)}"))
    
    return {"messages": tool_outputs}

# Build the graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("action", call_tools)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END
    }
)

workflow.add_edge("action", "agent")

# Compile the graph
app = workflow.compile()
