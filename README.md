# Advanced RAG System with Agentic AI Frameworks

A comprehensive Retrieval-Augmented Generation (RAG) system featuring multiple AI agent frameworks including LangGraph, Semantic Kernel, and custom implementations. The project provides production-ready deployment configurations for Kubernetes, cloud platforms (GKE, AKS, EKS), and serverless environments.

Key Features:
🤖 Multi-Framework Support: Custom Agentic RAG, LangGraph, and Semantic Kernel implementations
🧠 Advanced Memory Management: Episodic, semantic, and procedural memory systems
�� Production Monitoring: Grafana dashboards and Prometheus metrics
☁️ Cloud-Ready: Kubernetes manifests and cloud deployment configs
🔧 Comprehensive Testing: Unit tests, mocked integration tests, and full integration test suites
🚀 Scalable Architecture: Horizontal Pod Autoscaling and production optimizations

Tech Stack: FastAPI, Qdrant, OpenAI, LangChain, Semantic Kernel, Kubernetes, Docker, Grafana, Prometheus

Perfect for developers building AI-powered applications that need reliable RAG capabilities with multiple framework options and enterprise-grade monitoring.

**Production-Ready RAG Backend with FastAPI & Cloud Deployment**

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
