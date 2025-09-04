import os, asyncio
from src.app.services.embeddings import chunk_text, get_embeddings_texts, get_embedding_openai
from src.app.services.qdrant_client import ensure_collection, upsert_documents, search_similar

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

async def answer_question(user_id: str, query: str, context_limit: int = 5):
    # 1) redact (simple placeholder)
    query_clean = query.replace("\n"," ").strip()
    # 2) embed query
    if OPENAI_API_KEY:
        q_emb = get_embedding_openai(query_clean)
    else:
        q_emb = get_embeddings_texts([query_clean])[0]
    # 3) ensure collection exists
    ensure_collection(dim=len(q_emb))
    # 4) search similar
    docs = search_similar(q_emb, top_k=context_limit)
    # 5) build prompt (simple concatenation with attribution)
    retrieved_texts = []
    sources = []
    for d in docs:
        payload = d.get("payload", {})
        text = payload.get("text", "")
        src = payload.get("source_id", d.get("id"))
        retrieved_texts.append(f"SOURCE[{src}]: {text}")
        sources.append({
            "source_id": src,
            "chunk_id": payload.get("chunk_id", ""),
            "score": d.get("score", 0.0),
            "text_snippet": text[:400]
        })
    system_prompt = "Du bist ein sachlicher Lern-Coach. Antworte kurz und zitiere die Quellen."
    prompt = system_prompt + "\n\n" + "\n\n".join(retrieved_texts) + "\n\nFrage: " + query_clean
    # 6) call LLM (OpenAI)
    answer_text = ""    
    try:
        if OPENAI_API_KEY:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model=LLM_MODEL, 
                messages=[
                    {"role":"system","content":system_prompt},
                    {"role":"user","content":prompt}
                ], 
                max_tokens=400, 
                temperature=0.0
            )
            answer_text = resp.choices[0].message.content.strip()
        else:
            # fallback simple synthesizer
            answer_text = "Ich habe einige Quellen gefunden; bitte prüfe die Quellen. (Demo-Modus)\n" + "\n".join([s['text_snippet'] for s in sources])
    except Exception as e:
        answer_text = "Fehler beim Modellaufruf: " + str(e)
    # 7) simple confidence heuristic
    conf = min(0.99, 0.5 + 0.1 * len(sources))
    return {"answer": answer_text, "sources": sources, "confidence": conf}
