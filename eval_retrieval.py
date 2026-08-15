import csv

from dotenv import load_dotenv
from langfuse import get_client

from memory import search as vector_search
from hybrid import hybrid_search, smart_search


# Load environment variables from .env
load_dotenv()


# Initialize Langfuse after loading the environment
langfuse = get_client()


# ============================================================
# RETRIEVAL EVALUATION
# ============================================================

def evaluate(method_name, search_function):

    # Create an active Langfuse trace for this evaluation method.
    with langfuse.start_as_current_observation(
        as_type="evaluator",
        name=f"{method_name} Evaluation",
    ) as trace:

        total = 0
        recall_at_1 = 0
        recall_at_3 = 0
        reciprocal_rank_sum = 0.0

        print("\n" + "=" * 80)
        print(method_name)
        print("=" * 80)

        with open(
            "golden.csv",
            newline="",
            encoding="utf-8"
        ) as f:

            reader = csv.DictReader(f)

            for row in reader:

                question = row["question"]
                expected = row["correct_source"]

                results = search_function(
                    question,
                    k=3
                )

                sources = [
                    source
                    for _, source, _ in results
                ]

                total += 1

                # ------------------------------------------------
                # Recall@1
                # ------------------------------------------------

                if (
                    len(sources) >= 1
                    and sources[0] == expected
                ):

                    recall_at_1 += 1


                # ------------------------------------------------
                # Recall@3 + Reciprocal Rank
                # ------------------------------------------------

                if expected in sources:

                    recall_at_3 += 1

                    rank = sources.index(expected) + 1

                    reciprocal_rank_sum += 1 / rank

                else:

                    print(
                        f"\nMISS: {question}"
                    )

                    print(
                        f"Expected source: {expected}"
                    )

                    print(
                        f"Retrieved sources: {sources}"
                    )


        # ========================================================
        # CALCULATE METRICS
        # ========================================================

        if total > 0:

            recall_1 = recall_at_1 / total
            recall_3 = recall_at_3 / total
            mrr = reciprocal_rank_sum / total

        else:

            recall_1 = 0.0
            recall_3 = 0.0
            mrr = 0.0


        # ========================================================
        # PRINT RESULTS
        # ========================================================

        print("\nResults:")
        print("-" * 80)

        print(
            f"Total questions : {total}"
        )

        print(
            f"Recall@1        : {recall_1:.4f}"
        )

        print(
            f"Recall@3        : {recall_3:.4f}"
        )

        print(
            f"MRR             : {mrr:.4f}"
        )


        # ========================================================
        # UPDATE LANGFUSE TRACE
        # ========================================================

        trace.update(
            output={
                "method": method_name,
                "total_questions": total,
                "recall_at_1": recall_1,
                "recall_at_3": recall_3,
                "mrr": mrr,
            }
        )


        # ========================================================
        # CREATE LANGFUSE SCORES
        # ========================================================

        trace.score_trace(
            name="recall_at_1",
            value=float(recall_1),
            data_type="NUMERIC",
            comment=method_name,
        )

        trace.score_trace(
            name="recall_at_3",
            value=float(recall_3),
            data_type="NUMERIC",
            comment=method_name,
        )

        trace.score_trace(
            name="mrr",
            value=float(mrr),
            data_type="NUMERIC",
            comment=method_name,
        )


        # ========================================================
        # RETURN METRICS
        # ========================================================

        return {
            "method": method_name,
            "total": total,
            "recall_at_1": recall_1,
            "recall_at_3": recall_3,
            "mrr": mrr,
        }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 80)
    print("RegRadar Retrieval Evaluation")
    print("=" * 80)


    # ========================================================
    # VECTOR SEARCH
    # ========================================================

    vector_metrics = evaluate(
        "Vector Search",
        vector_search
    )


    # ========================================================
    # HYBRID SEARCH
    # ========================================================

    hybrid_metrics = evaluate(
        "Hybrid Search",
        hybrid_search
    )


    # ========================================================
    # SMART SEARCH
    # ========================================================

    smart_metrics = evaluate(
        "Smart Search",
        smart_search
    )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n")
    print("=" * 80)
    print("FINAL RETRIEVAL EVALUATION")
    print("=" * 80)

    print(
        f"\n{'Method':<20}"
        f"{'Recall@1':<15}"
        f"{'Recall@3':<15}"
        f"{'MRR':<15}"
    )

    print("-" * 65)

    for metrics in [
        vector_metrics,
        hybrid_metrics,
        smart_metrics,
    ]:

        print(
            f"{metrics['method']:<20}"
            f"{metrics['recall_at_1']:<15.4f}"
            f"{metrics['recall_at_3']:<15.4f}"
            f"{metrics['mrr']:<15.4f}"
        )


    # ========================================================
    # FLUSH LANGFUSE
    # ========================================================

    langfuse.flush()