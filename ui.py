import re
import streamlit as st

import requests

API_URL = "http://127.0.0.1:8000"
from hybrid import smart_search


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="RegRadar",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SESSION STATE
# ============================================================

if "question" not in st.session_state:
    st.session_state.question = ""

if "answer" not in st.session_state:
    st.session_state.answer = None

if "sources" not in st.session_state:
    st.session_state.sources = []


# ============================================================
# CUSTOM CSS
# ============================================================

st.html(
    """
    <style>

    /* ======================================================
       MAIN PAGE
       ====================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 50% -15%,
                rgba(37, 99, 235, 0.20),
                transparent 35%
            ),
            radial-gradient(
                circle at 95% 35%,
                rgba(124, 58, 237, 0.12),
                transparent 30%
            ),
            #030712;

        color: #f8fafc;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }


    /* ======================================================
       HEADER
       ====================================================== */

    .regradar-hero {
        text-align: center;
        padding: 30px 0 35px 0;
    }

    .regradar-shield {
        font-size: 64px;
        line-height: 1;

        filter:
            drop-shadow(0 0 15px rgba(59,130,246,.7))
            drop-shadow(0 0 35px rgba(124,58,237,.35));

        margin-bottom: 18px;
    }

    .regradar-title {
        font-size: 64px;
        font-weight: 850;
        letter-spacing: -4px;
        line-height: 1;
        margin: 0;
    }

    .regradar-reg {
        color: #f8fafc;
    }

    .regradar-radar {
        background: linear-gradient(
            90deg,
            #38bdf8,
            #3b82f6,
            #8b5cf6
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .regradar-subtitle {
        margin-top: 16px;
        color: #94a3b8;
        font-size: 17px;
    }

    .regradar-status {
        display: inline-block;

        margin-top: 18px;
        padding: 8px 16px;

        border-radius: 999px;

        color: #4ade80;

        background: rgba(34,197,94,.07);

        border: 1px solid rgba(34,197,94,.20);

        font-size: 13px;
    }


    /* ======================================================
       DIVIDER
       ====================================================== */

    .regradar-divider {
        height: 1px;

        margin: 5px 0 30px 0;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(59,130,246,.35),
                rgba(124,58,237,.35),
                transparent
            );
    }


    /* ======================================================
       QUESTION CARD
       ====================================================== */

    .question-card {
        background:
            linear-gradient(
                145deg,
                rgba(15,23,42,.95),
                rgba(8,15,30,.95)
            );

        border: 1px solid rgba(71,85,105,.40);

        border-radius: 20px;

        padding: 24px;

        box-shadow:
            0 20px 60px rgba(0,0,0,.35),
            inset 0 1px 0 rgba(255,255,255,.025);
    }

    .question-label {
        color: #e2e8f0;

        font-size: 16px;
        font-weight: 700;

        margin-bottom: 12px;
    }

    .question-icon {
        color: #38bdf8;
        margin-right: 7px;
    }


    /* ======================================================
       STREAMLIT TEXT AREA
       ====================================================== */

    textarea {
        background: #080f1c !important;

        color: #f8fafc !important;

        border: 1px solid #263449 !important;

        border-radius: 13px !important;

        font-size: 16px !important;

        line-height: 1.5 !important;
    }

    textarea:focus {
        border-color: #3b82f6 !important;

        box-shadow:
            0 0 0 1px #3b82f6,
            0 0 30px rgba(59,130,246,.12) !important;
    }


    /* ======================================================
       ASK BUTTON
       ====================================================== */

    .stButton > button {
        background:
            linear-gradient(
                90deg,
                #0ea5e9,
                #3b82f6,
                #7c3aed
            ) !important;

        color: white !important;

        border: none !important;

        border-radius: 11px !important;

        font-weight: 750 !important;

        padding: 0.65rem 1.4rem !important;

        box-shadow:
            0 8px 25px rgba(59,130,246,.25) !important;

        transition: .2s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);

        box-shadow:
            0 12px 35px rgba(59,130,246,.35) !important;
    }


    /* ======================================================
       ANSWER CARD
       ====================================================== */

    .answer-card {
        background:
            linear-gradient(
                145deg,
                rgba(15,23,42,.97),
                rgba(7,14,28,.97)
            );

        border: 1px solid rgba(59,130,246,.30);

        border-radius: 20px;

        padding: 26px;

        margin-top: 30px;

        box-shadow:
            0 20px 60px rgba(0,0,0,.35),
            0 0 40px rgba(37,99,235,.04);
    }

    .answer-title {
        display: flex;
        align-items: center;

        gap: 12px;

        font-size: 24px;
        font-weight: 800;

        color: #f8fafc;
    }

    .answer-icon {
        display: flex;

        align-items: center;
        justify-content: center;

        width: 42px;
        height: 42px;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                rgba(14,165,233,.18),
                rgba(124,58,237,.18)
            );

        border: 1px solid rgba(59,130,246,.25);

        font-size: 20px;
    }

    .answer-accent {
        width: 48px;
        height: 3px;

        margin-top: 13px;
        margin-bottom: 20px;

        border-radius: 10px;

        background:
            linear-gradient(
                90deg,
                #38bdf8,
                #8b5cf6
            );
    }


    /* ======================================================
       ANSWER CONTENT
       ====================================================== */

    .answer-card + div {
        color: #e2e8f0;
    }

    .answer-card p {
        color: #e2e8f0;
    }


    /* ======================================================
       SOURCES
       ====================================================== */

    .sources-card {
        background:
            linear-gradient(
                145deg,
                rgba(15,23,42,.92),
                rgba(8,15,30,.92)
            );

        border: 1px solid rgba(71,85,105,.35);

        border-radius: 20px;

        padding: 22px;

        margin-top: 30px;

        box-shadow:
            0 20px 60px rgba(0,0,0,.25);
    }

    .sources-title {
        display: flex;
        align-items: center;

        gap: 10px;

        color: #f8fafc;

        font-size: 20px;
        font-weight: 800;

        margin-bottom: 18px;
    }

    .source-count {
        font-size: 12px;

        color: #60a5fa;

        background: rgba(59,130,246,.10);

        border: 1px solid rgba(59,130,246,.20);

        border-radius: 999px;

        padding: 4px 8px;
    }

    .source-file {
        display: flex;
        align-items: center;

        gap: 10px;

        background: #080f1c;

        border: 1px solid #1e293b;

        border-radius: 11px;

        padding: 12px;

        margin-bottom: 9px;

        color: #cbd5e1;

        font-size: 12px;

        word-break: break-all;
    }

    .grounded-box {
        display: flex;
        align-items: center;

        gap: 8px;

        margin-top: 15px;

        padding: 12px;

        border-radius: 11px;

        color: #4ade80;

        background: rgba(34,197,94,.05);

        border: 1px solid rgba(34,197,94,.15);

        font-size: 13px;
    }


    /* ======================================================
       EXAMPLES
       ====================================================== */

    .examples-title {
        font-size: 21px;
        font-weight: 800;

        margin-top: 42px;
        margin-bottom: 16px;
    }

    .example-box {
        min-height: 105px;

        background:
            linear-gradient(
                145deg,
                rgba(15,23,42,.90),
                rgba(8,15,30,.90)
            );

        border: 1px solid #1e293b;

        border-radius: 14px;

        padding: 16px;

        color: #cbd5e1;

        font-size: 13px;

        line-height: 1.45;

        transition: .2s ease;
    }

    .example-box:hover {
        border-color: #3b82f6;

        box-shadow:
            0 0 25px rgba(59,130,246,.08);
    }


    /* ======================================================
       FOOTER
       ====================================================== */

    .regradar-footer {
        text-align: center;

        color: #64748b;

        font-size: 13px;

        margin-top: 50px;

        padding-top: 22px;

        border-top: 1px solid #172033;
    }

    .footer-brand {
        color: #60a5fa;
        font-weight: 700;
    }

    </style>
    """
)


# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div class="regradar-hero">

        <div class="regradar-shield">
            🛡️
        </div>

        <div class="regradar-title">
            <span class="regradar-reg">Reg</span><span class="regradar-radar">Radar</span>
        </div>

        <div class="regradar-subtitle">
            RBI Regulatory Intelligence Assistant
        </div>

        <div class="regradar-status">
            🟢 &nbsp; Grounded in RBI regulatory documents
        </div>

    </div>

    <div class="regradar-divider"></div>
    """
)


# ============================================================
# QUESTION
# ============================================================

st.html(
    """
    <div class="question-card">

        <div class="question-label">
            <span class="question-icon">◉</span>
            Ask about RBI regulations
        </div>

    </div>
    """
)


question = st.text_area(
    "Question",
    key="question",
    placeholder=(
        "Example: What are the responsibilities "
        "of the Board regarding cybersecurity?"
    ),
    height=130,
    label_visibility="collapsed",
)


# ============================================================
# ASK BUTTON
# ============================================================

ask_clicked = st.button(
    "➤  Ask RegRadar",
)


if ask_clicked:

    if not question.strip():

        st.warning("Please enter a question.")

    else:
        with st.spinner("Searching RBI regulatory documents..."):
            response = requests.post(
                f"{API_URL}/ask",
                json={"text": question},
                timeout=120,
            )

            response.raise_for_status()

            answer = response.json()["answer"]

        refusal = (
            "don't have enough information"
             in answer.lower()
             or
            "attempting to override"
            in answer.lower()
        )

        if not refusal:
            results = smart_search(question, k=3)
        else:
            results = []

        # Remove inline [Source: ...] labels because
        # sources are displayed separately.
        clean_answer = re.sub(
            r"\s*\[Source:[^\]]+\]",
            "",
            answer,
        )

        st.session_state.answer = clean_answer

        unique_sources = []

        for _, source, _ in results:

            if source not in unique_sources:
                unique_sources.append(source)

        st.session_state.sources = unique_sources


# ============================================================
# ANSWER + SOURCES
# ============================================================

if st.session_state.answer:

    answer_col, source_col = st.columns(
        [1.7, 1],
        gap="large",
    )


# ============================================================
# ANSWER + SOURCES
# ============================================================

if st.session_state.answer:

    # Create the two columns FIRST
    answer_col, source_col = st.columns(
        [1.7, 1],
        gap="large",
    )

    # ========================================================
    # ANSWER
    # ========================================================

    with answer_col:

        with st.container(border=True):

            st.html(
                """
                <div class="answer-title">

                    <div class="answer-icon">
                        ✨
                    </div>

                    <div>
                        Answer
                    </div>

                </div>

                <div class="answer-accent"></div>
                """
            )

            # Clean source labels from generated answer
            clean_answer = re.sub(
                r"\s*\[Source:[^\]]+\]",
                "",
                st.session_state.answer,
            )

            # Remove "(Sources: ...)" if present
            clean_answer = re.sub(
                r"\s*\(Sources?:.*?\)",
                "",
                clean_answer,
                flags=re.DOTALL | re.IGNORECASE,
            )

            # Render answer INSIDE the bordered container
            st.markdown(clean_answer)


    # ========================================================
    # SOURCES
    # ========================================================

    with source_col:

        sources = st.session_state.sources

        st.html(
            f"""
            <div class="sources-card">

                <div class="sources-title">

                    📚 Sources

                    <span class="source-count">
                        {len(sources)}
                    </span>

                </div>
            """
        )

        if sources:

            for source in sources:

                st.html(
                    f"""
                    <div class="source-file">
                        <span>📄</span>
                        <span>{source}</span>
                    </div>
                    """
                )

            st.html(
                """
                <div class="grounded-box">
                    🛡️
                    Answer grounded in provided
                    regulatory documents
                </div>
                """
            )

        else:

            st.html(
                """
                <div class="grounded-box">
                    🛡️
                    No supporting source was found.
                </div>
                """
            )

        st.html(
            """
            </div>
            """
        )



# ============================================================
# RETRIEVAL EVALUATION SCOREBOARD
# ============================================================

st.html(
    """
    <div class="examples-title">
        📊 Retrieval Evaluation
    </div>
    """
)

evaluation_data = [
    {
        "Method": "Vector Search",
        "Recall@1": "36.67%",
        "Recall@3": "93.33%",
        "MRR": "0.6278",
    },
    {
        "Method": "Hybrid Search",
        "Recall@1": "46.67%",
        "Recall@3": "100.00%",
        "MRR": "0.7222",
    },
    {
        "Method": "Smart Search",
        "Recall@1": "53.33%",
        "Recall@3": "93.33%",
        "MRR": "0.7278",
    },
]

st.table(evaluation_data)

st.caption(
    "Evaluation based on the current 30-question golden dataset."
)

st.info(
    "Smart Search currently has the best Recall@1 and MRR. "
    "Hybrid Search achieves perfect Recall@3."
)


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

st.html(
    """
    <div class="examples-title">
        💡 Try asking
    </div>
    """
)


examples = [
    "What is cyber resilience?",
    "What are the responsibilities of the Board regarding cybersecurity?",
    "What is a Cyber Crisis Management Plan?",
    "What are the four aspects of a Cyber Crisis Management Plan?",
    "What cybersecurity training is required for Board members?",
]


example_columns = st.columns(
    5,
    gap="small",
)


for i, example in enumerate(examples):

    with example_columns[i]:

        st.html(
            f"""
            <div class="example-box">
                💬
                <br><br>
                {example}
            </div>
            """
        )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="regradar-footer">

        🛡️
        <span class="footer-brand">RegRadar</span>

        &nbsp;•&nbsp;

        RBI Regulatory Intelligence

        &nbsp;•&nbsp;

        Built for clarity. Powered by AI.

    </div>
    """
)