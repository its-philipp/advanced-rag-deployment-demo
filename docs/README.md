# Advanced RAG System

**Production-Ready RAG Backend with FastAPI & Cloud Deployment**

## Overview
A comprehensive Retrieval-Augmented Generation (RAG) system featuring document indexing, vector search, source attribution, and cloud deployment capabilities. Built with FastAPI, Qdrant vector database, and OpenAI integration.

## Quickstart (Local Development)

**Prerequisites**
- Python 3.10+
- Docker & Docker Compose
- OpenAI API Key

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
  -d '{"user_id": "demo_user", "query": "How can I improve my learning routine?", "context_limit": 3}'
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
  "query": "How can I improve my learning routine for mathematics?",
  "context_limit": 5
}
```

```bash
curl -X POST "http://localhost:8080/api/v1/coach" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_1",
    "query": "How can I improve my learning routine for mathematics?",
    "context_limit": 5
  }'
```

**Example Response**
```json
{
  "answer": "Brief, well-founded text...",
  "sources": [
    {"source_id": "doc_123", "chunk_id": "c_3", "score": 0.91, "text_snippet": "..." }
  ],
  "confidence": 0.82
}
```
```json
{
  "answer": "To improve your learning routine for mathematics, you can apply the following strategies:\n\n1. **Regular Practice**: Plan daily practice sessions to reinforce concepts (Schunk, D. H. (2012). Learning Theories: An Educational Perspective).\n\n2. **Active Learning**: Use active learning methods like solving problems, explaining concepts, and working with study partners (Prince, M. (2004). Does Active Learning Work? A Review of the Research).\n\n3. **Goal Setting**: Set specific, measurable goals for each study session (Locke, E. A., & Latham, G. P. (2002). Building a Practically Useful Theory of Goal Setting and Task Motivation).\n\n4. **Resource Utilization**: Use various learning resources like online courses, videos, and practice sheets (Hattie, J. (2009). Visible Learning: A Synthesis of Over 800 Meta-Analyses Relating to Achievement).\n\n5. **Reflection**: Take time to reflect on what you've learned and evaluate your progress (Schön, D. A. (1983). The Reflective Practitioner: How Professionals Think in Action).\n\nThese approaches can help you systematically improve your mathematics skills.",
  "sources": [],
  "confidence": 0.5
}
```

```bash                                                      
{
    "user_id": "demo_user_1",
    "query": "How can I improve my learning routine for mathematics?",
    "context_limit": 5
}
{"answer":"To improve your learning routine for mathematics, you can apply the following strategies:\n\n1. **Regular Practice**: Plan daily practice sessions to reinforce concepts (Schunk, D. H. (2012). Learning Theories: An Educational Perspective).\n\n2. **Active Learning**: Use active learning methods like solving problems, explaining concepts, and working with study partners (Prince, M. (2004). Does Active Learning Work? A Review of the Research).\n\n3. **Goal Setting**: Set specific, measurable goals for each study session (Locke, E. A., & Latham, G. P. (2002). Building a Practically Useful Theory of Goal Setting and Task Motivation).\n\n4. **Resource Utilization**: Use various learning resources like online courses, videos, and practice sheets (Hattie, J. (2009). Visible Learning: A Synthesis of Over 800 Meta-Analyses Relating to Achievement).\n\n5. **Reflection**: Take time to reflect on what you've learned and evaluate your progress (Schön, D. A. (1983). The Reflective Practitioner: How Professionals Think in Action).\n\nThese approaches can help you systematically improve your mathematics skills.","sources":[],"confidence":0.5}
```

## Kubernetes Deployment

**Prerequisites**
- Docker
- minikube
- kubectl

**Quick Start with minikube**
```bash
# 1. Start minikube
minikube start --memory=4096 --cpus=2

# 2. Enable ingress
minikube addons enable ingress

# 3. Update secrets with your API keys
# Edit k8s/secret.yaml and replace the placeholder values

# 4. Deploy everything
./scripts/setup-minikube.sh

# 5. Test the application
SERVICE_URL=$(minikube service rag-demo-service -n rag-demo --url)
curl -X POST "$SERVICE_URL/api/v1/index-sample-docs"
curl -X POST "$SERVICE_URL/api/v1/coach" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "query": "How can I improve my learning routine?", "context_limit": 3}'
```

**Load Testing & HPA**
```bash
# Run load test to trigger HPA scaling
./scripts/load-test.sh $SERVICE_URL 10 20

# Monitor HPA scaling
kubectl get hpa -n rag-demo -w

# Check pod scaling
kubectl get pods -n rag-demo -w
```

**Cleanup**
```bash
./scripts/cleanup.sh
```

## Testing & CI/CD

**Run Tests Locally**
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run unit tests
pytest tests/ -v

# Run integration tests
pytest tests/integration/ -v

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

## Key Features
- ✅ **Live Demo**: Running RAG system with source attribution
- ✅ **Clean Architecture**: Modular FastAPI service with proper separation
- ✅ **CI/CD Pipeline**: Automated testing and Docker builds
- ✅ **Security**: Environment variables and proper secret management
- ✅ **Documentation**: Comprehensive README with multiple deployment options
- ✅ **Cloud Deployment**: Ready for AWS, GCP, Azure with monitoring
- ✅ **Scalability**: Kubernetes HPA and load balancing

## Responsible AI / Privacy Features
- No raw prompts stored persistently. Only anonymized telemetry (template_id, latency, confidence).
- PII redaction before persistence.
- Source attribution in responses.
- GDPR-compatible hosting options.

## Repository Structure
- `src/app` (FastAPI service)
- `src/app/services` (RAG service, embeddings, document indexing)
- `src/agents` (Advanced agentic RAG implementations)
- `docker/` (Docker configurations and versions)
- `k8s/` (Kubernetes deployment manifests)
- `cloud/` (Cloud deployment configurations)
- `monitoring/` (Grafana dashboards and Prometheus configs)
- `tests/` (Unit and integration tests)
- `docs/` (Documentation files)
- `scripts/` (Utility scripts and monitoring tools)
- `logs/` (Application logs)


## Architecture Overview
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

