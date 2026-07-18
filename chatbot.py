import streamlit as st

st.set_page_config(
    page_title="SynapseAI",
    layout="wide",
)


if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("SynapseAI")
st.caption("An extensible AI platform built with LangChain")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)


    response = "LLM integration coming soon..."

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(response)