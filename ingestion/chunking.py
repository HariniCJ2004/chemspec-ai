import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
 
 
def chunk_markdown_files(folder_path, doc_type):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
 
    documents = []
 
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return documents
 
    for file in os.listdir(folder_path):
        if file.endswith(".md"):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                text = f.read()
 
            chunks = splitter.split_text(text)
 
            for chunk in chunks:
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "source": file,
                            "type": doc_type
                        }
                    )
                )
 
    print(f"Total chunks created for {doc_type}: {len(documents)}")
    return documents