from typing import TypedDict
import os
import json
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from openai import AzureOpenAI
from agents.planner_agent import Planner
from azure_search.search_client import search_documents
 
load_dotenv()
 
# =========================================================
# Azure OpenAI Client
# =========================================================
 
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)
 
# =========================================================
# Graph State
# =========================================================
 
class AgentState(TypedDict):
    query: str
    route: str
    context: str
    answer: str
 
 
# =========================================================
# 1️⃣ Planner Node
# =========================================================
 
def planner_node(state: AgentState):
 
    planner_instance = Planner()
    route = planner_instance.route_query(state["query"])  # "SDS" or "TDS"
 
    print("\n🧠 ROUTED TO:", route)
 
    return {
        "query": state["query"],
        "route": route.lower(),   # normalize once
        "context": "",
        "answer": "",
    }
 
 
# =========================================================
# 2️⃣ Answer Node (Tool Calling + Grounded Response)
# =========================================================
 
def answer_node(state: AgentState):
 
    query = state["query"]
    route = state["route"]  # single source of truth
 
    # -----------------------------------------------------
    # Tool Schema
    # -----------------------------------------------------
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_documents_tool",
                "description": "Search documents from Azure AI Search",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "User query"
                        }
                    },
                    "required": ["query"]
                },
            },
        }
    ]
 
    # -----------------------------------------------------
    # First LLM Call → Force Tool Call
    # -----------------------------------------------------
    tool_response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {
                "role": "system",
                "content": "Call the search_documents_tool to retrieve relevant information."
            },
            {
                "role": "user",
                "content": query
            }
        ],
        tools=tools,
        tool_choice={
            "type": "function",
            "function": {"name": "search_documents_tool"}
        },
        temperature=0
    )
 
    message = tool_response.choices[0].message
 
    if not message.tool_calls:
        raise Exception("Tool was not called. Retrieval failed.")
 
    tool_call = message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
 
    # -----------------------------------------------------
    # Execute Retrieval
    # -----------------------------------------------------
    retrieved_chunks = search_documents(
        query=args["query"],
        document_type=route   # injected from planner
    )
 
    if not retrieved_chunks:
        return {
            "query": query,
            "route": route,
            "context": "",
            "answer": "The retrieved documents do not contain this information."
        }
 
    # -----------------------------------------------------
    # Format Retrieved Context
    # -----------------------------------------------------
    context_text = "\n\n".join(
        f"Chunk {i+1}:\n{chunk['content']}"
        for i, chunk in enumerate(retrieved_chunks)
    )
 
    print("\n--- Retrieved Context Preview ---\n")
    print(context_text[:1000])
 
    # -----------------------------------------------------
    # Strict Grounded Answer Call
    # -----------------------------------------------------
    system_prompt = """
You are a strictly document-grounded assistant.
 
Use ONLY the exact information explicitly present in the retrieved context.
 
Rules:
- Do NOT infer.
- Do NOT assume.
- Do NOT expand.
- Do NOT add external knowledge.
- Do NOT summarize beyond provided text.
 
If the answer is not clearly present in the context,
respond exactly with:
 
"The retrieved documents do not contain this information."
"""
 
    final_response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"""
User Question:
{query}
 
Retrieved Context:
{context_text}
"""
            }
        ],
        temperature=0
    )
 
    final_answer = final_response.choices[0].message.content.strip()
 
    return {
        "query": query,
        "route": route,
        "context": context_text,
        "answer": final_answer
    }
 
 
# =========================================================
# Build LangGraph
# =========================================================
 
builder = StateGraph(AgentState)
 
builder.add_node("planner", planner_node)
builder.add_node("answer", answer_node)
 
builder.set_entry_point("planner")
builder.add_edge("planner", "answer")
builder.add_edge("answer", END)
 
graph = builder.compile()