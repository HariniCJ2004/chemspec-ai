# ingestion/pdf_to_md.py
 
import os
import pdfplumber
 
 
def convert_pdf_to_markdown(pdf_path: str, output_path: str):
    """
    Converts a PDF file into structured Markdown.
    Extracts:
    - Page text
    - Tables (formatted row-wise with separators)
    """
 
    try:
        full_text = ""
 
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
 
                full_text += f"\n\n# Page {page_number}\n\n"
 
                # -------------------------
                # Extract Normal Text
                # -------------------------
                page_text = page.extract_text()
 
                if page_text:
                    full_text += page_text.strip() + "\n"
 
                # -------------------------
                # Extract Tables
                # -------------------------
                tables = page.extract_tables()
 
                if tables:
                    for table_index, table in enumerate(tables, start=1):
                        full_text += f"\n\n## Table {table_index} (Page {page_number})\n\n"
 
                        for row in table:
                            # Clean row cells
                            cleaned_row = [
                                cell.replace("\n", " ").strip() if cell else ""
                                for cell in row
                            ]
 
                            # Convert row to markdown-style pipe format
                            row_text = " | ".join(cleaned_row)
                            full_text += row_text + "\n"
 
        # -------------------------
        # Handle Empty Extraction
        # -------------------------
        if not full_text.strip():
            print(f"❌ No extractable content found in: {pdf_path}")
            return
 
        # -------------------------
        # Save Markdown File
        # -------------------------
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
 
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)
 
        print(f"✅ Markdown created: {output_path}")
 
    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {e}")
 
 
def process_folder(input_folder: str, output_folder: str):
    """
    Converts all PDFs in a folder into Markdown files.
    """
 
    if not os.path.exists(input_folder):
        print(f"❌ Input folder not found: {input_folder}")
        return
 
    os.makedirs(output_folder, exist_ok=True)
 
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]
 
    if not pdf_files:
        print(f"❌ No PDF files found in: {input_folder}")
        return
 
    for file in pdf_files:
        pdf_path = os.path.join(input_folder, file)
        md_filename = file.replace(".pdf", ".md")
        md_path = os.path.join(output_folder, md_filename)
 
        print(f"📄 Processing: {file}")
        convert_pdf_to_markdown(pdf_path, md_path)
 
 
if __name__ == "__main__":
    # Adjust these paths if needed
    process_folder("data/raw/tds", "data/markdown/tds")
    process_folder("data/raw/sds", "data/markdown/sds")