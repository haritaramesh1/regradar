import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


print("Loading chunks...")
with open("chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)


texts = [c["text"] for c in chunks]


# ============================================================
# BUILD FAISS INDEX
# ============================================================

def build_memory():

    print("Creating embeddings...")

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    index = faiss.IndexFlatIP(384)

    index.add(np.array(vectors))

    faiss.write_index(
        index,
        "regradar.index"
    )

    print(
        "Memory built:",
        index.ntotal,
        "chunks indexed"
    )


# ============================================================
# LOAD EXISTING INDEX
# ============================================================

print("Loading FAISS index...")

index = faiss.read_index(
    "regradar.index"
)


# ============================================================
# SEARCH
# ============================================================

def search(question, k=5):

    q_vec = model.encode(
        [question],
        normalize_embeddings=True
    )

    scores, ids = index.search(
        np.array(q_vec),
        k
    )

    return [
        (
            chunks[i]["text"],
            chunks[i]["source"],
            float(score)
        )
        for i, score in zip(ids[0], scores[0])
    ]


# ============================================================
# BUILD INDEX ONLY WHEN RUN DIRECTLY
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