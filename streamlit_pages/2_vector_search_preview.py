import streamlit as st
from snowflake.snowpark import Session
from utils.common_utils import get_connection_params
from utils.rag_utils import embed_text, query_similar_chunks

# Snowflake connection (use secrets in production)
connection_parameters = get_connection_params()
session = Session.builder.configs(connection_parameters).create()

st.title("🔍 Vector Search Preview")
st.markdown("Search your embedded documents using semantic similarity.")

user_query = st.text_input("Enter a natural language query:")

if user_query:
    with st.spinner("Embedding and searching..."):
        query_vector = embed_text(session, user_query)
        top_docs = query_similar_chunks(session, query_vector)

    st.success(f"Top {len(top_docs)} matching document chunks:")
    for _, row in top_docs.iterrows():
        st.markdown("---")
        st.markdown(f"**Document ID:** {row['DOC_ID']}")
        st.markdown(f"**Similarity Score:** {row['SCORE']:.4f}")
        st.markdown(f"```text\n{row['DOC_TEXT'][:1000]}\n```")
