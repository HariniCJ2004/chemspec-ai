from typing import TypedDict
import os
import json
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from openai import AzureOpenAI
from typing import Dict, Any 
from agents.planner_agent import Planner
from azure_search.search_client import search_documents
 
load_dotenv()
 
# ==========================
# Azure OpenAI Client
# ==========================
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)
 
# ==========================
# Graph State
# ==========================
class AgentState(TypedDict):
    query: str
    route: str
    context: str
    answer: str
 
 
# ==========================
# Planner Node
# ==========================
def planner_node(state: AgentState):
 
    planner_instance = Planner()
    route = planner_instance.route_query(state["query"])  # "SDS" or "TDS"
 
    print("ROUTED TO:", route)
 
    return {
        "query": state["query"],
        "route": route,
        "context": "",
        "answer": "",
    }
 
 
# ==========================
# Answer Node (Tool Calling)
# ==========================
def answer_node(state: AgentState):
 
    query = state["query"]
    route = state["route"]
 
    # Tool schema
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_documents_tool",
                "description": "Search relevant chunks from Azure AI Search based on document type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "User question"
                        },
                        "document_type": {
                            "type": "string",
                            "enum": ["SDS", "TDS"],
                            "description": "Document type to search"
                        }
                    },
                    "required": ["query", "document_type"]
                }
            }
        }
    ]
 
    system_prompt = """
You are a strictly document-grounded assistant.
 
Use ONLY the exact information explicitly present
in the retrieved chunks.
 
Rules:
- Do NOT infer.
- Do NOT assume.
- Do NOT expand.
- Do NOT summarize beyond provided text.
- Do NOT add environmental interpretations unless explicitly written.
 
If information is not clearly present in retrieved chunks,
respond exactly:
 
"The retrieved documents do not contain this information."
 
Return only supported facts.
"""
 
    # ======================
    # First Call (Force Tool)
    # ======================
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        tools=tools,
        tool_choice={
            "type": "function",
            "function": {"name": "search_documents_tool"}
        },
        temperature=0
    )
 
    message = response.choices[0].message
 
    if not message.tool_calls:
        raise Exception("Tool was not called. Retrieval failed.")
 
    tool_call = message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
 
    # ======================
    # Execute Retrieval
    # ======================
    retrieved_chunks = search_documents(
        query=args["query"],
        document_type=args["document_type"]
    )
 
    if not retrieved_chunks:
        raise Exception("Azure Search returned no chunks.")
 
    # ======================
    # Clean Context Formatting
    # ======================
    context_text = "\n\n".join(
        [f"Chunk {i+1}:\n{chunk['content']}"
         for i, chunk in enumerate(retrieved_chunks)]
    )
 
    print("\n--- Retrieved Context Preview ---\n")
    print(context_text[:1000])  # show preview only
 
    # ======================
    # Second Call (Grounded Answer)
    # ======================
    final_response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {
                "role": "system",
                "content": "Answer strictly using the retrieved context. Do not hallucinate."
            },
            {
                "role": "user",
                "content": f"""
User Question:
{query}
 
Retrieved Context:
{context_text}
 
Provide a clean, structured answer.
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
 
 
# ==========================
# Build LangGraph
# ==========================
builder = StateGraph(AgentState)
 
builder.add_node("planner", planner_node)
builder.add_node("answer", answer_node)
 
builder.set_entry_point("planner")
builder.add_edge("planner", "answer")
 
graph = builder.compile()