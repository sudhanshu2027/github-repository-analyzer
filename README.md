# 🤖 GitHub Repository Analyzer

A Retrieval-Augmented Generation (RAG) application that analyzes any **public GitHub repository** and answers natural language questions about its architecture, execution flow, source code, APIs, authentication, and database.

## 🚀 Features

- Analyze any public GitHub repository using its URL
- Automatic repository cloning
- Semantic code chunking
- In-memory Chroma vector database
- Natural language Q&A using Groq LLM
- Explains:
  - Project architecture
  - Folder structure
  - Execution flow
  - API routes
  - Authentication flow
  - Database usage
  - Socket communication
  - Frontend–Backend interaction

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **LLM:** Groq (`llama-3.3-70b-versatile`)
- **Embeddings:** Gemini Embeddings (`gemini-embedding-001`)
- **Vector Database:** ChromaDB
- **Framework:** LangChain
- **Git Operations:** GitPython

---

## 📂 Project Structure

```
github_repo_analyzer/
│── app.py
│── repo_analyzer.py
│── github_utils.py
│── requirements.txt
│── .env
└── README.md
```

---
---
Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=groq_api_key
GOOGLE_API_KEY=gemini_api_key
```

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

---

## 💡 How to Use

1. Enter the URL of a public GitHub repository.
2. Click **Analyze**.
3. Wait for the repository to be indexed.
4. Ask questions such as:
   - Explain the project architecture.
   - Describe the execution flow.
   - How does authentication work?
   - Which files handle API routes?
   - Explain the database schema.
   - Explain the frontend and backend interaction.

---

## 📌 Example Repository

```
https://github.com/username/repository
```

---



