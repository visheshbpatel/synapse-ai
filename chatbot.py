import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import os

load_dotenv()


def build_history(messages):
    history = []

    for message in messages:
        if message["role"] == "user":
            history.append(HumanMessage(content=message["content"]))
        else:
            history.append(AIMessage(content=message["content"]))

    return history


model = ChatOpenAI(
    model="openai/gpt-4.1-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    max_tokens=200,
    temperature=0.3,
    streaming=True
)

SYSTEM_PROMPT = """
You are SynapseAI, a knowledgeable and professional AI assistant.

Your goals are:
- Provide accurate, clear, and concise answers.
- Explain technical concepts step by step when appropriate.
- Use Markdown formatting for readability.
- Use bullet points or numbered lists when they improve clarity.
- If the user asks for code, write clean, well-structured, and documented code.
- If information is uncertain, clearly state your uncertainty instead of guessing.
- Ask clarifying questions only when required to give a correct answer.
- Avoid unnecessary repetition and filler.
- Maintain context throughout the conversation and provide consistent responses.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ('system', SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
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

