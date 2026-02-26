from azure_search.search_client import search_documents
 
def search_documents_tool(query: str, document_type: str):
    """
    Tool: Performs vector search on Azure AI Search.
 
    IMPORTANT:
    - Uses document_type exactly as received from planner.
    - No hardcoding.
    - Returns only retrieved chunks.
    """
 
    # Normalize type
    document_type = document_type.lower().strip()
 
    print("\n--- TOOL EXECUTION ---")
    print("QUERY:", query)
    print("DOCUMENT TYPE RECEIVED:", document_type)
 
    chunks = search_documents(
        query=query,
        document_type=document_type,
        top_k=5
    )
 
    print("RETRIEVED CHUNKS:", len(chunks))
    print("----------------------\n")
 
    # Return ONLY chunks (clean)
    return chunks