import os

from dotenv import load_dotenv
from google import genai

from hybrid import smart_search

# Load API key
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

    if is_suspicious(question):
        return "This request appears to be attempting to override system instructions. I can't process it."

    results = smart_search(question, k=3)

    if len(results) == 0:
        return "I don't have enough information in my documents."

    if results[0][2] < CONFIDENCE_FLOOR:
        return "I don't have enough information in my documents."

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=build_prompt(question, results),
    )

    answer = response.text

    if "INSUFFICIENT_CONTEXT" in answer:
        return "I don't have enough information in my documents."

    return answer


if __name__ == "__main__":

    print("=" * 80)
    print("RegRadar")
    print("=" * 80)

    while True:

        question = input("\nAsk a question (type 'exit' to quit): ")

        if question.lower() == "exit":
            break

        print("\nThinking...\n")

        answer = ask(question)

        print(answer)