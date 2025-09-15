# 📊 Monitoring Setup Guide

This guide explains how to set up and use the monitoring stack for the RAG demo application.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│   Prometheus     │    │   Grafana       │
│   (Port 8080)   │    │   (Port 9090)    │    │   (Port 3000)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   /metrics      │    │   Metrics Store  │    │   Dashboards    │
│   Endpoint      │    │   & Scraping     │    │   & Alerts      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start the Complete Stack

```bash
# Start all services (RAG app + Qdrant + Prometheus + Grafana)
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 2. Test the Setup

```bash
# Run the test script
python test_monitoring.py
```

### 3. Access Monitoring Tools

- **Grafana Dashboard**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`
- **Prometheus**: http://localhost:9090
- **API Documentation**: http://localhost:8080/docs
- **Metrics Endpoint**: http://localhost:8080/metrics

## 📊 Available Metrics

### HTTP Metrics
- `http_requests_total` - Total HTTP requests by method, endpoint, and status code
- `http_request_duration_seconds` - HTTP request duration histogram

### RAG-Specific Metrics
- `rag_queries_total` - Total RAG queries processed by user
- `rag_query_duration_seconds` - RAG query processing duration
- `rag_query_confidence` - RAG query confidence scores
- `rag_sources_retrieved` - Number of sources retrieved per query

### Document Indexing Metrics
- `documents_indexed_total` - Total documents indexed by source type
- `chunks_created_total` - Total document chunks created

### AI Model Metrics
- `embedding_requests_total` - Total embedding requests by model
- `embedding_duration_seconds` - Embedding generation duration
- `llm_requests_total` - Total LLM requests by model
- `llm_duration_seconds` - LLM generation duration
- `llm_tokens_used_total` - Total LLM tokens used by model and type

## 🎯 Grafana Dashboard

The dashboard includes the following panels:

1. **Request Rate** - HTTP requests per second
2. **Response Time** - 95th and 50th percentile response times
3. **RAG Queries** - RAG queries per second by user
4. **RAG Query Duration** - Query processing time
5. **RAG Confidence Scores** - Confidence score distribution
6. **Sources Retrieved** - Number of sources per query
7. **Documents Indexed** - Document indexing rate
8. **LLM Requests** - LLM requests per second by model

## 🔧 Configuration Files

### Prometheus Configuration
- **File**: `monitoring/prometheus.yml`
- **Purpose**: Defines what metrics to scrape and how often

### Grafana Configuration
- **Dashboard**: `monitoring/grafana-dashboard.json`
- **Datasource**: `monitoring/grafana-datasource.yml`

## 🧪 Testing

### Manual Testing

1. **Health Check**:
   ```bash
   curl http://localhost:8080/health
   ```

2. **Metrics Endpoint**:
   ```bash
   curl http://localhost:8080/metrics
   ```

3. **Index Documents**:
   ```bash
   curl -X POST http://localhost:8080/api/v1/index-sample-docs
   ```

4. **RAG Query**:
   ```bash
   curl -X POST http://localhost:8080/api/v1/coach \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test", "query": "Wie verbessere ich meine Lernroutine?", "context_limit": 3}'
   ```

### Automated Testing

```bash
# Run the comprehensive test script
python test_monitoring.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**:
   - Make sure ports 8080, 9090, and 3000 are available
   - Check with `lsof -i :8080` (or other ports)

2. **Prometheus Not Scraping**:
   - Check Prometheus targets: http://localhost:9090/targets
   - Verify the RAG app is running and accessible

3. **Grafana Not Loading**:
   - Check Grafana logs: `docker-compose logs grafana`
   - Verify Prometheus datasource is configured

4. **No Metrics in Grafana**:
   - Check if Prometheus is collecting data
   - Verify the dashboard queries are correct

### Useful Commands

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs rag-demo
docker-compose logs prometheus
docker-compose logs grafana

# Restart a service
docker-compose restart rag-demo

# Clean up
docker-compose down -v
```

## 📈 Performance Monitoring

### Key Metrics to Watch

1. **Response Time**: Should be < 2 seconds for most queries
2. **Error Rate**: Should be < 1% of total requests
3. **RAG Confidence**: Higher confidence indicates better source matching
4. **Token Usage**: Monitor LLM costs and usage patterns

### Alerting (Future Enhancement)

You can set up alerts for:
- High response times (> 5 seconds)
- High error rates (> 5%)
- Low confidence scores (< 0.3)
- High token usage spikes

## 🔄 Development Workflow

1. **Make changes** to the FastAPI app
2. **Rebuild** the container: `docker-compose up --build rag-demo`
3. **Test** the changes: `python test_monitoring.py`
4. **Check metrics** in Grafana
5. **Iterate** based on monitoring data

## 📚 Next Steps

1. **Set up alerts** for critical metrics
2. **Add custom dashboards** for specific use cases
3. **Implement log aggregation** (ELK stack)
4. **Add distributed tracing** (Jaeger)
5. **Set up automated testing** with monitoring validation

## 🎉 Success!

You now have a complete monitoring stack for your RAG application! The metrics will help you:

- **Monitor performance** in real-time
- **Debug issues** quickly
- **Optimize** the application based on data
- **Scale** based on actual usage patterns
- **Track costs** and resource usage

Happy monitoring! 🚀
