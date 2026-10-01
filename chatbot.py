import streamlit as st
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langsmith import traceable
import uuid
import sqlite3


from components.rag import index_documents, list_documents, delete_document, get_user_paths
from components.graph import stream_response, graph
from components.llm import model
from components.conversation import create_conversation, get_conversations, get_conversation, touch_conversation
from components.user import authenticate_user, create_user
from components.document import create_document


def render_authentication():
    st.title("SynapseAI")

    signup_tab, login_tab = st.tabs(["Sign Up", "Login"])

    with signup_tab:
        st.subheader("Create an account")

        signup_username = st.text_input(
            "Username",
            key="signup_username",
        )

        signup_email = st.text_input(
            "Email",
            key="signup_email",
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password",
        )

        if st.button("Create account"):
            if (
                not signup_username
                or not signup_email
                or not signup_password
            ):
                st.error("All fields are required.")

            else:
                try:
                    create_user(
                        username=signup_username,
                        email=signup_email,
                        password=signup_password,
                    )

                    st.success(
                        "Account created. You can now log in."
                    )

                except sqlite3.IntegrityError:
                    st.error(
                        "Username or email already exists."
                    )

    with login_tab:
        st.subheader("Login")

        login_email = st.text_input(
            "Email",
            key="login_email",
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password",
        )

        if st.button("Login"):
            user = authenticate_user(
                login_email,
                login_password,
            )

            if user is None:
                st.error("Invalid email or password.")

            else:
                st.session_state.user_id = user["id"]
                st.session_state.username = user["username"]

                st.success(
                    f"Welcome, **{user['username']}**!"
                )

                st.rerun()


def load_conversation(thread_id):
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    state = graph.get_state(config)

    messages = []
    pending_sources = []

    messages_state = state.values.get("messages", [])

    for message in messages_state:

        if isinstance(message, HumanMessage):
            messages.append({
                "role": "user",
                "content": message.content
            })

        elif isinstance(message, ToolMessage):
            artifact = getattr(message, "artifact", None)

            if artifact:
                pending_sources.extend(artifact)

        elif isinstance(message, AIMessage):
            if message.content:
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "sources": pending_sources
                })

                pending_sources = []

    return messages


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


@traceable(
    name="Generate Chat Title",
    run_type="chain",
    tags=["chat-title"],
)
def generate_chat_title(user_input):
    try:
        prompt = (
            "Generate a short chat title from the user's message. "
            "Use exactly 3 to 4 words. "
            "Return only the title, with no quotes or punctuation.\n\n"
            f"User message: {user_input}"
        )

        response = model.invoke(prompt)
        return response.content.strip()

    except Exception:
        return user_input[:40]


st.set_page_config(
    page_title="SynapseAI",
    layout="wide"
)


if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = None


if st.session_state.user_id is None:
    render_authentication()
    st.stop()


st.title("SynapseAI")
st.caption("AI assistant with RAG, tools, and persistent conversations")


uploaded_files = st.sidebar.file_uploader(
    "Upload Documents",
    type=["pdf","txt","md"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.sidebar.button("Index Documents"):
        user_paths = get_user_paths(
            st.session_state.user_id
        )

        uploads_path = user_paths["uploads"]

        uploads_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        for uploaded_file in uploaded_files:
            file_path = uploads_path / uploaded_file.name

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            create_document(
                user_id=st.session_state.user_id,
                filename=uploaded_file.name,
            )

        with st.spinner("Indexing Documents..."):
            result = index_documents(st.session_state.user_id)

        if result["indexed"]:
            st.sidebar.success(
                f"Indexed: **{len(result['indexed'])}** document(s)"
            )

        if result["changed"]:
            st.sidebar.info(
                f"Updated: **{len(result['changed'])}** document(s)"
            )

        if result["deleted"]:
            st.sidebar.info(
                f"Deleted: **{len(result['deleted'])}** document(s)"
            )

        if result["unchanged"]:
            st.sidebar.caption(
                f"Unchanged: **{len(result['unchanged'])}** document(s)"
            )

        if result["failed"]:
            st.sidebar.error(
                f"Failed: **{len(result['failed'])}** document(s)"
            )


if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

conversations = get_conversations(st.session_state.user_id)


with st.sidebar:
    st.divider()

    if st.button("+ New Chat", use_container_width=True):
        st.session_state.thread_id = None
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.header("Conversations")

    for conversation in conversations:
        thread_id = conversation["thread_id"]

        if st.button(
            conversation["title"],
            key=f"conversation_{thread_id}",
            use_container_width=True
        ):
            st.session_state.thread_id = thread_id
            st.session_state.messages = load_conversation(thread_id)

            st.rerun()

    st.divider()

    st.header("Documents")

    documents = list_documents(st.session_state.user_id)

    if documents:

        for document in documents:

            col1, col2 = st.sidebar.columns([4, 1])

            col1.write(document["name"])

            if col2.button("Delete", key=f"delete_{document['path']}"):

                try:
                    delete_document(
                        st.session_state.user_id,
                        document["name"],
                    )

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



for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            display_sources(message.get("sources", []))


user_input = st.chat_input("Ask Anything...")
    

if user_input:
    if st.session_state.thread_id is None:
        st.session_state.thread_id = str(uuid.uuid4())

    thread_id = st.session_state.thread_id

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        with st.chat_message("assistant"):
            stream, sources = stream_response(
                user_input,
                thread_id,
                st.session_state.user_id
            )

            response = st.write_stream(stream)

            if sources:
                display_sources(sources)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
                "sources": sources
            }
        )

        if get_conversation(st.session_state.user_id, thread_id) is None:
            title = generate_chat_title(user_input)
            create_conversation(
                user_id=st.session_state.user_id,
                thread_id=thread_id,
                title=title,
            )
        else:
            touch_conversation(st.session_state.user_id, thread_id)

        st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")

