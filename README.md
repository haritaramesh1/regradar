# 🛡️ RegRadar

### RBI Regulatory Intelligence Assistant

RegRadar is a Retrieval-Augmented Generation (RAG) application that allows users to ask questions about RBI cybersecurity and regulatory requirements using a collection of RBI regulatory documents.

Instead of relying on general web knowledge, RegRadar retrieves relevant passages from the provided regulatory documents and uses them as evidence for generating answers.

---

## ✨ Features

- 🔎 Semantic vector search using FAISS
- 🔤 Keyword retrieval using BM25
- 🔀 Hybrid retrieval using Reciprocal Rank Fusion (RRF)
- 🧠 Cross-encoder reranking
- 🤖 Gemini-powered answer generation
- 📚 Source-aware answers
- 🛡️ Prompt-injection detection
- 🚫 Refuses to answer when relevant document context is unavailable
- 📊 Retrieval evaluation using Recall@1, Recall@3 and MRR
- 🌑 Dark Streamlit interface
- 🔐 Environment variables for API keys

---

## 🧠 How RegRadar Works

RegRadar follows a multi-stage RAG pipeline:

```text
                    User Question
                         │
                         ▼
                ┌─────────────────┐
                │  Query Handling │
                └────────┬────────┘
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      ┌──────────────┐       ┌──────────────┐
      │ Vector Search│       │  BM25 Search │
      │    FAISS     │       │   Keywords   │
      └──────┬───────┘       └──────┬───────┘
             │                      │
             └──────────┬───────────┘
                        ▼
              ┌───────────────────┐
              │   Hybrid Search   │
              │       RRF         │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Cross-Encoder     │
              │    Reranking      │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Relevant Evidence │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Gemini Generation  │
              └─────────┬─────────┘
                        │
                        ▼
                    Final Answer
````

---

## 🔍 Retrieval Pipeline

### 1. Vector Search

RegRadar converts document chunks into embeddings and stores them in a FAISS index.

This allows semantically similar passages to be retrieved even when the user's wording does not exactly match the wording in the document.

### 2. BM25 Search

BM25 provides traditional keyword-based retrieval.

This is useful when a question contains important regulatory terminology, acronyms, or exact phrases.

### 3. Hybrid Search

The vector and BM25 results are combined using Reciprocal Rank Fusion (RRF).

This allows RegRadar to benefit from both:

* semantic similarity
* exact keyword matching

### 4. Cross-Encoder Reranking

The retrieved candidates are passed through a cross-encoder model to determine which passages are most relevant to the question.

The highest-ranked passages are then provided to the language model.

### 5. Grounded Generation

Gemini receives the retrieved evidence and is instructed to answer only from that evidence.

If the documents do not contain enough information, RegRadar returns:

```text
I don't have enough information in my documents.
```

---

## 📊 Retrieval Evaluation

RegRadar includes a golden evaluation dataset containing questions and their expected source documents.

The retrieval system is evaluated using:

| Metric   | Description                                           |
| -------- | ----------------------------------------------------- |
| Recall@1 | Whether the correct document appears first            |
| Recall@3 | Whether the correct document appears in the top three |
| MRR      | Measures how highly the correct document is ranked    |

### Current Results

Based on the current 30-question evaluation set:

| Search Method | Recall@1 |   Recall@3 |   MRR |
| ------------- | -------: | ---------: | ----: |
| Vector Search |    36.7% |      93.3% | 0.628 |
| Hybrid Search |    46.7% | **100.0%** | 0.722 |
| Smart Search  |    53.3% |      93.3% | 0.728 |

Hybrid retrieval successfully placed the expected document within the top three results for all 30 evaluation questions.

---

## 🛡️ Security

RegRadar includes basic protection against prompt-injection attempts.

Requests containing phrases such as:

```text
ignore previous instructions
ignore all previous
system prompt
developer prompt
reveal your prompt
show me your prompt
jailbreak
bypass
override
```

are rejected before being sent to the language model.

RegRadar also prevents unsupported questions from being answered using outside knowledge.

For example:

```text
What is the capital of France?
```

should return:

```text
I don't have enough information in my documents.
```

---

## 🖥️ User Interface

The application is built with Streamlit and provides:

* Dark cybersecurity-inspired interface
* RegRadar branding
* Question input
* AI-generated answers
* Retrieved document sources
* Grounding indicator
* Example questions

---

## 🧰 Tech Stack

### Python

Core application language.

### FAISS

Used for vector similarity search.

### Sentence Transformers

Used for generating document and query embeddings.

### BM25

Used for keyword-based retrieval.

### Cross-Encoder

Used to rerank retrieved candidates.

### Google Gemini

Used to generate the final grounded answer.

### Streamlit

Used for the web interface.

### Git / GitHub

Used for version control and project hosting.

---

## 📁 Project Structure

```text
regradar/
│
├── app.py
├── answer.py
├── hybrid.py
├── memory.py
├── eval_retrieval.py
├── golden.csv
├── README.md
├── .gitignore
│
├── chunks.json
├── faiss.index
│
└── data/
    └── RBI regulatory documents
```

> Generated indexes, chunks, and document files may vary depending on the local dataset setup.

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/haritaramesh1/regradar.git
```

### 2. Enter the project

```bash
cd regradar
```

### 3. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

### 4. Activate the environment

```powershell
venv\Scripts\activate
```

### 5. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project directory:

```text
GEMINI_API_KEY=your_api_key_here
```

The `.env` file is intentionally excluded from Git using `.gitignore`.

Never commit API keys or other secrets to the repository.

---

## 🚀 Running RegRadar

Start the Streamlit application with:

```powershell
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

---

## 🧪 Running Retrieval Evaluation

To evaluate the retrieval pipeline:

```powershell
python eval_retrieval.py
```

The evaluator reports:

```text
Recall@1
Recall@3
MRR
```

for the configured evaluation dataset.

---

## 💬 Example Questions

Try asking:

```text
What is cyber resilience?
```

```text
What are the responsibilities of the Board regarding cybersecurity?
```

```text
What is a Cyber Crisis Management Plan?
```

```text
What are the four aspects of a Cyber Crisis Management Plan?
```

```text
What is risk-based transaction monitoring?
```

```text
What is device binding?
```

---

## 🎯 Project Goal

The goal of RegRadar is to demonstrate how a RAG system can be designed for regulatory information retrieval while reducing unsupported answers through:

1. Multiple retrieval strategies
2. Reranking
3. Grounded generation
4. Source attribution
5. Retrieval evaluation
6. Basic prompt-injection protection

---

## 🔮 Future Improvements

Potential future improvements include:

* Better document chunking
* Metadata-aware retrieval
* Improved source highlighting
* More extensive evaluation datasets
* Query rewriting
* Conversation history
* Document upload functionality
* Authentication
* Cloud deployment
* Improved citation precision
* Automated retrieval evaluation during CI/CD

---

## 👩‍💻 Author

**Harita Ramesh**

Built as an exploration of Retrieval-Augmented Generation, information retrieval, regulatory intelligence, and AI application development.

---

## 📜 Disclaimer

RegRadar is an experimental regulatory information retrieval tool.

It is not a substitute for official RBI publications, professional legal/compliance advice, or an organisation's internal regulatory interpretation.

