"""
Step 4 -- RAG query pipeline: retrieval -> prompt construction -> Groq LLM
-> grounded answer + sources, with an explicit hallucination guardrail.
"""
from groq import Groq
from app.config import GROQ_API_KEY, MODEL_NAME, TOP_K_RESULTS
from app.vector_store import query_similar

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using ONLY the
provided document excerpts (context). Follow these rules strictly:

1. Only use information found in the provided context to answer.
2. If the context does not contain the information needed to answer the question,
   respond exactly with: "I could not find this information in the uploaded documents."
   Do not guess, and do not use outside/general knowledge.
3. Be concise and direct.
4. Do not mention "the context" or "the documents provided" in your answer -- just
   answer naturally as if you know the information, and cite sources separately.
"""


def build_prompt(question: str, matches: list):
    if not matches:
        context_block = "(no relevant context found)"
    else:
        context_block = "\n\n".join(
            f"[Source: {m['metadata']['document_name']}, Page {m['metadata']['page_number']}]\n{m['text']}"
            for m in matches
        )
    return f"""Context:
{context_block}

Question: {question}

Answer the question using only the context above."""


def answer_question(question: str, top_k: int = None):
    top_k = top_k or TOP_K_RESULTS
    matches = query_similar(question, top_k=top_k)

    # Hallucination guardrail: if nothing relevant was retrieved at all,
    # short-circuit before even calling the LLM.
    if not matches:
        return {
            "answer": "I could not find this information in the uploaded documents.",
            "sources": [],
        }

    prompt = build_prompt(question, matches)

    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=600,
    )
    answer_text = completion.choices[0].message.content.strip()

    # De-duplicate sources (same doc+page can appear from multiple chunks)
    seen = set()
    sources = []
    for m in matches:
        key = (m["metadata"]["document_name"], m["metadata"]["page_number"])
        if key not in seen:
            seen.add(key)
            sources.append({
                "document_name": m["metadata"]["document_name"],
                "page_number": m["metadata"]["page_number"],
            })

    return {"answer": answer_text, "sources": sources}
