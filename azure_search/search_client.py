# azure_search/search_client.py
 
import os
from dotenv import load_dotenv
 
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
 
load_dotenv()
 
 
# ---------------------------
# Azure OpenAI Client (Embedding)
# ---------------------------
 
openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
 
 
def get_embedding(text: str):
    response = openai_client.embeddings.create(
        input=text,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    )
    return response.data[0].embedding
 
 
# ---------------------------
# Azure AI Search Client
# ---------------------------
 
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)
 
 
def search_documents(query: str, document_type: str, top_k: int = 5):
 
    query_vector = get_embedding(query)
 
    results = search_client.search(
        search_text=None,
        vector_queries=[
            {
                "vector": query_vector,
                "fields": "content_vector",
                "k": top_k
            }
        ],
        filter=f"document_type eq '{document_type}'"
    )
 
    chunks = []
 
    for result in results:
        chunks.append({
            "id": result["id"],
            "content": result["content"],
            "document_type": result["document_type"]
        })
 
    return chunks