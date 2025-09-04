# pinkpro-rag-demo

**Klein-Demo für Bewerbung — RAG-basiertes Backend (FastAPI)**

## Ziel
Einfacher Proof-of-Concept: Indexieren von Dokumenten in Qdrant, Retrieval + RAG-Orchestrierung, Source-Attribution, PII-Redaction, Docker + simple CI-Ready Struktur.

## Quickstart (lokal, ohne K8s)

**Voraussetzungen**
- Python 3.10+
- Docker & Docker Compose
- OpenAI API-Key

**Setup Environment Variables**
1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` and add your API keys:
```bash
# Edit .env file with your actual API keys
OPENAI_API_KEY=your_actual_openai_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here  # optional
```

**Option 1: Docker Compose (Recommended)**
```bash
# Start all services (Qdrant + RAG Demo)
docker-compose up --build

# Index sample documents
curl -X POST "http://localhost:8080/api/v1/index-sample-docs"

# Test the API
curl -X POST "http://localhost:8080/api/v1/coach" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user", "query": "Wie verbessere ich meine Lernroutine?", "context_limit": 3}'
```

**Option 2: Local Development**
```bash
# Start Qdrant
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest

# Setup Python environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the application
uvicorn src.app.main:app --reload --port 8080
```

**Option 3: Docker Only**
```bash
# Start Qdrant
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest

# Build and run RAG demo
docker build --tag rag-demo:latest .
docker run -d -p 8080:8080 \
  -e QDRANT_URL="http://host.docker.internal:6333" \
  -e OPENAI_API_KEY="your_api_key_here" \
  --name rag-demo-container rag-demo:latest
```

**Demo request (POST /api/v1/coach)**
```json
{
  "user_id": "demo_user_1",
  "query": "Wie verbessere ich meine Lernroutine für Mathe?",
  "context_limit": 5
}
```

```bash
curl -X POST "http://localhost:8080/api/v1/coach" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_1",
    "query": "Wie verbessere ich meine Lernroutine für Mathe?",
    "context_limit": 5
  }'
```

**Beispiel-Antwort**
```json
{
  "answer": "Kurzer, fundierter Text...",
  "sources": [
    {"source_id": "doc_123", "chunk_id": "c_3", "score": 0.91, "text_snippet": "..." }
  ],
  "confidence": 0.82
}
```
```json
{
  "answer": "Um deine Lernroutine für Mathe zu verbessern, kannst du folgende Strategien anwenden:\n\n1. **Regelmäßige Übung**: Plane tägliche Übungseinheiten ein, um Konzepte zu festigen (Schunk, D. H. (2012). Learning Theories: An Educational Perspective).\n\n2. **Aktives Lernen**: Nutze aktive Lernmethoden wie das Lösen von Aufgaben, Erklären von Konzepten und das Arbeiten mit Lernpartnern (Prince, M. (2004). Does Active Learning Work? A Review of the Research).\n\n3. **Zielsetzung**: Setze dir spezifische, messbare Ziele für jede Lerneinheit (Locke, E. A., & Latham, G. P. (2002). Building a Practically Useful Theory of Goal Setting and Task Motivation).\n\n4. **Ressourcen nutzen**: Verwende verschiedene Lernressourcen wie Online-Kurse, Videos und Übungsblätter (Hattie, J. (2009). Visible Learning: A Synthesis of Over 800 Meta-Analyses Relating to Achievement).\n\n5. **Reflexion**: Nimm dir Zeit, um über das Gelernte nachzudenken und deine Fortschritte zu bewerten (Schön, D. A. (1983). The Reflective Practitioner: How Professionals Think in Action).\n\nDiese Ansätze können dir helfen, deine Mathekenntnisse systematisch zu verbessern.",
  "sources": [],
  "confidence": 0.5
}
```

```bash                                                      
{
    "user_id": "demo_user_1",
    "query": "Wie verbessere ich meine Lernroutine für Mathe?",
    "context_limit": 5
}
{"answer":"Um deine Lernroutine für Mathe zu verbessern, kannst du folgende Strategien anwenden:\n\n1. **Regelmäßige Übung**: Plane tägliche Übungseinheiten ein, um Konzepte zu festigen (Schunk, D. H. (2012). Learning Theories: An Educational Perspective).\n\n2. **Aktives Lernen**: Nutze aktive Lernmethoden wie das Lösen von Aufgaben, Erklären von Konzepten und das Arbeiten mit Lernpartnern (Prince, M. (2004). Does Active Learning Work? A Review of the Research).\n\n3. **Zielsetzung**: Setze dir spezifische, messbare Ziele für jede Lerneinheit (Locke, E. A., & Latham, G. P. (2002). Building a Practically Useful Theory of Goal Setting and Task Motivation).\n\n4. **Ressourcen nutzen**: Verwende verschiedene Lernressourcen wie Online-Kurse, Videos und Übungsblätter (Hattie, J. (2009). Visible Learning: A Synthesis of Over 800 Meta-Analyses Relating to Achievement).\n\n5. **Reflexion**: Nimm dir Zeit, um über das Gelernte nachzudenken und deine Fortschritte zu bewerten (Schön, D. A. (1983). The Reflective Practitioner: How Professionals Think in Action).\n\nDiese Ansätze können dir helfen, deine Mathekenntnisse systematisch zu verbessern.","sources":[],"confidence":0.5}
```

## Testing & CI/CD

**Run Tests Locally**
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

**GitHub Actions CI/CD**
The project includes automated CI/CD with GitHub Actions:
- ✅ **Multi-Python Testing**: Tests on Python 3.10 and 3.11
- ✅ **Docker Build**: Automated Docker image building
- ✅ **Linting**: Code quality checks with flake8
- ✅ **Environment Variables**: Secure handling of API keys via GitHub Secrets

**Setup GitHub Secrets**
Add these secrets to your GitHub repository:
- `OPENAI_API_KEY`: Your OpenAI API key for testing

## Was zeigen im Interview
- ✅ **Live Demo**: Running RAG system with source attribution
- ✅ **Clean Architecture**: Modular FastAPI service with proper separation
- ✅ **CI/CD Pipeline**: Automated testing and Docker builds
- ✅ **Security**: Environment variables and proper secret management
- ✅ **Documentation**: Comprehensive README with multiple deployment options

## Responsible AI / Privacy Hinweise
- Keine Roh-Prompts persistent speichern. Nur anonymisierte Telemetrie (template_id, latency, conf).
- PII-Redaction vor Persistenz.
- Source attribution in Antworten.
- Hosting in EU-Region für DSGVO-Kompatibilität.

## Dateien in diesem Repo
- `src/app` (FastAPI service)
- `src/app/services` (rag_service, embeddings)
- `docker/Dockerfile`
- `k8s/` (Beispiele)


## Architektur-Überblick:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│   Qdrant DB      │    │   OpenAI API    │
│   (Docker)      │    │   (Vector Store) │    │   (LLM + Embed) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Document Indexer│    │ Vector Search    │    │ Text Generation │
│ Chunking Service│    │ Similarity Match │    │ Source Citation │
└─────────────────┘    └──────────────────┘    └─────────────────┘

