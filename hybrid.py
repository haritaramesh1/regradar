import json
from rank_bm25 import BM25Okapi

# --------------------------------------------------
# LOAD CHUNKS
# --------------------------------------------------

with open("chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

if not isinstance(chunks, list):
    chunks = []

# --------------------------------------------------
# BM25 SEARCH
# --------------------------------------------------

tokenized = [
    chunk.get("text", "").lower().split()
    for chunk in chunks
]

bm25 = BM25Okapi(tokenized) if tokenized else None


def smart_search(question, k=3):

    if not chunks or bm25 is None:
        return []

    scores = bm25.get_scores(
        question.lower().split()
    )

    top_ids = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:k]

    max_score = max(scores) if len(scores) else 0

    results = []

    for i in top_ids:

        if max_score > 0:
            confidence = float(scores[i] / max_score)
        else:
            confidence = 0.0

        results.append(
            (
                chunks[i].get("text", ""),
                chunks[i].get("source", "Unknown"),
                confidence
            )
        )

    return results


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    question = input("Ask a question: ")

    results = smart_search(question)

    for text, source, score in results:

        print("\n" + "=" * 80)
        print(f"Score : {score:.4f}")
        print(f"Source: {source}")
        print()
        print(text[:400])