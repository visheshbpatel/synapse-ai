import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

model = ChatOpenAI(
    model="openai/gpt-oss-20b:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    max_tokens=300,
    temperature=0.3,
    streaming=True
)

SYSTEM_PROMPT = "You are a helpful AI."

prompt = ChatPromptTemplate.from_messages(
    [
        ('system', SYSTEM_PROMPT),
        ('human', "{question}")
    ]
)

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

    st.session_state.messages.append(
        {"role": "user", "content":user_input}
        )
    
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = st.write_stream(
            chain.stream({"question": user_input})
        )

    st.session_state.messages.append(
        {"role": "assistant", "content":response}
        )
    

