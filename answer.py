import os
import time

from dotenv import load_dotenv
from google import genai

from hybrid import smart_search


# Load API key from .env
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# If reranker confidence is below this,
# don't let the model answer.
CONFIDENCE_FLOOR = 0.30


def is_suspicious(question):
    question = question.lower()

    blocked = [
        "ignore previous",
        "ignore all previous",
        "ignore your instructions",
        "forget your instructions",
        "system prompt",
        "developer prompt",
        "reveal your prompt",
        "show me your prompt",
        "act as",
        "pretend to be",
        "jailbreak",
        "bypass",
        "override",
    ]

    return any(phrase in question for phrase in blocked)


def build_prompt(question, results):

    evidence = ""

    for text, source, score in results:
        evidence += f"\n\n[Source: {source}]\n{text}"

    prompt = f"""
You are RegRadar.

You answer ONLY using the RBI documents below.

Rules:

1. Use ONLY the information provided in the Sources section.
2. Never use outside knowledge.
3. If the answer is not supported by the sources, reply exactly:
INSUFFICIENT_CONTEXT
4. Keep the answer under 250 words.
5. Use bullet points where appropriate.
6. Mention the source after every important statement.
7. Do not invent or assume facts.

Sources:

{evidence}

Question:
{question}
"""

    return prompt


def ask(question):

    # ---------------------------------
    # 1. Check for prompt injection
    # ---------------------------------

    if is_suspicious(question):
        return (
            "This request appears to be attempting to override "
            "system instructions. I can't process it."
        )

    # ---------------------------------
    # 2. Retrieve relevant documents
    # ---------------------------------

    results = smart_search(question, k=3)

    if len(results) == 0:
        return "I don't have enough information in my documents."

    # ---------------------------------
    # 3. Check retrieval confidence
    # ---------------------------------

    if results[0][2] < CONFIDENCE_FLOOR:
        return "I don't have enough information in my documents."

    # ---------------------------------
    # 4. Ask Gemini
    # ---------------------------------

    response = None

    for attempt in range(3):

        try:

            print(
                f"Generating answer... "
                f"(attempt {attempt + 1}/3)"
            )

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=build_prompt(question, results),
            )

            # If successful, stop retrying
            break

        except Exception as e:

            print(
                f"Gemini temporarily unavailable: {e}"
            )

            # If this was the final attempt,
            # return a friendly error instead of crashing.
            if attempt == 2:
                return (
                    "Gemini is temporarily unavailable. "
                    "Please try again in a moment."
                )

            # Wait before trying again
            print("Retrying in 3 seconds...")
            time.sleep(3)

    # ---------------------------------
    # 5. Read Gemini response
    # ---------------------------------

    answer = response.text

    # ---------------------------------
    # 6. Handle insufficient context
    # ---------------------------------

    if "INSUFFICIENT_CONTEXT" in answer:
        return "I don't have enough information in my documents."

    # ---------------------------------
    # 7. Return final answer
    # ---------------------------------

    return answer


if __name__ == "__main__":

    print("=" * 80)
    print("RegRadar")
    print("=" * 80)

    while True:

        question = input(
            "\nAsk a question (type 'exit' to quit): "
        )

        if question.lower() == "exit":
            break

        print("\nThinking...\n")

        answer = ask(question)

        print(answer)