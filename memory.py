import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


# ============================================================
# GLOBALS
# ============================================================

model = None
chunks = None
texts = None
index = None


# ============================================================
# LAZY LOADING
# ============================================================

def load_memory():

    global model, chunks, texts, index

    if model is not None:
        return

    print("Loading RegRadar retrieval system...")

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Loading chunks...")
    with open("chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [c["text"] for c in chunks]

    print("Loading FAISS index...")
    index = faiss.read_index("regradar.index")

    print("Retrieval system ready.")


# ============================================================
# BUILD FAISS INDEX
# ============================================================

def build_memory():

    load_memory()

    print("Creating embeddings...")

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    new_index = faiss.IndexFlatIP(384)

    new_index.add(np.array(vectors))

    faiss.write_index(
        new_index,
        "regradar.index"
    )

    print(
        "Memory built:",
        new_index.ntotal,
        "chunks indexed"
    )


# ============================================================
# SEARCH
# ============================================================

def search(question, k=5):

    load_memory()

    q_vec = model.encode(
        [question],
        normalize_embeddings=True
    )

    scores, ids = index.search(
        np.array(q_vec),
        k
    )

    results = []

    for i, score in zip(ids[0], scores[0]):

        if i < 0:
            continue

        results.append(
            (
                chunks[i]["text"],
                chunks[i]["source"],
                float(score)
            )
        )

    return results


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    build_memory()

    print("\nTesting search...\n")

    results = search(
        "What are the KYC requirements?"
    )

    for text, source, score in results:

        print(
            f"\nScore: {score:.4f}"
        )

        print(source)

        print(text[:250])