from html import escape
from string import Template

import streamlit as st


BLUE = "#2196F3"
BLUE_BRIGHT = "#38BDF8"
BLUE_DARK = "#1565C0"

BACKGROUND = "#080D14"
SURFACE = "#111923"
SURFACE_RAISED = "#182334"
SIDEBAR = "#0D1622"
BORDER = "#26384F"

TEXT = "#F5F7FA"
MUTED = "#9AAABD"


_THEME_CSS = Template(
    """
<style>
:root {
    color-scheme: dark;
}

/* App shell */

[data-testid="stApp"] {
    background: $background;
    color: $text;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 50% -10%,
            rgba(33, 150, 243, 0.10),
            transparent 38%
        ),
        $background;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stAppDeployButton"],
.stDeployButton {
    display: none;
}

[data-testid="stMainBlockContainer"] {
    max-width: 960px;
    padding-top: 3.5rem;
    padding-bottom: 2rem;
}

[data-testid="stApp"] h1,
[data-testid="stApp"] h2,
[data-testid="stApp"] h3,
[data-testid="stApp"] h4,
[data-testid="stWidgetLabel"] p {
    color: $text;
}

[data-testid="stMarkdownContainer"] a {
    color: $blue_bright;
}

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: $muted;
}

[data-testid="stAlert"] {
    border-radius: 10px;
}

[data-testid="stColumn"] {
    min-width: 0;
}


/* Sidebar */

section[data-testid="stSidebar"] {
    background: $sidebar;
    border-right: 1px solid $border;
}

section[data-testid="stSidebar"] > div {
    background: $sidebar;
}

section[data-testid="stSidebar"][aria-expanded="true"] {
    width: 290px !important;
    min-width: 290px !important;
    max-width: 290px !important;
}

section[data-testid="stSidebar"][aria-expanded="true"] > div {
    width: 100%;
}

[data-testid="stSidebarHeader"] {
    height: 2.5rem;
    min-height: 0;
    padding: 0.5rem 0.75rem 0 1rem;
    margin-bottom: 0;
}

[data-testid="stSidebarUserContent"] {
    padding: 0.25rem 1rem 1rem;
}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.5rem;
}

section[data-testid="stSidebar"] .st-key-chat_history [data-testid="stVerticalBlock"] {
    gap: 0.35rem;
}

.synapse-brand {
    color: $text;
    font-size: 1.3rem;
    font-weight: 750;
    line-height: 1.2;
    letter-spacing: -0.01em;
}

.synapse-brand span {
    color: $blue_bright;
}

.synapse-section-label {
    margin-top: 0.4rem;
    padding-top: 0.8rem;
    border-top: 1px solid $border;
    color: $muted;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}


/* Buttons */

button[data-testid="stBaseButton-secondary"],
[data-testid="stPopover"] button {
    min-height: 38px;
    border: 1px solid $border;
    border-radius: 9px;
    background: $surface;
    color: $text;
    font-weight: 500;
    transition: background 0.15s ease, border-color 0.15s ease;
}

button[data-testid="stBaseButton-secondary"]:hover,
[data-testid="stPopover"] button:hover {
    border-color: $blue;
    background: $surface_raised;
    color: $text;
}

button[data-testid="stBaseButton-secondary"]:focus:not(:active),
[data-testid="stPopover"] button:focus:not(:active) {
    border-color: $blue;
    color: $text;
}

button[data-testid="stBaseButton-secondary"]:active,
[data-testid="stPopover"] button:active {
    border-color: $blue;
    background: $surface_raised;
    color: $text;
}

button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"] {
    min-height: 40px;
    border: 1px solid $blue;
    border-radius: 9px;
    background: linear-gradient(135deg, $blue, $blue_dark);
    color: #FFFFFF;
    font-weight: 600;
    transition: background 0.15s ease, border-color 0.15s ease;
}

button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    border-color: $blue_bright;
    background: linear-gradient(135deg, $blue_bright, $blue);
    color: #FFFFFF;
}

button[data-testid="stBaseButton-primary"]:focus:not(:active),
button[data-testid="stBaseButton-primaryFormSubmit"]:focus:not(:active) {
    border-color: $blue_bright;
    color: #FFFFFF;
    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.35);
}

button[data-testid="stBaseButton-primary"]:active,
button[data-testid="stBaseButton-primaryFormSubmit"]:active {
    border-color: $blue_dark;
    background: $blue_dark;
    color: #FFFFFF;
}

button[data-baseweb="tab"]:focus-visible {
    outline: 2px solid rgba(33, 150, 243, 0.5);
}

button[data-testid="stBaseButton-tertiary"] {
    min-height: 30px;
    border: none;
    background: transparent;
    color: $muted;
}

button[data-testid="stBaseButton-tertiary"]:hover {
    background: rgba(239, 68, 68, 0.12);
    color: #F87171;
}


/* Account menu */

[data-testid="stPopoverBody"],
[data-baseweb="popover"] > div {
    border: 1px solid $border;
    border-radius: 12px;
    background: $surface;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
}

.synapse-account {
    margin-bottom: 0.25rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid $border;
}

.synapse-account-label {
    color: $muted;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.synapse-account-name {
    margin-top: 0.3rem;
    color: $text;
    font-size: 0.95rem;
    font-weight: 600;
}

.synapse-account-email {
    color: $muted;
    font-size: 0.82rem;
    word-break: break-all;
}


/* Documents */

[data-testid="stExpander"] details {
    border: 1px solid $border;
    border-radius: 10px;
    background: $surface;
}

[data-testid="stExpander"] summary {
    padding: 0.5rem 0.75rem;
    color: $text;
    font-weight: 500;
}

[data-testid="stExpander"] summary:hover {
    color: $blue_bright;
}

[data-testid="stExpanderDetails"] {
    padding: 0 0.75rem 0.75rem;
}

[data-testid="stFileUploader"] label p {
    color: $muted;
    font-size: 0.78rem;
}

[data-testid="stFileUploaderDropzone"] {
    padding: 0;
    border: none;
    background: transparent;
}

[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploaderDropzone"] small {
    display: none;
}

[data-testid="stFileUploaderDropzone"] button {
    width: 100%;
}

[data-testid="stExpander"] [data-testid="stCaptionContainer"] p {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}


/* Conversation list */

section[data-testid="stSidebar"] [class*="st-key-conv_"] button {
    justify-content: flex-start !important;
    width: 100%;
    min-height: 38px;
    padding: 0.4rem 0.7rem;
    border: 1px solid rgba(38, 56, 79, 0.75);
    background: $surface;
    color: $muted;
    font-weight: 450;
    text-align: left;
}

section[data-testid="stSidebar"] [class*="st-key-conv_"] button > div {
    width: 100%;
}

section[data-testid="stSidebar"] [class*="st-key-conv_"] button * {
    justify-content: flex-start !important;
    text-align: left !important;
}

section[data-testid="stSidebar"] [class*="st-key-conv_"] button:hover {
    border-color: rgba(33, 150, 243, 0.5);
    background: $surface_raised;
    color: $text;
}

section[data-testid="stSidebar"] [class*="st-key-conv_"] button[data-testid="stBaseButton-primary"] {
    border-color: rgba(33, 150, 243, 0.65);
    background: rgba(33, 150, 243, 0.18);
    color: $text;
}

section[data-testid="stSidebar"] [class*="st-key-conv_"] button[data-testid="stBaseButton-primary"]:hover {
    border-color: $blue;
    background: rgba(33, 150, 243, 0.26);
}

section[data-testid="stSidebar"] [class*="st-key-conv_"] p {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}


/* Empty state */

.synapse-hero {
    max-width: 820px;
    margin: 6vh auto 1.5rem;
    padding: 2.4rem 2.6rem;
    border: 1px solid $border;
    border-radius: 22px;
    background:
        radial-gradient(
            circle at 92% 0%,
            rgba(33, 150, 243, 0.18),
            transparent 45%
        ),
        linear-gradient(
            145deg,
            rgba(17, 25, 35, 0.96),
            rgba(13, 22, 34, 0.96)
        );
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
}

.synapse-hero-eyebrow {
    margin-bottom: 0.7rem;
    color: $blue_bright;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.synapse-hero-title {
    margin: 0;
    padding: 0;
    color: $text;
    font-size: 2.7rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.synapse-hero-title span {
    color: $blue_bright;
}

.synapse-hero-subtitle {
    max-width: 600px;
    margin: 1rem 0 0;
    color: $muted;
    font-size: 1rem;
    line-height: 1.6;
}

.synapse-hero-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1.4rem;
}

.synapse-hero-chips span {
    padding: 0.3rem 0.8rem;
    border: 1px solid $border;
    border-radius: 999px;
    background: rgba(24, 35, 52, 0.7);
    color: $text;
    font-size: 0.8rem;
    font-weight: 500;
}


/* Chat messages */

[data-testid="stChatMessage"] {
    padding: 0.75rem 0.75rem;
    border: 1px solid transparent;
    border-radius: 14px;
    background: transparent;
}

[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="chatAvatarIcon-user"]
) {
    border-color: rgba(38, 56, 79, 0.8);
    background: rgba(24, 35, 52, 0.55);
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    line-height: 1.65;
}

[data-testid="stChatMessageAvatarUser"],
[data-testid="chatAvatarIcon-user"] {
    border: 1px solid $border;
    background: $surface_raised !important;
    color: $blue_bright !important;
}

[data-testid="stChatMessageAvatarAssistant"],
[data-testid="chatAvatarIcon-assistant"] {
    background: $blue !important;
    color: #FFFFFF !important;
}


/* Chat input */

[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    background: $background;
}

[data-testid="stChatInput"] {
    border: 1px solid $border !important;
    border-radius: 14px !important;
    background: $surface !important;
    box-shadow: none !important;
    transition: border-color 0.15s ease;
}

[data-testid="stChatInput"]:focus-within {
    border-color: rgba(33, 150, 243, 0.75) !important;
}

[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"] {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea {
    border: none !important;
    outline: none !important;
    background: transparent !important;
    box-shadow: none !important;
    color: $text;
    caret-color: $blue_bright;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: $muted;
}

[data-testid="stChatInputSubmitButton"] {
    border: none;
    border-radius: 10px;
    background: $blue;
    color: #FFFFFF;
}

[data-testid="stChatInputSubmitButton"]:hover:not(:disabled) {
    background: $blue_bright;
    color: #FFFFFF;
}

[data-testid="stChatInputSubmitButton"]:disabled {
    background: transparent;
    color: $muted;
    opacity: 0.6;
}


/* Authentication */

.st-key-auth {
    width: 100%;
    max-width: 460px;
    margin: 4rem auto 0;
}

.synapse-auth-brand {
    margin-bottom: 1.5rem;
    text-align: center;
}

.synapse-auth-title {
    color: $text;
    font-size: 2.2rem;
    font-weight: 750;
    line-height: 1.15;
}

.synapse-auth-title span {
    color: $blue_bright;
}

.synapse-auth-subtitle {
    margin-top: 0.55rem;
    color: $muted;
    font-size: 0.95rem;
}

[data-baseweb="tab-border"] {
    background-color: $border !important;
}

[data-baseweb="tab-highlight"] {
    background-color: $blue !important;
}

button[data-baseweb="tab"] p {
    color: $muted;
}

button[data-baseweb="tab"]:hover p,
button[data-baseweb="tab"][aria-selected="true"] p {
    color: $blue_bright !important;
}

[data-testid="stForm"] {
    padding: 1.4rem;
    border: 1px solid $border;
    border-radius: 14px;
    background: $surface;
}

[data-testid="stForm"] h3 {
    margin-bottom: 0.25rem;
    padding-top: 0;
    font-size: 1.3rem;
    font-weight: 650;
}


/* Text inputs */

[data-testid="stTextInputRootElement"] {
    border: 1px solid $border !important;
    border-radius: 9px !important;
    background: $background !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

[data-testid="stTextInputRootElement"]:hover {
    border-color: rgba(33, 150, 243, 0.5) !important;
}

[data-testid="stTextInputRootElement"]:focus-within {
    border-color: $blue !important;
    box-shadow: 0 0 0 1px rgba(33, 150, 243, 0.35) !important;
}

[data-testid="stTextInputRootElement"] input {
    border: none !important;
    outline: none !important;
    background: transparent !important;
    box-shadow: none !important;
    color: $text;
}

[data-testid="stTextInputRootElement"] input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0 1000px $background inset;
    -webkit-text-fill-color: $text;
}


/* Sources */

.synapse-sources {
    margin-top: 0.6rem;
    padding: 0.55rem 0.8rem;
    border: 1px solid $border;
    border-radius: 10px;
    background: rgba(17, 25, 35, 0.6);
}

.synapse-sources-title {
    margin-bottom: 0.25rem;
    color: $blue_bright;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.synapse-source {
    color: $muted;
    font-size: 0.82rem;
    line-height: 1.5;
}


/* Scrollbars */

[data-testid="stApp"] * {
    scrollbar-color: $border transparent;
    scrollbar-width: thin;
}


/* Small screens */

@media (max-width: 768px) {
    [data-testid="stMainBlockContainer"] {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .synapse-hero {
        margin-top: 3vh;
        padding: 1.6rem 1.25rem;
    }

    .synapse-hero-title {
        font-size: 2rem;
    }

    .st-key-auth {
        margin-top: 1.5rem;
    }
}
</style>
"""
).substitute(
    blue=BLUE,
    blue_bright=BLUE_BRIGHT,
    blue_dark=BLUE_DARK,
    background=BACKGROUND,
    surface=SURFACE,
    surface_raised=SURFACE_RAISED,
    sidebar=SIDEBAR,
    border=BORDER,
    text=TEXT,
    muted=MUTED,
)


def apply_theme():
    st.html(_THEME_CSS)


def render_brand():
    st.html('<div class="synapse-brand">Synapse<span>AI</span></div>')


def render_section_label(text):
    st.html(f'<div class="synapse-section-label">{escape(text)}</div>')


def render_account_card(username, email=None):
    email_html = (
        f'<div class="synapse-account-email">{escape(email)}</div>'
        if email
        else ""
    )

    st.html(
        f"""
        <div class="synapse-account">
            <div class="synapse-account-label">Signed in as</div>
            <div class="synapse-account-name">{escape(username)}</div>
            {email_html}
        </div>
        """
    )


def render_auth_header():
    st.html(
        """
        <div class="synapse-auth-brand">
            <div class="synapse-auth-title">Synapse<span>AI</span></div>
            <div class="synapse-auth-subtitle">
                Your AI assistant for conversations, knowledge and tools.
            </div>
        </div>
        """
    )


def render_hero():
    st.html(
        """
        <section class="synapse-hero">
            <div class="synapse-hero-eyebrow">
                LangChain · LangGraph · RAG
            </div>
            <h1 class="synapse-hero-title">
                Welcome to <span>SynapseAI</span>
            </h1>
            <p class="synapse-hero-subtitle">
                Ask questions, search your uploaded documents and get
                grounded answers with sources. Your conversations are
                saved across sessions.
            </p>
            <div class="synapse-hero-chips">
                <span>Document search</span>
                <span>Cited sources</span>
                <span>Saved history</span>
            </div>
        </section>
        """
    )


def render_sources(sources):
    if not sources:
        return

    items = []
    seen = set()

    for source in sources:
        raw_name = str(source.get("source", "Unknown source"))
        name = raw_name.replace("\\", "/").rsplit("/", 1)[-1] or "Unknown source"
        page = source.get("page")

        label = escape(name)

        if page is not None:
            label = f"{label} — page {escape(str(page))}"

        if label in seen:
            continue

        seen.add(label)
        items.append(f'<div class="synapse-source">• {label}</div>')

    st.html(
        f"""
        <div class="synapse-sources">
            <div class="synapse-sources-title">Sources</div>
            {"".join(items)}
        </div>
        """
    )