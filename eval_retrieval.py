import csv

from memory import search as vector_search
from hybrid import hybrid_search, smart_search


def evaluate(method_name, search_function):
    total = 0
    correct = 0

    with open("golden.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            question = row["question"]
            expected = row["correct_source"]

            results = search_function(question, k=3)

            sources = [source for _, source, _ in results]

            if expected in sources:
                correct += 1

            total += 1

    accuracy = (correct / total) * 100

    print(f"{method_name}: {accuracy:.1f}% ({correct}/{total})")


print("\nEvaluating retrieval...\n")

evaluate("Vector Search", vector_search)
evaluate("Hybrid Search", hybrid_search)
evaluate("Smart Search", smart_search)