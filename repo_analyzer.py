import os
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)
from langchain_core.prompts import ChatPromptTemplate


class GitHubRepoAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vector_store = None
        self.rag_chain = None

    def load_and_chunk_code(self):
        """
        Load source files from the repository
        and split them into semantic chunks.
        """

        print(f"Loading repository: {self.repo_path}")

        extensions = [
           "**/*.py",
           "**/*.js",
           "**/*.jsx",
           "**/*.ts",
           "**/*.tsx",

           "**/*.java",
           "**/*.cpp",
           "**/*.c",
           "**/*.cs",
           "**/*.go",
           "**/*.rs",

           "**/*.html",
           "**/*.css",

           "**/*.md",
           "**/README.md",

           "**/*.json",
           "**/*.yaml",
           "**/*.yml",

           "**/*.sql",
           "**/*.toml",

           "**/*.xml",

           "**/*.env.example",

           "**/*.sh",
           "**/*.bat",

           "**/Dockerfile",
           "**/*.dockerfile",
]

        ignore_dirs = {
            ".git",
            ".github",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            "dist",
            "build",
            ".next",
            "coverage",
        }

        documents = []

        for ext in extensions:

            loader = DirectoryLoader(
                self.repo_path,
                glob=ext,
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"},
                show_progress=False,
                silent_errors=True,
            )

            docs = loader.load()

            for doc in docs:

                source = doc.metadata.get("source", "")

                if any(folder in source for folder in ignore_dirs):
                    continue

                filename = os.path.basename(source)

                if filename.startswith("test_"):
                    continue

                doc.metadata["filename"] = filename

                doc.page_content = (
                    f"FILE: {filename}\n"
                    f"PATH: {source}\n\n"
                    f"{doc.page_content}"
                )

                documents.append(doc)

        if not documents:
            raise ValueError(
                "No supported source files were found."
            )

        print(f"Loaded {len(documents)} source files.")

        splitter = RecursiveCharacterTextSplitter(
            separators=[
                "\nclass ",
                "\ndef ",
                "\nasync def ",
                "\nfunction ",
                "\nexport ",
                "\nconst ",
                "\nlet ",
                "\n\n",
                "\n",
                " ",
                "",
            ],
            chunk_size=1000,
            chunk_overlap=150,
        )

        chunked_docs = splitter.split_documents(documents)

        print(f"Created {len(chunked_docs)} chunks.")

        return chunked_docs

    def build_vector_database(self, chunked_docs):
        """
        Build an in-memory Chroma vector database.
        """

        print("Building vector database...")

        self.vector_store = Chroma.from_documents(
            documents=chunked_docs,
            embedding=self.embeddings,
        )

        print("Vector database created successfully.")

        self._initialize_chain()

    def _initialize_chain(self):
        """
        Create the Retrieval-Augmented Generation chain.
        """

        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 25}
        )

        system_prompt ="""You are an expert Software Architect and Senior Software Engineer.

Your job is to explain a GitHub repository to another developer.

Use ONLY the retrieved repository context.

Never invent code or functionality.

If the repository contains README.md, package.json, requirements.txt, pyproject.toml, Dockerfile or similar project description files, use them together with the source code.

When answering:

1. Summarize the project purpose.

2. Mention important folders.

3. Mention important files.

4. Mention important classes.

5. Mention important functions.

6. Explain the backend architecture.

7. Explain the frontend architecture.

8. Explain authentication.

9. Explain database usage.

10. Explain API routes.

11. Explain Socket.IO/WebSocket communication.

12. Explain execution flow from user request to response.

13. Explain how different files interact.

14. Mention important libraries/frameworks.

15. Whenever possible, include exact filenames.

If some information is unavailable, explicitly say:

"The retrieved repository context does not contain this information."

Repository Context:



{context}
"""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(
            self.llm,
            prompt,
        )

        self.rag_chain = create_retrieval_chain(
            retriever,
            question_answer_chain,
        )

    def ask_question(self, question: str):
        """
        Ask a question about the repository.
        """

        if self.rag_chain is None:
            raise ValueError(
                "Repository has not been processed yet."
            )

        response = self.rag_chain.invoke(
            {
                "input": question,
            }
        )

        return response["answer"]