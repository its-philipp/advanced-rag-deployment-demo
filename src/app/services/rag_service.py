import os, asyncio
import time
from dotenv import load_dotenv
from src.app.services.embeddings_minimal import chunk_text, get_embeddings_texts, get_embedding_openai
from src.app.services.qdrant_client import ensure_collection, upsert_documents, search_similar
from src.app.metrics import track_rag_query, track_embedding_request, track_llm_request

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

async def answer_question(user_id: str, query: str, context_limit: int = 5):
    start_time = time.time()
    
    # 1) redact (simple placeholder)
    query_clean = query.replace("\n"," ").strip()
    
    # 2) embed query
    embedding_start = time.time()
    if OPENAI_API_KEY:
        q_emb = get_embedding_openai(query_clean)
        track_embedding_request("openai", time.time() - embedding_start)
    else:
        q_emb = get_embeddings_texts([query_clean])[0]
        track_embedding_request("sentence-transformers", time.time() - embedding_start)
    
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
    llm_start = time.time()
    input_tokens = 0
    output_tokens = 0
    
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
            # Track token usage if available
            if hasattr(resp, 'usage'):
                input_tokens = resp.usage.prompt_tokens
                output_tokens = resp.usage.completion_tokens
        else:
            # fallback simple synthesizer
            answer_text = "Ich habe einige Quellen gefunden; bitte prüfe die Quellen. (Demo-Modus)\n" + "\n".join([s['text_snippet'] for s in sources])
    except Exception as e:
        answer_text = "Fehler beim Modellaufruf: " + str(e)
    
    # Track LLM metrics
    track_llm_request(LLM_MODEL, time.time() - llm_start, input_tokens, output_tokens)
    
    # 7) simple confidence heuristic
    conf = min(0.99, 0.5 + 0.1 * len(sources))
    
    # Track overall RAG query metrics
    total_duration = time.time() - start_time
    track_rag_query(user_id, total_duration, conf, len(sources))
    
    return {"answer": answer_text, "sources": sources, "confidence": conf}
