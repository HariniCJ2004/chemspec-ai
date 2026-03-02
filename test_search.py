from azure_search.search_client import search_documents
 
results = search_documents(
    query="materials to avoid",
    document_type="sds",
    top_k=5
)
 
print("\nReturned Chunks:\n")
for r in results:
    print("="*50)
    print(r["content"])