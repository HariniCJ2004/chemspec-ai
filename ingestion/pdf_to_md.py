import os
from pypdf import PdfReader
 
 
def convert_pdf_to_markdown(pdf_path, output_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
 
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
 
            if page_text:
                text += f"\n\n## Page {page_num + 1}\n\n"
                text += page_text
            else:
                print(f"⚠️ No text found on page {page_num + 1} in {pdf_path}")
 
        if text.strip() == "":
            print(f"❌ No extractable text in {pdf_path}")
            return
 
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
 
        print(f"✅ Markdown created: {output_path}")
 
    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {e}")
 
 
def process_folder(input_folder, output_folder):
    if not os.path.exists(input_folder):
        print(f"❌ Input folder not found: {input_folder}")
        return
 
    os.makedirs(output_folder, exist_ok=True)
 
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith(".pdf")]
 
    if not pdf_files:
        print(f"❌ No PDF files found in {input_folder}")
        return
 
    for file in pdf_files:
        pdf_path = os.path.join(input_folder, file)
        md_filename = file.replace(".pdf", ".md")
        md_path = os.path.join(output_folder, md_filename)
 
        convert_pdf_to_markdown(pdf_path, md_path)
 
 
if __name__ == "__main__":
    process_folder("data/raw/tds", "data/markdown/tds")
    process_folder("data/raw/sds", "data/markdown/sds")