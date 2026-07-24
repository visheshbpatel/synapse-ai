import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from pathlib import Path

from components.rag import get_rag_chain, UPLOADS_PATH


Path(UPLOADS_PATH).mkdir(parents=True, exist_ok=True)

def build_history(messages):
    history = []

    for message in messages:
        if message["role"] == "user":
            history.append(HumanMessage(content=message["content"]))
        else:
            history.append(AIMessage(content=message["content"]))

    return history

chain = get_rag_chain()

st.set_page_config(
    page_title="SynapseAI",
    layout="wide"
)

st.title("SynapseAI")
st.caption("Built with LangChain")


uploaded_files = st.sidebar.file_uploader(
    "Upload Documents",
    type=["pdf","txt","md"],
    accept_multiple_files=True
)

for uploaded_file in uploaded_files:
    file_path = Path(UPLOADS_PATH)/uploaded_file.name

    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())


if uploaded_files:
    st.sidebar.success(f"Uploaded {len(uploaded_files)} document(s).")



if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])


user_input = st.chat_input("Ask Anything...")

if user_input:

    history = build_history(st.session_state.messages)

    st.session_state.messages.append(
        {"role": "user", "content":user_input}
        )
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    try:
        with st.chat_message("assistant"):
            response = st.write_stream(
                chain.stream(
                    {
                        "history": history,
                        "question": user_input
                    }
                )
            )

        st.session_state.messages.append(
            {"role": "assistant", "content":response}
        )
    
    except Exception as e:
        st.error(f"Error:{e}")

