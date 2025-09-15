"""
User-specific coaching agent that provides personalized responses
based on user context, preferences, and chat history.
"""
import os
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
from src.app.services.embeddings_minimal import get_embedding_openai, get_embeddings_texts
from src.app.services.qdrant_client import search_hybrid, search_user_similar, search_similar
from src.app.services.user_context import UserContext
from src.app.metrics import track_rag_query, track_embedding_request, track_llm_request

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

class UserCoachingAgent:
    """Personalized coaching agent for individual users."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.context = UserContext(user_id)
    
    async def answer_question(self, query: str, context_limit: int = 5, use_hybrid: bool = True):
        """Answer a question with personalized context."""
        start_time = time.time()
        
        # 1) Clean query
        query_clean = query.replace("\n", " ").strip()
        
        # 2) Get query embedding
        embedding_start = time.time()
        if OPENAI_API_KEY:
            q_emb = get_embedding_openai(query_clean)
            track_embedding_request("openai", time.time() - embedding_start)
        else:
            q_emb = get_embeddings_texts([query_clean])[0]
            track_embedding_request("sentence-transformers", time.time() - embedding_start)
        
        # 3) Search for relevant documents
        if use_hybrid:
            docs = search_hybrid(self.user_id, q_emb, top_k=context_limit)
        else:
            # Try user-specific first, fallback to global
            docs = search_user_similar(self.user_id, q_emb, top_k=context_limit)
            if not docs:
                docs = search_similar(q_emb, top_k=context_limit)
        
        # 4) Build context from retrieved documents
        retrieved_texts = []
        sources = []
        for d in docs:
            payload = d.get("payload", {})
            text = payload.get("text", "")
            src = payload.get("source_id", d.get("id"))
            source_type = d.get("source", "global")
            
            retrieved_texts.append(f"SOURCE[{src}]: {text}")
            sources.append({
                "source_id": src,
                "chunk_id": payload.get("chunk_id", ""),
                "score": d.get("score", 0.0),
                "text_snippet": text[:400],
                "source_type": source_type
            })
        
        # 5) Build personalized prompt
        system_prompt = self.context.get_personality_prompt()
        
        # Add recent context if available
        recent_context = self.context.get_recent_context(3)
        context_text = ""
        if recent_context:
            context_text = "\n\nVorheriger Gesprächsverlauf:\n"
            for msg in recent_context:
                role = "Nutzer" if msg.role == "user" else "Coach"
                context_text += f"{role}: {msg.content}\n"
        
        # Build the full prompt
        prompt = system_prompt + context_text + "\n\nRelevante Quellen:\n" + "\n\n".join(retrieved_texts) + "\n\nFrage: " + query_clean
        
        # 6) Generate response with LLM
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
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.1  # Lower temperature for more consistent responses
                )
                answer_text = resp.choices[0].message.content.strip()
                
                # Track token usage
                if hasattr(resp, 'usage'):
                    input_tokens = resp.usage.prompt_tokens
                    output_tokens = resp.usage.completion_tokens
            else:
                # Fallback response
                answer_text = f"Basierend auf deinen Präferenzen und dem Kontext: {query_clean}\n\nRelevante Quellen:\n" + "\n".join([s['text_snippet'] for s in sources])
        except Exception as e:
            answer_text = f"Fehler beim Generieren der Antwort: {str(e)}"
        
        # Track LLM metrics
        track_llm_request(LLM_MODEL, time.time() - llm_start, input_tokens, output_tokens)
        
        # 7) Calculate confidence
        conf = min(0.99, 0.5 + 0.1 * len(sources))
        
        # 8) Update user context
        self.context.add_chat_interaction(query_clean, answer_text, sources, conf)
        
        # 9) Track overall metrics
        total_duration = time.time() - start_time
        track_rag_query(self.user_id, total_duration, conf, len(sources))
        
        return {
            "answer": answer_text,
            "sources": sources,
            "confidence": conf,
            "personalized": True,
            "user_context": {
                "learning_goals": self.context.profile.learning_goals,
                "learning_style": self.context.profile.learning_style,
                "total_sessions": self.context.profile.total_sessions
            }
        }
    
    def update_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences."""
        self.context.update_preferences(preferences)
    
    def update_learning_goals(self, goals: List[str]):
        """Update user learning goals."""
        self.context.update_learning_goals(goals)
    
    def update_learning_style(self, style: str):
        """Update user learning style."""
        self.context.update_learning_style(style)
    
    def get_user_summary(self) -> Dict[str, Any]:
        """Get user profile summary."""
        return self.context.get_user_summary()
    
    def add_user_document(self, title: str, content: str, source_id: str = None):
        """Add a document to the user's personal collection."""
        from src.app.services.document_indexer import chunk_text, get_embeddings_texts, get_embedding_openai
        from src.app.services.qdrant_client import upsert_user_documents
        import uuid
        
        # Generate source ID if not provided
        if not source_id:
            source_id = f"user_{self.user_id}_{uuid.uuid4().hex[:8]}"
        
        # Chunk the document
        chunks = chunk_text(content, chunk_size=300, overlap=50)
        
        # Create embeddings
        if OPENAI_API_KEY:
            embeddings = [get_embedding_openai(chunk) for chunk in chunks]
        else:
            embeddings = get_embeddings_texts(chunks)
        
        # Prepare metadata and IDs
        metadatas = []
        ids = []
        for i, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            metadata = {
                "source_id": source_id,
                "chunk_id": f"{source_id}_chunk_{i}",
                "title": title,
                "text": chunk,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "user_id": self.user_id,
                "document_type": "user_upload"
            }
            metadatas.append(metadata)
            ids.append(chunk_id)
        
        # Upsert to user collection
        upsert_user_documents(self.user_id, embeddings, metadatas, ids)
        
        return len(chunks)
