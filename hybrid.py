import json
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from memory import search as vector_search, chunks

# -----------------------------
# BM25 SETUP
# -----------------------------

tokenized = [c["text"].lower().split() for c in chunks]

bm25 = BM25Okapi(tokenized)

# -----------------------------
# CROSS ENCODER RERANKER
# -----------------------------

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# -----------------------------
# KEYWORD SEARCH
# -----------------------------

def keyword_search(question, k=5):
    """Top-k chunks using BM25 keyword search."""

    scores = bm25.get_scores(question.lower().split())

    top_ids = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:k]

    return [
        (chunks[i]["text"], chunks[i]["source"], scores[i])
        for i in top_ids
    ]


# -----------------------------
# HYBRID SEARCH (FAISS + BM25)
# -----------------------------

def hybrid_search(question, k=5):
    """Merge semantic search and keyword search using Reciprocal Rank Fusion."""

    vec = vector_search(question, k=10)

    key = keyword_search(question, k=10)

    points = {}

    # FAISS votes
    for rank, (text, source, _) in enumerate(vec):
        points[(text, source)] = (
            points.get((text, source), 0)
            + 1 / (60 + rank)
        )

    # BM25 votes
    for rank, (text, source, _) in enumerate(key):
        points[(text, source)] = (
            points.get((text, source), 0)
            + 1 / (60 + rank)
        )

    merged = sorted(
        points.items(),
        key=lambda kv: kv[1],
        reverse=True
    )[:k]

    return [
        (text, source, score)
        for (text, source), score in merged
    ]


# -----------------------------
# SMART SEARCH (RERANKER)
# -----------------------------

def smart_search(question, k=3):
    """Hybrid search followed by CrossEncoder reranking."""

    candidates = hybrid_search(question, k=10)

    pairs = [
        (question, text)
        for text, _, _ in candidates
    ]

    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        (text, source, float(score))
        for (text, source, _), score in ranked[:k]
    ]


# -----------------------------
# TEST
# -----------------------------

if __name__ == "__main__":

    question = input("Ask a question: ")

    results = smart_search(question)

    for text, source, score in results:

        print("\n" + "=" * 80)
        print(f"Score : {score:.4f}")
        print(f"Source: {source}")
        print()
        print(text[:400], "...")