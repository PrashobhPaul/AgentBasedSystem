import streamlit as st
from agents.bot_agent import handle_user_query

st.title("Event Assistant Bot")
user = st.text_input("Enter your name")
query = st.text_input("Ask me anything about the event:")

if st.button("Submit") and user:
    response = handle_user_query(user, query)
    st.write(response)
