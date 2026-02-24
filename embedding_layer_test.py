from azure_search.search_client import get_embedding
 
embedding = get_embedding("What are the hazards?")
print("Embedding length:", len(embedding))