import os
from pathlib import Path

from groq import Groq
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
QDRANT_PATH = BASE_DIR / "COBOL_logic_extrator" / "qdrant_storage"
COLLECTION_NAME = "cobol_code_chunks"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "openai/gpt-oss-20b"

TOP_K = 5


# ============================================================
# CHECK GROQ API KEY
# ============================================================

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is not set.\n"
        'Run: $env:GROQ_API_KEY="YOUR_KEY"'
    )

groq_client = Groq(api_key=api_key)


# ============================================================
# CONNECT TO QDRANT
# ============================================================

print("\n========================================")
print("COBOL RAG ASSISTANT")
print("========================================")

print("\nConnecting to Qdrant...")

qdrant = QdrantClient(path=str(QDRANT_PATH))

if not qdrant.collection_exists(COLLECTION_NAME):
    raise RuntimeError(
        f"Qdrant collection '{COLLECTION_NAME}' does not exist."
    )

collection_info = qdrant.get_collection(COLLECTION_NAME)

print("Connected to Qdrant")
print("Collection:", COLLECTION_NAME)
print("Vectors available:", collection_info.points_count)


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("\nLoading embedding model...")

embedding_model = SentenceTransformer(EMBEDDING_MODEL)

print("Embedding model ready.")


# ============================================================
# SEMANTIC RETRIEVAL
# ============================================================

def retrieve_chunks(question):

    query_vector = embedding_model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    response = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=TOP_K,
        with_payload=True
    )

    return response.points


# ============================================================
# BUILD EVIDENCE CONTEXT
# ============================================================

def build_context(results):

    context_parts = []

    for number, result in enumerate(results, start=1):

        payload = result.payload or {}

        evidence = f"""
================ EVIDENCE {number} ================

Similarity Score:
{result.score:.4f}

File:
{payload.get("file_name", "UNKNOWN")}

Program:
{payload.get("program", "UNKNOWN")}

Section:
{payload.get("section", "UNKNOWN")}

Paragraph:
{payload.get("paragraph", "UNKNOWN")}

Operations:
{payload.get("operations", [])}

Variables:
{payload.get("variables", [])}

COBOL CODE:
{payload.get("code", "")}
"""

        context_parts.append(evidence)

    return "\n".join(context_parts)


# ============================================================
# ASK LLM
# ============================================================

def ask_llm(question, context):

    system_prompt = """
You are a legacy COBOL code analysis assistant.

Your job is to explain business logic using ONLY the COBOL
evidence retrieved from the vector database.

STRICT RULES:

1. Do not invent COBOL logic.
2. Do not invent file names.
3. Do not invent paragraph names.
4. Do not invent variables.
5. Use only information contained in the supplied evidence.
6. If the evidence is insufficient, clearly say:
   "The retrieved evidence is insufficient to answer this confidently."
7. Distinguish direct evidence from interpretation.
8. When a calculation exists, explain the actual formula.
9. Mention the strongest supporting file and paragraph.
10. Keep the explanation understandable to a developer or business analyst.
11. Do not claim that one program feeds another unless the supplied
    evidence directly establishes that relationship.
12. Do not treat semantic similarity as proof of dependency or lineage.

Return the answer in this format:

ANSWER:
<clear answer>

LOCATION:
File:
Program:
Paragraph:

BUSINESS LOGIC:
<simple explanation>

EVIDENCE:
<important COBOL statements or variables supporting the answer>

CONFIDENCE:
High / Medium / Low
"""

    user_prompt = f"""
USER QUESTION:

{question}


RETRIEVED COBOL EVIDENCE:

{context}


Answer the question using only the evidence above.
"""

    response = groq_client.chat.completions.create(
        model=LLM_MODEL,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        temperature=0.1,
        max_tokens=1200
    )

    return response.choices[0].message.content


# ============================================================
# MAIN
# ============================================================

try:

    while True:

        print("\n========================================")

        question = input(
            "\nAsk a question about the COBOL code "
            "(or type 'exit'): "
        ).strip()

        if question.lower() in {"exit", "quit"}:
            print("\nCOBOL RAG Assistant stopped.")
            break

        if not question:
            continue


        # ----------------------------------------------------
        # STEP 1 - QDRANT RETRIEVAL
        # ----------------------------------------------------

        print("\nSearching Qdrant...")

        results = retrieve_chunks(question)

        if not results:
            print("No relevant COBOL evidence found.")
            continue

        print(
            f"Retrieved {len(results)} relevant COBOL chunks."
        )


        # ----------------------------------------------------
        # STEP 2 - BUILD CONTEXT
        # ----------------------------------------------------

        context = build_context(results)


        # ----------------------------------------------------
        # STEP 3 - SEND ONLY RETRIEVED EVIDENCE TO GROQ
        # ----------------------------------------------------

        print("Sending retrieved evidence to LLM...")

        answer = ask_llm(
            question,
            context
        )


        # ----------------------------------------------------
        # STEP 4 - FINAL ANSWER
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("RAG ANSWER")
        print("=" * 70)

        print(answer)

        print("\n" + "=" * 70)
        print("RETRIEVAL SOURCES")
        print("=" * 70)

        for i, result in enumerate(results, start=1):

            payload = result.payload or {}

            print(
                f"{i}. "
                f"{payload.get('file_name')} | "
                f"{payload.get('program')} | "
                f"{payload.get('paragraph')} | "
                f"Score: {result.score:.4f}"
            )

        print("=" * 70)


finally:

    qdrant.close()