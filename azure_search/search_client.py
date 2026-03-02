# azure_search/search_client.py
 
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
 
load_dotenv()
 
# ==============================
# Azure OpenAI Client (Embedding)
# ==============================
openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)
 
def get_embedding(text: str):
    response = openai_client.embeddings.create(
        input=text,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    )
    return response.data[0].embedding
 
 
# ==============================
# Azure AI Search Client
# ==============================
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)
 
 
# ==============================
# Hybrid Search (Vector + Keyword)
# ==============================
def search_documents(query: str, document_type: str, top_k: int = 8):
 
    document_type = document_type.lower()
 
    # Generate query embedding
    query_vector = get_embedding(query)
 
    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="contentVector"
    )
 
    results = search_client.search(
        search_text=query,                 # ✅ HYBRID SEARCH ENABLED
        vector_queries=[vector_query],     # ✅ VECTOR SEARCH
        filter=f"type eq '{document_type}'",
        top=top_k
    )
 
    results_list = list(results)
 
    print("FILTER:", f"type eq '{document_type}'")
    print("TOTAL RESULTS:", len(results_list))
 
    chunks = []
    for r in results_list:
        chunks.append({
            "id": r.get("id", ""),
            "content": r.get("content", ""),
            "document_type": r.get("type", "")
        })
 
    return chunks