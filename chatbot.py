import sqlite3
import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langsmith import traceable

from components.conversation import (
    create_conversation,
    get_conversation,
    get_conversations,
    touch_conversation,
)
from components.document import create_document
from components.graph import graph, stream_response
from components.llm import model
from components.rag import (
    delete_document,
    get_user_paths,
    index_documents,
    list_documents,
)
from components.ui import (
    apply_theme,
    render_account_card,
    render_auth_header,
    render_brand,
    render_hero,
    render_section_label,
    render_sources,
)
from components.user import authenticate_user, create_user


CONVERSATION_LIST_HEIGHT = 320
DOCUMENT_LIST_HEIGHT = 150
DOCUMENT_LIST_SCROLL_AFTER = 4


def render_authentication():
    with st.container(key="auth"):
        render_auth_header()

        signup_tab, login_tab = st.tabs(["Sign Up", "Login"])

        with signup_tab:
            with st.form("signup_form"):
                st.subheader("Create your account")

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

                submitted = st.form_submit_button(
                    "Create account",
                    type="primary",
                    width="stretch",
                )

            if submitted:
                if not signup_username or not signup_email or not signup_password:
                    st.error("All fields are required.")
                else:
                    try:
                        create_user(
                            username=signup_username,
                            email=signup_email,
                            password=signup_password,
                        )
                        st.success("Account created. You can now log in.")
                    except sqlite3.IntegrityError:
                        st.error("Username or email already exists.")

        with login_tab:
            with st.form("login_form"):
                st.subheader("Welcome back")

                login_email = st.text_input(
                    "Email",
                    key="login_email",
                )

                login_password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                )

                submitted = st.form_submit_button(
                    "Login",
                    type="primary",
                    width="stretch",
                )

            if submitted:
                user = authenticate_user(
                    login_email,
                    login_password,
                )

                if user is None:
                    st.error("Invalid email or password.")
                else:
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]
                    st.session_state.email = user["email"]
                    st.session_state.thread_id = None
                    st.session_state.messages = []

                    st.rerun()


def load_conversation(thread_id):
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    state = graph.get_state(config)

    messages = []
    pending_sources = []

    messages_state = state.values.get("messages", [])

    for message in messages_state:
        if isinstance(message, HumanMessage):
            messages.append(
                {
                    "role": "user",
                    "content": message.content,
                }
            )

        elif isinstance(message, ToolMessage):
            artifact = getattr(message, "artifact", None)

            if artifact:
                pending_sources.extend(artifact)

        elif isinstance(message, AIMessage):
            if message.content:
                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content,
                        "sources": pending_sources,
                    }
                )

                pending_sources = []

    return messages


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


def render_user_menu():
    username = st.session_state.username or "User"

    with st.popover(
        username,
        icon=":material/account_circle:",
        width="stretch",
    ):
        render_account_card(
            username,
            st.session_state.get("email"),
        )

        if st.button(
            "Log out",
            width="stretch",
            key="logout_button",
        ):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.email = None
            st.session_state.thread_id = None
            st.session_state.messages = []

            st.rerun()


def render_document_section():
    for level, text in st.session_state.pop("index_feedback", []):
        getattr(st, level)(text)

    uploaded_files = st.file_uploader(
        "PDF, TXT or MD files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        key=f"document_uploader_{st.session_state.uploader_version}",
    )

    if uploaded_files:
        if st.button(
            "Index Documents",
            type="primary",
            width="stretch",
            key="index_documents",
        ):
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

                with open(file_path, "wb") as file:
                    file.write(
                        uploaded_file.getbuffer()
                    )

                create_document(
                    user_id=st.session_state.user_id,
                    filename=uploaded_file.name,
                )

            with st.spinner("Indexing documents..."):
                result = index_documents(
                    st.session_state.user_id
                )

            feedback = []

            if result["indexed"]:
                feedback.append(
                    (
                        "success",
                        f"Indexed {len(result['indexed'])} document(s).",
                    )
                )

            if result["changed"]:
                feedback.append(
                    (
                        "info",
                        f"Updated {len(result['changed'])} document(s).",
                    )
                )

            if result["deleted"]:
                feedback.append(
                    (
                        "info",
                        f"Deleted {len(result['deleted'])} document(s).",
                    )
                )

            if result["failed"]:
                feedback.append(
                    (
                        "error",
                        f"Failed {len(result['failed'])} document(s).",
                    )
                )

            st.session_state.index_feedback = feedback
            st.session_state.uploader_version += 1

            st.rerun()

    documents = list_documents(
        st.session_state.user_id
    )

    if not documents:
        st.caption("No documents indexed yet.")
        return

    if len(documents) > DOCUMENT_LIST_SCROLL_AFTER:
        holder = st.container(
            height=DOCUMENT_LIST_HEIGHT,
            border=False,
        )
    else:
        holder = st.container()

    with holder:
        for document in documents:
            col1, col2 = st.columns(
                [5, 1],
                vertical_alignment="center",
            )

            with col1:
                st.caption(document["name"])

            with col2:
                if st.button(
                    "",
                    icon=":material/close:",
                    type="tertiary",
                    key=f"delete_{document['path']}",
                    help=f"Delete {document['name']}",
                ):
                    try:
                        delete_document(
                            st.session_state.user_id,
                            document["name"],
                        )

                        st.rerun()

                    except Exception as error:
                        st.error(
                            f"Failed to delete document: {error}"
                        )

def render_conversation_list():
    conversations = get_conversations(
        st.session_state.user_id
    )

    if not conversations:
        st.caption("No conversations yet.")
        return

    with st.container(
        height=CONVERSATION_LIST_HEIGHT,
        border=False,
        key="chat_history",
    ):
        for conversation in conversations:
            thread_id = conversation["thread_id"]

            is_active = (
                thread_id == st.session_state.thread_id
            )

            if st.button(
                conversation["title"],
                key=f"conv_{thread_id}",
                width="stretch",
                type="primary" if is_active else "secondary",
            ):
                st.session_state.thread_id = thread_id
                st.session_state.messages = (
                    load_conversation(thread_id)
                )

                st.rerun()


def render_sidebar():
    with st.sidebar:
        render_brand()

        render_user_menu()

        with st.expander(
            "Documents",
            icon=":material/folder:",
            expanded=False,
        ):
            render_document_section()

        if st.button(
            "+  New Chat",
            type="primary",
            width="stretch",
            key="new_chat",
        ):
            st.session_state.thread_id = None
            st.session_state.messages = []
            st.rerun()

        render_section_label("Conversations")

        render_conversation_list()


def render_chat():
    if not st.session_state.messages:
        render_hero()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                render_sources(
                    message.get("sources", [])
                )

    user_input = st.chat_input(
        "Ask anything..."
    )

    if not user_input:
        return

    if st.session_state.thread_id is None:
        st.session_state.thread_id = str(
            uuid.uuid4()
        )

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
                st.session_state.user_id,
            )

            response = st.write_stream(stream)

            if sources:
                render_sources(sources)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
                "sources": sources,
            }
        )

        conversation = get_conversation(
            st.session_state.user_id,
            thread_id,
        )

        if conversation is None:
            title = generate_chat_title(
                user_input
            )

            create_conversation(
                user_id=st.session_state.user_id,
                thread_id=thread_id,
                title=title,
            )
        else:
            touch_conversation(
                st.session_state.user_id,
                thread_id,
            )

        st.rerun()

    except Exception as error:
        st.error(
            f"Something went wrong: {error}"
        )


def initialize_session():
    defaults = {
        "user_id": None,
        "username": None,
        "email": None,
        "thread_id": None,
        "messages": [],
        "uploader_version": 0,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def main():
    st.set_page_config(
        page_title="SynapseAI",
        page_icon="S",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_theme()
    initialize_session()

    if st.session_state.user_id is None:
        render_authentication()
        st.stop()

    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()