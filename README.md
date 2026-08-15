RegRadar 🏦

RBI Regulatory Intelligence & Retrieval-Augmented Generation System

RegRadar is a Retrieval-Augmented Generation (RAG) system designed to answer questions from a collection of RBI regulatory documents. It retrieves relevant regulatory passages first and then uses an LLM to generate a grounded answer from the retrieved evidence.

Project Objective

RegRadar is designed to:

Search RBI regulatory documents

Retrieve relevant passages using semantic and keyword search

Combine multiple retrieval methods

Rerank retrieved passages using a CrossEncoder

Generate grounded answers using Gemini

Cite source documents for important claims

Refuse to answer when sufficient evidence is unavailable

Protect against common prompt-injection attempts

Evaluate retrieval quality using a 30-question golden dataset

Provide a Streamlit interface

Architecture

                  RBI Regulatory PDFs
                          │
                          ▼
                   PDF Text Extraction
                          │
                          ▼
                     Text Chunking
                          │
                          ▼
                      chunks.json
                          │
                 ┌────────┴────────┐
                 │                 │
                 ▼                 ▼
        FAISS Semantic Search   BM25 Keyword Search
                 │                 │
                 └────────┬────────┘
                          ▼
              Reciprocal Rank Fusion
                          │
                          ▼
                  Candidate Chunks
                          │
                          ▼
                  CrossEncoder Reranking
                          │
                          ▼
                   Top Evidence
                          │
                          ▼
                       Gemini
                          │
                    Grounded Answer

Retrieval Pipeline

1. Semantic Search

Document chunks are embedded using all-MiniLM-L6-v2 and stored in a FAISS index. This retrieves passages based on semantic similarity.

2. BM25 Keyword Search

BM25 provides keyword-based retrieval and is useful for exact regulatory terminology and phrases.

3. Hybrid Search

FAISS and BM25 results are combined using Reciprocal Rank Fusion (RRF), giving the system both semantic and exact-term retrieval signals.

4. CrossEncoder Reranking

The hybrid stage produces candidates. A CrossEncoder evaluates the question together with each candidate passage and reranks them by relevance.

Grounded Answer Generation

Gemini is the primary generation provider. The generation prompt instructs the model to:

Use only the retrieved regulatory evidence.

Avoid outside knowledge.

Avoid inventing unsupported facts.

Mention source documents after important claims.

Return an insufficient-context response when the evidence does not support an answer.

If Gemini is temporarily unavailable, Groq is used as a fallback.

Safety & Reliability

Prompt Injection Protection

RegRadar checks for common prompt-injection attempts such as:

ignore previous instructions
ignore all previous
ignore your instructions
reveal your prompt
show me your prompt
system prompt
developer prompt
jailbreak
override

Suspicious requests are rejected before normal answer generation.

Insufficient Context

When the retrieved evidence does not support a question, the system returns:

I don't have enough information in my documents.

This conservative behavior is important for regulatory QA.

Retrieval Evaluation

Retrieval quality was evaluated using a 30-question golden dataset with an expected source document for each question.

Method

Recall@1

Recall@3

MRR

Vector Search

36.67%

93.33%

0.6278

Hybrid Search

46.67%

100.00%

0.7222

Smart Search

53.33%

93.33%

0.7278

Hybrid Search achieved 100% Recall@3, meaning the correct source appeared within the top three retrieved results for all 30 evaluation questions.

Smart Search achieved the highest Recall@1 (53.33%) and MRR (0.7278).

Example

Question

What is cyber resilience?

Example RegRadar response

RegRadar retrieves relevant RBI passages and generates a grounded response such as:

Based on the provided RBI documents, Cyber Resilience is the ability of an organisation to continue to carry out its mission by anticipating and adapting to cyber threats and other relevant changes in the environment, and by withstanding, containing, and rapidly recovering from cyber incidents.

The response includes the relevant RBI source documents.

Streamlit UI

Run the interface locally:

streamlit run ui.py

Streamlit normally opens:

http://localhost:8501

Local Setup

Clone the repository

git clone https://github.com/haritaramesh1/regradar.git
cd regradar

Create and activate a virtual environment

python -m venv venv
venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

Environment Variables

Create a .env file locally:

GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=your_langfuse_host

Never commit .env to GitHub.

Retrieval Evaluation

Run:

python eval_retrieval.py

Evaluation output is stored in evaluation_results.json.

Terminal Application

Run:

python answer.py

Then enter a question such as:

What is cyber resilience?

Type exit to stop.

FastAPI Backend

Start the API locally:

python -m uvicorn app:app --host 0.0.0.0 --port 8000

Health check:

http://localhost:8000/health

Expected response:

{
  "status": "alive"
}

The question endpoint is:

POST /ask

Example request:

{
  "text": "What is cyber resilience?"
}

PowerShell example:

$body = @{ text = "What is cyber resilience?" } | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8000/ask" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

Project Structure

regradar/
│
├── app.py
├── ui.py
├── answer.py
├── memory.py
├── hybrid.py
├── eval_retrieval.py
├── ingest.py
│
├── chunks.json
├── regradar.index
├── golden.csv
├── evaluation_results.json
│
├── requirements.txt
├── .gitignore
└── README.md

Main Components

File

Purpose

ingest.py

Extracts and chunks PDF text

chunks.json

Stores processed document chunks

memory.py

FAISS semantic index and search

hybrid.py

BM25 + FAISS hybrid retrieval and CrossEncoder reranking

answer.py

Grounded generation, safety checks, and provider fallback

app.py

FastAPI backend

ui.py

Streamlit interface

eval_retrieval.py

Retrieval evaluation

golden.csv

30-question evaluation dataset

evaluation_results.json

Evaluation output

regradar.index

FAISS vector index

requirements.txt

Python dependencies

Design Decisions

Why Hybrid Retrieval?

Semantic retrieval is useful for understanding meaning, while BM25 is effective for exact terminology. Combining them is useful for regulatory documents.

Why CrossEncoder Reranking?

The initial retrieval stage gathers candidates, while the CrossEncoder performs a more detailed relevance comparison before generation.

Why Grounded Generation?

Regulatory questions require evidence. RegRadar instructs the generation model to answer only from retrieved regulatory documents.

Why Refuse Unsupported Questions?

A regulatory assistant should prefer an explicit insufficient-context response over an unsupported answer.

Current Project Status

The core RegRadar system has been implemented and tested locally, including:

PDF document processing

Text chunking

FAISS semantic retrieval

BM25 keyword retrieval

Reciprocal Rank Fusion

CrossEncoder reranking

Retrieval evaluation

Gemini answer generation

Groq fallback

Prompt-injection protection

Insufficient-context handling

FastAPI backend

Streamlit UI

Langfuse instrumentation

GitHub version control

Public deployment is intentionally not required for the final local version so the high-quality retrieval architecture can be preserved without reducing it to fit limited hosting resources.

Future Improvements

Page-level citations

Better document metadata filtering

Regulation/date filtering

Larger evaluation datasets

Automated CI evaluation

Improved evidence visualization

More RBI regulatory documents

Query rewriting

Retrieval latency optimization

Production deployment with sufficient compute resources

Technologies

Python

FAISS

Sentence Transformers

BM25

CrossEncoder

Gemini

Groq

FastAPI

Streamlit

Langfuse

Git/GitHub

Final Architecture

                    RBI PDFs
                       │
                       ▼
                  PDF Extraction
                       │
                       ▼
                 Text Chunking
                       │
                       ▼
                  chunks.json
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
           FAISS              BM25
       Semantic Search     Keyword Search
              │                 │
              └────────┬────────┘
                       ▼
                     RRF
                       │
                       ▼
                Candidate Chunks
                       │
                       ▼
                 CrossEncoder
                   Reranking
                       │
                       ▼
                  Top Evidence
                       │
                       ▼
                    Gemini
                       │
                       ▼
                Grounded Answer
                       │
                       ▼
                  Streamlit UI

Project Outcome

RegRadar demonstrates a complete Retrieval-Augmented Generation pipeline for regulatory intelligence.

The retrieval system was quantitatively evaluated using a 30-question golden dataset.

Hybrid Search: 100% Recall@3

Smart Search: 53.33% Recall@1 and 0.7278 MRR