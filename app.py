import streamlit as st
import scripts.load_embeddings as ld

ld.load_embeddings()

st.set_page_config(page_title="Snowflake Chatbot", page_icon="❄️")

# Load home content
st.title("Snowflake AI Chatbot")
st.markdown("Welcome to the Snowflake AI Chatbot interface.")
st.markdown("Use the sidebar to navigate to:")
st.markdown("- **Chatbot Interface** to start a conversation")
st.markdown("- **Vector Search Preview** to explore document matches")

pages = {
    "Main:": [
        st.Page('streamlit_pages/1_chatbot_interface.py' , title="Chatbot Interface", icon="❄️")
    ],
    "Support:": [
        st.Page('streamlit_pages/2_vector_search_preview.py' , title="Vector Search Preview", icon="🔍")
    ]
}

pg = st.navigation(pages, position='sidebar')
pg.run()
