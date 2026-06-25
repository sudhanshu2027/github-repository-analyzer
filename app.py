import os
import streamlit as st
from dotenv import load_dotenv

from repo_analyzer import GitHubRepoAnalyzer
from github_utils import clone_repository, delete_repository

# ---------------------------------------
# Load Environment Variables
# ---------------------------------------
load_dotenv()

# ---------------------------------------
# Page Configuration
# ---------------------------------------
st.set_page_config(
    page_title="GitHub Repository Analyzer",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 GitHub Repository Analyzer")

st.markdown(
    """
Analyze any **public GitHub repository** and ask natural language questions
about its architecture, classes, functions and execution flow.
"""
)

# ---------------------------------------
# Session State
# ---------------------------------------
if "analyzer" not in st.session_state:
    st.session_state.analyzer = None

if "processed" not in st.session_state:
    st.session_state.processed = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0

if "cloned_repo_path" not in st.session_state:
    st.session_state.cloned_repo_path = None
# ---------------------------------------
# Sidebar
# ---------------------------------------
with st.sidebar:

    st.header("⚙️ Configuration")

    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repository",
    )

    col1, col2 = st.columns(2)

    process_clicked = col1.button(
        "🚀 Analyze",
        use_container_width=True,
    )

    clear_clicked = col2.button(
        "🗑 Clear",
        use_container_width=True,
    )

    if clear_clicked:

        if st.session_state.cloned_repo_path:
            delete_repository(st.session_state.cloned_repo_path)

        st.session_state.chat_history = []
        st.session_state.analyzer = None
        st.session_state.processed = False
        st.session_state.chunk_count = 0
        st.session_state.cloned_repo_path = None

        st.rerun()

    if process_clicked:

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:

            st.error("GROQ_API_KEY not found in your .env file.")

        elif not repo_url:

            st.error("Please enter a GitHub repository URL.")

        elif not repo_url.startswith("https://github.com/"):

            st.error("Please enter a valid GitHub repository URL.")

        else:

            repo_path = None

            try:

                with st.spinner("Cloning repository..."):

                    repo_path = clone_repository(repo_url)
                    st.session_state.cloned_repo_path = repo_path

                with st.spinner("Analyzing repository..."):

                    analyzer = GitHubRepoAnalyzer(repo_path)

                    chunks = analyzer.load_and_chunk_code()

                    analyzer.build_vector_database(chunks)

                

                st.session_state.analyzer = analyzer
                st.session_state.processed = True
                st.session_state.chat_history = []
                st.session_state.chunk_count = len(chunks)

                st.success("Repository analyzed successfully!")

            except Exception as e:

                if repo_path is not None:
                    delete_repository(repo_path)
                st.session_state.cloned_repo_path = None
                st.exception(e)

# ---------------------------------------
# Main Area
# ---------------------------------------
if st.session_state.processed:

    st.success(
        f"✅ Repository indexed successfully! ({st.session_state.chunk_count} code chunks)"
    )

    st.divider()

    st.subheader("💬 Ask Questions About Your Repository")

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    question = st.chat_input(
        "Example: Explain the authentication flow..."
    )

    if question:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):

            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    answer = st.session_state.analyzer.ask_question(
                        question
                    )

                    st.markdown(answer)

                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                except Exception as e:

                    st.exception(e)

else:

    st.info(
        """
### 👋 Welcome

**Getting Started**

1. Paste a public GitHub repository URL.

2. Click **🚀 Analyze**.

3. Wait while the repository is analyzed.

4. Ask questions such as:

- Explain the project architecture.
- Which files handle database operations?
- Describe the execution flow.
"""
    )