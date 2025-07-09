from snowflake.snowpark.functions import call_function, col, lit
from snowflake.snowpark.types import VectorType

def embed_text(session, text):
    """Embed raw text using Snowflake Cortex."""
    df = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{text}') AS EMBEDDING
    """)
    return df.collect()[0]['EMBEDDING']

def query_similar_chunks(session, query_embedding, table_name="DOCUMENT_VECTORS", top_k=3):
    """Retrieve top-k similar documents from vector store using parameter-safe query."""

    if not isinstance(query_embedding, list) or len(query_embedding) != 768:
        raise ValueError("query_embedding must be a list of 768 floats")

    # Create a literal vector expression
    query_vector_expr = lit(query_embedding).cast(VectorType(float, 768))

    # Load table as Snowpark DataFrame
    df = session.table(table_name)

    # Add similarity score using Snowflake's vector function
    df_with_scores = df.with_column(
        "score",
        call_function("VECTOR_COSINE_SIMILARITY", query_vector_expr, col("EMBEDDING"))
    )

    # Return top-k as pandas DataFrame
    return (
        df_with_scores
        .sort(col("score").desc())
        .limit(top_k)
        .select("DOC_ID", "DOC_TEXT", "score")
        .to_pandas()
    )

def construct_prompt_with_context(context_chunks, user_question):
    # Combine context with user input for RAG prompting.
    context_text = "\n---\n".join(chunk for chunk in context_chunks)
    return f"Context: {context_text}\n\nQuestion: {user_question}"
