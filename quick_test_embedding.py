from azure_search.search_client import get_embedding
 
print(len(get_embedding("hello")))