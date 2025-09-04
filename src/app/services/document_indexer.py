import os
from typing import List, Dict
from src.app.services.embeddings import chunk_text, get_embeddings_texts, get_embedding_openai
from src.app.services.qdrant_client import ensure_collection, upsert_documents
import uuid

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def index_documents(documents: List[Dict[str, str]]):
    """
    Index a list of documents into Qdrant.
    
    Args:
        documents: List of dicts with 'title', 'content', and optionally 'source_id'
    """
    all_chunks = []
    all_embeddings = []
    all_metadatas = []
    all_ids = []
    
    for doc in documents:
        source_id = doc.get('source_id', f"doc_{uuid.uuid4().hex[:8]}")
        title = doc.get('title', 'Untitled')
        content = doc.get('content', '')
        
        # Chunk the document
        chunks = chunk_text(content, chunk_size=300, overlap=50)
        
        # Create embeddings for each chunk
        if OPENAI_API_KEY:
            embeddings = [get_embedding_openai(chunk) for chunk in chunks]
        else:
            embeddings = get_embeddings_texts(chunks)
        
        # Prepare metadata and IDs for each chunk
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())  # Use UUID for point ID
            metadata = {
                "source_id": source_id,
                "chunk_id": f"{source_id}_chunk_{i}",
                "title": title,
                "text": chunk,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            
            all_chunks.append(chunk)
            all_embeddings.append(embedding)
            all_metadatas.append(metadata)
            all_ids.append(chunk_id)
    
    # Ensure collection exists with correct dimensions
    if all_embeddings:
        dim = len(all_embeddings[0])
        ensure_collection(dim=dim)
        
        # Upsert all documents
        upsert_documents(all_embeddings, all_metadatas, all_ids)
        print(f"Indexed {len(all_ids)} chunks from {len(documents)} documents")
    
    return len(all_ids)

def get_sample_documents() -> List[Dict[str, str]]:
    """Return sample educational documents for testing."""
    return [
        {
            "source_id": "math_learning_guide",
            "title": "Mathematik Lernstrategien",
            "content": """
            Effektive Mathematik-Lernstrategien:
            
            1. Regelmäßige Übung: Täglich 30-60 Minuten Mathematik üben ist effektiver als sporadische lange Sitzungen.
            
            2. Verstehen vor Auswendiglernen: Konzepte verstehen, bevor man Formeln auswendig lernt.
            
            3. Schritt-für-Schritt-Lösungen: Komplexe Probleme in kleinere Schritte aufteilen.
            
            4. Fehleranalyse: Fehler analysieren und verstehen, warum sie entstanden sind.
            
            5. Verschiedene Lernmethoden: Visuelle, auditive und kinästhetische Lernmethoden kombinieren.
            
            6. Praktische Anwendungen: Mathematik in realen Situationen anwenden.
            
            7. Lerngruppen: Mit anderen lernen und sich gegenseitig erklären.
            
            8. Technologie nutzen: Online-Tools, Apps und Videos für zusätzliches Lernen verwenden.
            """
        },
        {
            "source_id": "study_habits",
            "title": "Effektive Lerngewohnheiten",
            "content": """
            Wissenschaftlich fundierte Lerngewohnheiten:
            
            Spaced Repetition: Informationen in regelmäßigen Abständen wiederholen, um das Langzeitgedächtnis zu stärken.
            
            Active Recall: Sich selbst testen, anstatt nur zu lesen. Dies verbessert das Behalten um 50%.
            
            Interleaving: Verschiedene Themen oder Fähigkeiten in einer Sitzung mischen, anstatt sich auf ein Thema zu konzentrieren.
            
            Elaborative Interrogation: Sich fragen "Warum?" und "Wie?" beim Lernen neuer Konzepte.
            
            Dual Coding: Informationen sowohl verbal als auch visuell kodieren.
            
            Retrieval Practice: Regelmäßig das Gelernte abrufen, ohne auf Notizen zu schauen.
            
            Metacognition: Über das eigene Denken nachdenken und Lernstrategien bewusst anpassen.
            
            Pomodoro-Technik: 25 Minuten fokussiert lernen, dann 5 Minuten Pause.
            """
        },
        {
            "source_id": "memory_techniques",
            "title": "Gedächtnistechniken",
            "content": """
            Bewährte Gedächtnistechniken für besseres Lernen:
            
            Mnemonics: Gedächtnishilfen wie Akronyme, Reime oder Geschichten verwenden.
            
            Method of Loci: Informationen mit bekannten Orten verknüpfen (Gedächtnispalast).
            
            Chunking: Große Informationsmengen in kleinere, verwandte Gruppen aufteilen.
            
            Visualization: Mentale Bilder erstellen, um abstrakte Konzepte zu verstehen.
            
            Association: Neue Informationen mit bereits bekannten verknüpfen.
            
            Storytelling: Informationen in eine Geschichte verwandeln, um sie besser zu merken.
            
            Mind Mapping: Visuelle Darstellung von Informationen und deren Zusammenhängen.
            
            Repetition with Variation: Informationen in verschiedenen Kontexten wiederholen.
            """
        },
        {
            "source_id": "time_management",
            "title": "Zeitmanagement für Studenten",
            "content": """
            Effektive Zeitmanagement-Strategien:
            
            Prioritäten setzen: Wichtige und dringende Aufgaben identifizieren (Eisenhower-Matrix).
            
            Zeitblöcke: Spezifische Zeiten für verschiedene Aktivitäten reservieren.
            
            Deadlines setzen: Realistische Fristen für Aufgaben festlegen.
            
            Ablenkungen minimieren: Handy, soziale Medien und andere Störungen während der Lernzeit ausschalten.
            
            Pausen einplanen: Regelmäßige Pausen für bessere Konzentration und Produktivität.
            
            Aufgabenlisten: Tägliche und wöchentliche To-Do-Listen erstellen.
            
            Realistische Ziele: Erreichbare Ziele setzen, um Frustration zu vermeiden.
            
            Flexibilität: Zeitpläne anpassen können, wenn unvorhergesehene Ereignisse eintreten.
            """
        }
    ]
