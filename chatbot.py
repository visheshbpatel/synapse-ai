from components.prompt import prompt
from components.llm import model

import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage



def build_history(messages):
    history = []

    for message in messages:
        if message["role"] == "user":
            history.append(HumanMessage(content=message["content"]))
        else:
            history.append(AIMessage(content=message["content"]))

    return history


parser = StrOutputParser()

chain = prompt | model | parser


st.set_page_config(
    page_title="SynapseAI",
    layout="wide"
)

st.title("SynapseAI")
st.caption("Built with LangChain")


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

