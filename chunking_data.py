from ingestion.chunking import chunk_markdown_files
 
tds_docs = chunk_markdown_files("data/markdown/tds", "tds")
sds_docs = chunk_markdown_files("data/markdown/sds", "sds")
 
print("TDS chunks:", len(tds_docs))
print("SDS chunks:", len(sds_docs))