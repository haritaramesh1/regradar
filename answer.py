import os
import time

from dotenv import load_dotenv
from google import genai
from groq import Groq
from langfuse import observe, get_client

from hybrid import smart_search


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

langfuse = get_client()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ============================================================
# AI CLIENTS
# ============================================================

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)

groq_client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# CONFIDENCE THRESHOLD
# ============================================================

CONFIDENCE_FLOOR = 0.30


# ============================================================
# PROMPT-INJECTION PROTECTION
# ============================================================

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

    return any(
        phrase in question
        for phrase in blocked
    )


# ============================================================
# RETRIEVAL
# ============================================================

@observe(as_type="retriever")
def retrieve_documents(question):

    results = smart_search(
        question,
        k=3
    )

    return results


# ============================================================
# BUILD GROUNDED PROMPT
# ============================================================

@observe(as_type="chain")
def build_prompt(question, results):

    evidence = ""

    for text, source, score in results:

        evidence += (
            f"\n\n"
            f"[Source: {source}]\n"
            f"{text}"
        )

    prompt = f"""
You are RegRadar.

You answer ONLY using the RBI documents provided below.

Rules:

1. Use ONLY information from the Sources section.
2. Never use outside knowledge.
3. Do not invent or assume facts.
4. If the answer is not supported by the sources, reply exactly:
INSUFFICIENT_CONTEXT
5. Keep the answer under 250 words.
6. Use bullet points where appropriate.
7. Mention the source after important statements.

Sources:

{evidence}

Question:

{question}
"""

    return prompt


# ============================================================
# GEMINI
# ============================================================

@observe(as_type="generation")
def ask_gemini(prompt):

    response = gemini_client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt,
    )

    return response.text


# ============================================================
# GROQ FALLBACK
# ============================================================

@observe(as_type="generation")
def ask_groq(prompt):

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    return response.choices[0].message.content


# ============================================================
# MAIN ASK FUNCTION
# ============================================================

@observe()
def ask(question):

    # --------------------------------------------------------
    # Check for prompt injection
    # --------------------------------------------------------

    if is_suspicious(question):

        return (
            "This request appears to be attempting "
            "to override system instructions. "
            "I can't process it."
        )


    # --------------------------------------------------------
    # Retrieve relevant documents
    # --------------------------------------------------------

    results = retrieve_documents(
        question
    )


    # --------------------------------------------------------
    # No results
    # --------------------------------------------------------

    if len(results) == 0:

        return (
            "I don't have enough information "
            "in my documents."
        )


    # --------------------------------------------------------
    # Confidence check
    # --------------------------------------------------------

    if results[0][2] < CONFIDENCE_FLOOR:

        return (
            "I don't have enough information "
            "in my documents."
        )


    # --------------------------------------------------------
    # Build grounded prompt
    # --------------------------------------------------------

    prompt = build_prompt(
        question,
        results
    )


    # ========================================================
    # GEMINI FIRST
    # ========================================================

    for attempt in range(3):

        try:

            print(
                f"Generating answer with Gemini "
                f"(attempt {attempt + 1}/3)..."
            )

            answer = ask_gemini(prompt)

            if "INSUFFICIENT_CONTEXT" in answer:

                return (
                    "I don't have enough information "
                    "in my documents."
                )

            return answer

        except Exception as error:

            print(
                f"Gemini temporarily unavailable: {error}"
            )

            if attempt < 2:

                print(
                    "Retrying in 3 seconds..."
                )

                time.sleep(3)


    # ========================================================
    # GEMINI FAILED → GROQ FALLBACK
    # ========================================================

    print(
        "Gemini failed after 3 attempts."
    )

    print(
        "Falling back to Groq..."
    )


    try:

        answer = ask_groq(prompt)

        if "INSUFFICIENT_CONTEXT" in answer:

            return (
                "I don't have enough information "
                "in my documents."
            )

        return answer


    except Exception as error:

        print(
            f"Groq temporarily unavailable: {error}"
        )

        return (
            "Both AI providers are temporarily "
            "unavailable. Please try again later."
        )


# ============================================================
# TERMINAL TEST
# ============================================================

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

        print(
            "\nThinking...\n"
        )

        answer = ask(question)

        print(answer)


    # --------------------------------------------------------
    # Ensure buffered Langfuse events are sent
    # --------------------------------------------------------

    langfuse.flush()