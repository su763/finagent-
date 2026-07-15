
import os
import chromadb
from pypdf import PdfReader

print("--- 1. Script started successfully ---")

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def build_vector_store(doc_dir="data/documents", chroma_dir="data/chroma_db"):
    print(f"--- 3. Inside build_vector_store function ---")
    print(f"Checking directory: {os.path.abspath(doc_dir)}")
    
    # Ensure directories exist
    os.makedirs(doc_dir, exist_ok=True)
    os.makedirs(chroma_dir, exist_ok=True)
    
    # Check if there are actually PDFs to process
    pdf_files = [f for f in os.listdir(doc_dir) if f.endswith('.pdf')]
    print(f"Found PDF files: {pdf_files}")
    
    if not pdf_files:
        print(f"ALERT: No PDFs found in {doc_dir}. Please drop your PDF here!")
        return

    # Initialize ChromaDB persistent client
    print("Initializing ChromaDB persistent client...")
    client = chromadb.PersistentClient(path=chroma_dir)
    collection = client.get_or_create_collection(name="financial_docs")
    
    print(f"Processing {len(pdf_files)} documents...")
    
    for filename in pdf_files:
        file_path = os.path.join(doc_dir, filename)
        reader = PdfReader(file_path)
        
        doc_chunks = []
        doc_metadatas = []
        doc_ids = []
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
                
            text = " ".join(text.split())
            chunks = chunk_text(text)
            
            for i, chunk in enumerate(chunks):
                doc_chunks.append(chunk)
                doc_metadatas.append({
                    "source": filename,
                    "page": page_num + 1
                })
                doc_ids.append(f"{filename}_p{page_num+1}_c{i}")
        
        if doc_chunks:
            collection.add(
                documents=doc_chunks,
                metadatas=doc_metadatas,
                ids=doc_ids
            )
            print(f"Ingested {filename}: {len(doc_chunks)} chunks.")

    print("\nVector store built successfully!")

print("--- 2. Before __main__ check ---")

if __name__ == "__main__":
    print("--- 4. __main__ block triggered ---")
    build_vector_store()