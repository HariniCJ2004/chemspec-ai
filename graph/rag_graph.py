# graph/rag_graph.py
 
from typing import TypedDict
import os
from dotenv import load_dotenv
 
from langgraph.graph import StateGraph
from openai import AzureOpenAI
 
from agents.planner_agent import planner
from azure_search.search_client import search_documents
from utils.prompt_loader import load_prompt
 
load_dotenv()
 
 
# -------------------------
# Azure OpenAI Client
# -------------------------
 
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
 
 
# -------------------------
# Graph State
# -------------------------
 
class AgentState(TypedDict):
    query: str
    route: str
    context: str
    answer: str
 
 
# -------------------------
# Planner Node
# -------------------------
 
def planner_node(state: AgentState):
 
    route = planner.route_query(state["query"])  # returns "SDS" or "TDS"
 
    return {
        "query": state["query"],
        "route": route,
        "context": "",
        "answer": ""
    }
 
 
# -------------------------
# Retrieval Node
# -------------------------
 
def retrieval_node(state: AgentState):
 
    query = state["query"]
    document_type = state["route"]
 
    chunks = search_documents(query, document_type=document_type)
 
    # Merge chunks into single context block
    context = "\n\n".join([chunk["content"] for chunk in chunks])
 
    return {
        "query": query,
        "route": document_type,
        "context": context,
        "answer": ""
    }
 
 
# -------------------------
# Answer Node
# -------------------------
 
def answer_node(state: AgentState):
 
    query = state["query"]
    route = state["route"]
    context = state["context"]
 
    # Load retrieval system prompt from external file
    system_prompt_template = load_prompt("retrieval_agent_prompt.md")
 
    system_prompt = system_prompt_template.format(
        document_type=route
    )
 
    user_prompt = f"""
User Question:
{query}
 
Retrieved Context:
{context}
"""
 
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
 
    return {
        "query": query,
        "route": route,
        "context": context,
        "answer": response.choices[0].message.content.strip()
    }
 
 
# -------------------------
# Build Graph
# -------------------------
 
builder = StateGraph(AgentState)
 
builder.add_node("planner", planner_node)
builder.add_node("retrieval", retrieval_node)
builder.add_node("answer", answer_node)
 
builder.set_entry_point("planner")
 
builder.add_edge("planner", "retrieval")
builder.add_edge("retrieval", "answer")
 
graph = builder.compile()