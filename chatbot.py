import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from pathlib import Path

from components.rag import  get_rag_response, index_documents, list_documents, delete_document, is_relevant, UPLOADS_PATH
from components.agent import get_agent


def build_history(messages):
    history = []

    for message in messages:
        if message["role"] == "user":
            history.append(HumanMessage(content=message["content"]))
        else:
            history.append(AIMessage(content=message["content"]))

    return history


def display_sources(sources):

    if not sources:
        return

    st.markdown("**Sources:**")

    for source in sources:

        if "page" in source:
            st.markdown(
                f"- `{source['source']}` — page {source['page']}"
            )
        else:
            st.markdown(
                f"- `{source['source']}`"
            )

agent = get_agent()


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


if uploaded_files:

    if st.sidebar.button("Index Documents"):

        Path(UPLOADS_PATH).mkdir(parents=True, exist_ok=True)

        for uploaded_file in uploaded_files:
            file_path = Path(UPLOADS_PATH)/uploaded_file.name

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        with st.spinner("Indexing Documents..."):
            index_documents()

        st.sidebar.success(
            f"Successfully indexed {len(uploaded_files)} documents(s)"
        )

st.sidebar.divider()

st.sidebar.subheader("Documents")

documents = list_documents()

if documents:

    for document in documents:

        col1, col2 = st.sidebar.columns([4, 1])

        col1.write(document["name"])

        if col2.button("Delete", key=f"delete_{document['path']}"):

            try:
                delete_document(document["path"])

                st.sidebar.success(
                    f"Deleted {document['name']}"
                )

                st.rerun()

            except Exception as e:
                st.sidebar.error(
                    f"Failed to delete {document['name']}: {e}"
                )

else:
    st.sidebar.caption("No documents found.")

    

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            display_sources(message.get("sources", []))


user_input = st.chat_input("Ask Anything...")

if user_input:

    history = build_history(st.session_state.messages)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    try:

        sources = []

        with st.chat_message("assistant"):

            if is_relevant(user_input):

                answer_stream, sources = get_rag_response(
                    question=user_input,
                    history=history,
                )

                response = st.write_stream(answer_stream)

                display_sources(sources)

            else:

                result = agent.invoke(
                    {
                        "messages": [
                            *history,
                            HumanMessage(content=user_input)
                        ]
                    }
                )

                response = result["messages"][-1].content

                st.markdown(response)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
                "sources": sources,
            }
        )

    except Exception as e:
        st.error(f"Error: {e}")

