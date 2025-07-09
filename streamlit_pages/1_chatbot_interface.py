import streamlit as st
from snowflake.snowpark import Session
import pandas as pd
from datetime import datetime, timezone
from utils.common_utils import get_connection_params
from utils.cortex_utils import call_cortex
from utils.rag_utils import embed_text, query_similar_chunks, construct_prompt_with_context

# Save message to Snowflake
def save_message(user_id:str, session_id:str, role:str, content:str):
    
    df = pd.DataFrame([{
        "USER_ID": user_id,
        "SESSION_ID": session_id,
        "TIMESTAMP": datetime.now(timezone.utc),
        "ROLE": role,
        "MESSAGE": content
    }])
    session.write_pandas(df, table_name="CHAT_MEMORY", auto_create_table=False)

# Load config (in real deployment, use Streamlit secrets)
connection_parameters = get_connection_params()
session = Session.builder.configs(connection_parameters).create()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

st.title("Chat Window")
user_input = st.chat_input("Ask your Snowflake assistant anything...")

if user_input:
    prev_context = "\n--\n".join(chat['content'] for chat in st.session_state['chat_history'])
    st.session_state['chat_history'].append({"role": "user", "content": user_input})
    save_message("user1", "session1", "user", user_input)

    # 1. Embed user question
    user_embedding = embed_text(session, user_input)

    # 2. Retrieve top 3 similar docs
    similar_chunks = query_similar_chunks(session, user_embedding)

    # 3. Construct prompt with retrieved context
    context = [row["DOC_TEXT"] for _, row in similar_chunks.iterrows()]
    context.append(prev_context)
    rag_prompt = construct_prompt_with_context(context, user_input)

    # 4. Compose chat messages
    messages = [
        {"role": "system", "content": "You are a Snowflake-savvy AI assistant. Answer based on provided context."},
        {"role": "user", "content": rag_prompt}
    ]

    # 5. Call Cortex
    response = call_cortex(session, messages)

    st.session_state['chat_history'].append({"role": "assistant", "content": response})
    save_message("user1", "session1", "assistant", response)

# Display messages
for msg in st.session_state['chat_history']:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])
