from snowflake.snowpark import Session, Row
from snowflake.snowpark.types import StructType, StructField, StringType, VectorType

from utils.common_utils import get_connection_params
from utils.rag_utils import embed_text

# Connection config (replace with st.secrets or secure method)
connection_parameters = get_connection_params()
session = Session.builder.configs(connection_parameters).create()

# Example documents
SAMPLE_DOCS = [
    {"DOC_ID": "doc_001", "DOC_TEXT": "Welcome to using Snowflake-based Chatbot!"},
    {"DOC_ID": "doc_002", "DOC_TEXT": "My name is Chatbot-Shahzad. How can I help you today?"},
    {"DOC_ID": "doc_003", "DOC_TEXT": "Be vary of long chats. My boss will get upset and may come around begging for your help!"}
]

def load_embeddings(documents=SAMPLE_DOCS):
    rows = []

    for doc in documents:
        # Get embedding as a list of floats
        embedding = embed_text(session, doc["DOC_TEXT"])  # Should return a list of 768 floats

        # Ensure it is a list of 768 floats
        if not isinstance(embedding, list) or len(embedding) != 768:
            raise ValueError("Embedding must be a list of 768 floats")

        rows.append(Row(
            DOC_ID=doc["DOC_ID"],
            DOC_TEXT=doc["DOC_TEXT"],
            EMBEDDING=embedding
        ))

    if rows:
        # Define schema using VECTOR type
        schema = StructType([
            StructField("DOC_ID", StringType()),
            StructField("DOC_TEXT", StringType()),
            StructField("EMBEDDING", VectorType(element_type=float, dimension=768))
        ])

        df_sf = session.create_dataframe(rows, schema=schema)

        # Write to Snowflake table using truncate mode
        df_sf.write.saveAsTable("DOCUMENT_VECTORS", mode="truncate")


if __name__ == "__main__":
    load_embeddings()
