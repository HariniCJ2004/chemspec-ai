from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv
from azure_search.search_client import get_embedding
 
load_dotenv()
 
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)
 
 
def retrieve(query, doc_type):
 
    # Step 1: Get embedding
    vector = get_embedding(query)
 
    # Step 2: Create proper VectorizedQuery object
    vector_query = VectorizedQuery(
        vector=vector,
        k_nearest_neighbors=5,
        fields="contentVector"
    )
 
    # Step 3: Perform search
    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        filter=f"type eq '{doc_type.lower()}'"
    )
 
    context = ""
    for r in results:
        context += r["content"] + "\n"
 
    return context