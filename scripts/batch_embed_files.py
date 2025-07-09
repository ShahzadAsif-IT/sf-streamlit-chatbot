import pypdf2  # For PDFs
from pathlib import Path
import pandas as pd
from snowflake.snowpark import Session
from utils.common_utils import get_connection_params
from utils.rag_utils import embed_text

# Initialize Snowflake session (replace with st.secrets for production)
connection_parameters = get_connection_params()
session = Session.builder.configs(connection_parameters).create()

# === CONFIG === #
DATA_DIR = "data/"
SUPPORTED_EXT = [".pdf", ".txt"]
CHUNK_SIZE = 500  # Characters per chunk
OVERLAP = 50  # Overlap between chunks

def extract_text(file_path):
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        doc = pypdf2.open(file_path)
        return "\n".join([page.get_text() for page in doc])
    elif ext == ".txt":
        return file_path.read_text(encoding='utf-8')
    return ""

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def load_and_embed_files():
    files = list(Path(DATA_DIR).glob("*"))
    rows = []
    for f in files:
        if f.suffix.lower() not in SUPPORTED_EXT:
            continue
        print(f"Processing: {f.name}")
        raw_text = extract_text(f)
        chunks = chunk_text(raw_text)
        for i, chunk in enumerate(chunks):
            doc_id = f"{f.stem}_chunk_{i}"
            vector = embed_text(session, chunk)
            rows.append({
                "DOC_ID": doc_id,
                "DOC_TEXT": chunk,
                "EMBEDDING": vector
            })

    if rows:
        df = pd.DataFrame(rows)
        session.write_pandas(df, table_name="DOCUMENT_VECTORS", auto_create_table=True)
        print(f"Loaded {len(rows)} chunks into DOCUMENT_VECTORS")
    else:
        print("No valid documents found to process.")

if __name__ == "__main__":
    load_and_embed_files()
