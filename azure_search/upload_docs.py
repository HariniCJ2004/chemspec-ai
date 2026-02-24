import os
import uuid
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
 
from ingestion.chunking import chunk_markdown_files
from azure_search.search_client import get_embedding
 
load_dotenv()
 
endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX")
 
search_client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(key)
)
 
def upload_all_documents():
 
    tds_docs = chunk_markdown_files("data/markdown/tds", "tds")
    sds_docs = chunk_markdown_files("data/markdown/sds", "sds")
 
    all_docs = tds_docs + sds_docs
 
    print(f"Total chunks to upload: {len(all_docs)}")
 
    if len(all_docs) == 0:
        print("❌ No documents found. Check markdown folder.")
        return
 
    batch = []
 
    for doc in all_docs:
        embedding = get_embedding(doc.page_content)
 
        batch.append({
            "id": str(uuid.uuid4()),
            "content": doc.page_content,
            "source": doc.metadata["source"],
            "type": doc.metadata["type"],
            "contentVector": embedding
        })
 
    result = search_client.upload_documents(batch)
 
    print("Upload result:", result)
    print("✅ Documents uploaded successfully")
 
 
if __name__ == "__main__":
    upload_all_documents()
 