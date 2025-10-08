# Advanced RAG System with Agentic AI Frameworks

A comprehensive Retrieval-Augmented Generation (RAG) system featuring multiple AI agent frameworks including LangGraph, Semantic Kernel, and custom implementations. The project provides production-ready deployment configurations for Kubernetes, cloud platforms (GKE, AKS, EKS), and serverless environments.

**Key Features:**
- 🤖 **Multi-Framework Support**: Custom Agentic RAG, LangGraph, and Semantic Kernel implementations
- 🧠 **Advanced Memory Management**: Episodic, semantic, and procedural memory systems
- 📊 **Production Monitoring**: Grafana dashboards and Prometheus metrics
- ☁️ **Cloud-Ready**: Kubernetes manifests and cloud deployment configs
- 🔧 **Comprehensive Testing**: Unit tests, mocked integration tests, and full integration test suites
- 🚀 **Scalable Architecture**: Horizontal Pod Autoscaling and production optimizations

**Tech Stack:** FastAPI, Qdrant, OpenAI, LangChain, Semantic Kernel, Kubernetes, Docker, Grafana, Prometheus

---

## 🎯 What Can This App Do?

This is a **Production-Ready Retrieval-Augmented Generation (RAG) system** that combines personalized AI coaching with advanced agentic AI frameworks. Perfect for building **personalized AI tutors, coaching assistants, or knowledge management systems** with rich user context and memory.

### 📡 Available API Endpoints

#### **1. Personalized Coaching API** (`/api/v1/*`)

**Query & Coaching**
- `POST /api/v1/coach` - Ask questions with personalized coaching and source attribution
- `POST /api/v1/personalized-coach` - Enhanced coaching with hybrid search (personal + global docs)

**User Management**
- `GET /api/v1/users/{user_id}/profile` - Get user profile, preferences, and learning goals
- `PUT /api/v1/users/{user_id}/preferences` - Update learning style and preferences
- `PUT /api/v1/users/{user_id}/learning-goals` - Set/update learning goals
- `GET /api/v1/users/{user_id}/context` - View recent conversation history

**Document Management**
- `POST /api/v1/index-sample-docs` - Load sample educational documents
- `POST /api/v1/index-document` - Index a single global document
- `POST /api/v1/users/{user_id}/documents` - Add documents to user's personal collection

#### **2. Advanced Agentic RAG API** (`/api/agentic/*`)

**Agentic Query Processing**
- `POST /api/agentic/agentic-query` - Query with custom agentic RAG (all memory types)
- `POST /api/agentic/semantic-kernel-query` - Query using Microsoft Semantic Kernel
- `POST /api/agentic/langgraph-query` - Query using LangGraph framework
- `POST /api/agentic/compare-frameworks` - Compare all three frameworks side-by-side

**Memory Management**
- `GET /api/agentic/memory-stats` - Get statistics about stored memories
- `POST /api/agentic/store-semantic-memory` - Store facts, concepts, knowledge
- `POST /api/agentic/store-procedural-memory` - Store skills, workflows, procedures
- `GET /api/agentic/episodic-memories/{user_id}` - Retrieve user's past interactions
- `GET /api/agentic/semantic-memories` - Query stored concepts and knowledge
- `GET /api/agentic/procedural-memories` - Query stored procedures and skills

**User Initialization**
- `POST /api/agentic/initialize-user/{user_id}` - Initialize new user with default memories
- `DELETE /api/agentic/clear-memories` - Clear all memories (testing only)

#### **3. System Endpoints**
- `GET /health` - Health check endpoint
- `GET /metrics` - Prometheus metrics for monitoring

### 🔑 Core Capabilities

- **Personalized Learning** - Tracks user preferences, learning style, and goals
- **Hybrid Search** - Combines user's personal documents with global knowledge base
- **Source Attribution** - Every answer includes sources with confidence scores
- **Multi-Framework Support** - Compare different AI agent implementations
- **Advanced Memory** - Episodic (past events), Semantic (facts), Procedural (skills)
- **Production Ready** - Monitoring, health checks, and cloud deployment configs

---

## Quick Start

This is a comprehensive Retrieval-Augmented Generation (RAG) system featuring document indexing, vector search, source attribution, and cloud deployment capabilities.

### 🚀 Quick Setup

**Prerequisites**
- Python 3.10+
- Docker & Docker Compose
- OpenAI API Key

**1. Environment Setup**
```bash
cp env.example .env
# Edit .env with your API keys
```

**2. Start with Docker Compose**
```bash
docker-compose up --build
```

**3. Test the API**
```bash
curl -X POST "http://localhost:8080/api/v1/coach" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user", "query": "How can I improve my learning routine?", "context_limit": 3}'
```

## 📚 Documentation

- **[Complete Documentation](docs/README.md)** - Full setup and deployment guide
- **[Cloud Deployment](docs/CLOUD_RUN_DEPLOYMENT.md)** - Google Cloud Run deployment
- **[Monitoring Setup](docs/MONITORING.md)** - Grafana and Prometheus monitoring
- **[Agentic RAG](docs/AGENTIC_RAG_IMPLEMENTATION.md)** - Advanced agentic implementations

## 🏗️ Project Structure

```
├── src/                    # Source code
│   ├── app/               # FastAPI application
│   └── agents/            # Agentic RAG implementations
├── docker/                # Docker configurations
│   └── versions/          # Alternative Docker builds
├── k8s/                   # Kubernetes manifests
├── cloud/                 # Cloud deployment configs
├── monitoring/            # Monitoring dashboards
├── tests/                 # Test suites
│   └── integration/       # Integration tests
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── logs/                  # Application logs
```

## 🚀 Deployment Options

- **Local Development**: Docker Compose
- **Kubernetes**: Minikube, GKE, EKS, AKS
- **Cloud**: Google Cloud Run, Railway, Render
- **Monitoring**: Prometheus + Grafana

## 🔧 Key Features

- ✅ **Live Demo**: Running RAG system with source attribution
- ✅ **Clean Architecture**: Modular FastAPI service
- ✅ **CI/CD Pipeline**: Automated testing and Docker builds
- ✅ **Cloud Ready**: Multiple deployment options
- ✅ **Monitoring**: Comprehensive observability
- ✅ **Scalability**: Kubernetes HPA and load balancing

## 📖 Learn More

For detailed setup instructions, deployment guides, and advanced features, see the [complete documentation](docs/README.md).