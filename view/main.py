import streamlit as st
from streamlit import session_state as state
import requests
port = 8000

st.subheader("Unravel Source")

if "messages" not in st.session_state:
    st.session_state.messages = []
# if st.button("Clear Chat"):
    # st.session_state.messages = []
for message  in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
if prompt := st.chat_input():
    st.session_state.messages.append({"role":"user" , "content" : prompt })
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        st.markdown("Processing your request...")
        res = requests.post(f"http://localhost:{port}/chat/", json= { 'prompt' : prompt})
        full_response = res.json()["Response"]
        if "Sources:" in full_response:
             answer_text, sources_text = full_response.split("Sources:", 1)
        else:
            answer_text, sources_text = full_response, ""

        
        response = st.write(answer_text)
        st.write("### Sources")
        st.write(sources_text)
    st.session_state.messages.append({"role":"assistant", "content": answer_text})