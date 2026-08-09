import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

chunks = json.load(open("chunks.json", encoding="utf-8"))
texts = [c["text"] for c in chunks]

vectors = model.encode(
    texts,
    normalize_embeddings=True,
    show_progress_bar=True
)

index = faiss.IndexFlatIP(384)
index.add(np.array(vectors))

faiss.write_index(index, "regradar.index")

print("Memory built:", index.ntotal, "chunks indexed")


def search(question, k=5):
    q_vec = model.encode(
        [question],
        normalize_embeddings=True
    )

    scores, ids = index.search(np.array(q_vec), k)

    return [
        (
            chunks[i]["text"],
            chunks[i]["source"],
            float(score)
        )
        for i, score in zip(ids[0], scores[0])
    ]


if __name__ == "__main__":

    for text, source, score in search(
        "What are the KYC requirements?"
    ):
        print(f"\n[{score:.2f}] {source}")
        print(text[:200], "...")