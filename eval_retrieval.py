import csv

from memory import search as vector_search
from hybrid import hybrid_search, smart_search


def evaluate(method_name, search_function):
    total = 0
    recall_at_1 = 0
    recall_at_3 = 0
    reciprocal_rank_sum = 0

    print("\n" + "=" * 80)
    print(method_name)
    print("=" * 80)

    with open("golden.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            question = row["question"]
            expected = row["correct_source"]

            results = search_function(question, k=3)

            sources = [source for _, source, _ in results]

            total += 1

            # Recall@1
            if len(sources) >= 1 and sources[0] == expected:
                recall_at_1 += 1

            # Recall@3
            if expected in sources:
                recall_at_3 += 1

                # Find the rank of the correct source
                rank = sources.index(expected) + 1

                # Reciprocal Rank
                reciprocal_rank_sum += 1 / rank

            else:
                print("\n❌ FAILED")
                print("Question:", question)
                print("Expected:", expected)
                print("Retrieved:")

                for _, source, score in results:
                    print(f"  {source} | score: {score:.4f}")

    r1 = (recall_at_1 / total) * 100
    r3 = (recall_at_3 / total) * 100
    mrr = reciprocal_rank_sum / total

    print(f"\nRecall@1: {r1:.1f}% ({recall_at_1}/{total})")
    print(f"Recall@3: {r3:.1f}% ({recall_at_3}/{total})")
    print(f"MRR:      {mrr:.3f}")


print("\nEvaluating retrieval...")


evaluate("Vector Search", vector_search)
evaluate("Hybrid Search", hybrid_search)
evaluate("Smart Search", smart_search)