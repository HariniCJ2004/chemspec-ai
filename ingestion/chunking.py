# ingestion/chunking.py
 
import os
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
 
 
MAX_CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
 
 
def clean_repeated_headers(text: str):
    """
    Removes repeating SDS header lines.
    """
    lines = text.splitlines()
    cleaned = []
 
    for line in lines:
        if "SAFETY DATA SHEET" in line.upper():
            continue
        if "Version" in line and "Revision" in line:
            continue
        cleaned.append(line)
 
    return "\n".join(cleaned)
 
 
def split_sds_sections(text: str):
    """
    Proper SDS section extraction.
    Keeps SECTION header + full body until next SECTION.
    """
 
    pattern = r"(SECTION\s+\d+.*?)(?=SECTION\s+\d+|$)"
 
    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )
 
    return [m.strip() for m in matches if m.strip()]
 
 
def recursive_split(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_text(text)
 
 
def chunk_markdown_files(folder_path: str, doc_type: str):
 
    documents = []
 
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return documents
 
    for file in os.listdir(folder_path):
        if not file.endswith(".md"):
            continue
 
        print(f"\n📄 Processing file: {file}")
 
        with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
            text = f.read()
 
        text = clean_repeated_headers(text)
 
        chunk_counter = 1
 
        # =========================
        # SDS STRATEGY
        # =========================
        if doc_type.lower() == "sds":
 
            sections = split_sds_sections(text)
            print(f"🔎 SDS Sections found: {len(sections)}")
 
            for section in sections:
 
                # If section too large → split safely
                if len(section) > MAX_CHUNK_SIZE:
                    smaller_chunks = recursive_split(section)
                else:
                    smaller_chunks = [section]
 
                for chunk in smaller_chunks:
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={
                                "source": file,
                                "type": "sds",
                                "chunk_id": chunk_counter,
                            },
                        )
                    )
                    chunk_counter += 1
 
        # =========================
        # TDS STRATEGY
        # =========================
        else:
 
            print("🔎 Using recursive chunking for TDS")
 
            chunks = recursive_split(text)
 
            for chunk in chunks:
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "source": file,
                            "type": "tds",
                            "chunk_id": chunk_counter,
                        },
                    )
                )
                chunk_counter += 1
 
        print(f"✅ Total chunks created for {doc_type}: {chunk_counter - 1}")
 
    return documents
 
 
if __name__ == "__main__":
    print("\nTesting TDS chunking...\n")
    chunk_markdown_files("data/markdown/tds", "tds")
 
    print("\nTesting SDS chunking...\n")
    chunk_markdown_files("data/markdown/sds", "sds")