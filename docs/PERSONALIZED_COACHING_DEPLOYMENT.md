# 🎯 Personalized Coaching System - GKE Deployment Guide

This guide covers deploying the personalized coaching system to Google Kubernetes Engine (GKE) with persistent storage for user data.

## 🚀 **Quick Start**

### **Prerequisites**
- Google Cloud SDK (`gcloud`) installed
- `kubectl` installed
- Docker installed
- OpenAI API key
- Qdrant API key (optional)

### **1. Set up Google Cloud Project**

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable dns.googleapis.com
```

### **2. Deploy to GKE**

```bash
# Navigate to the GKE deployment directory
cd cloud/gke

# Make the script executable
chmod +x deploy-gke.sh

# Deploy with your project ID
./deploy-gke.sh $PROJECT_ID
```

### **3. Configure Secrets**

After deployment, update the secrets with your API keys:

```bash
# Update OpenAI API key
kubectl create secret generic rag-demo-secrets \
  --from-literal=OPENAI_API_KEY="your-openai-api-key" \
  --from-literal=QDRANT_API_KEY="your-qdrant-api-key" \
  -n rag-demo --dry-run=client -o yaml | kubectl apply -f -
```

## 🏗️ **Architecture Overview**

### **Components Deployed:**

1. **RAG Demo Application** - FastAPI with personalized coaching
2. **Qdrant Vector Database** - For document storage and retrieval
3. **Persistent Storage** - For user profiles and chat history
4. **Load Balancer** - For external access
5. **Horizontal Pod Autoscaler** - For automatic scaling
6. **SSL Certificate** - For HTTPS (optional)

### **Key Features:**

- ✅ **User-specific vector collections** in Qdrant
- ✅ **Persistent user data storage** (profiles, chat history)
- ✅ **Personalized coaching agents** per user
- ✅ **Hybrid search** (user + global knowledge)
- ✅ **Learning style personalization**
- ✅ **Chat history tracking**
- ✅ **Personal document upload**

## 📊 **Storage Configuration**

### **User Data Persistence:**
- **PVC Size**: 10Gi (configurable)
- **Storage Class**: `standard-rwo` (single-writer)
- **Mount Path**: `/app/.rag-demo`
- **Data Stored**:
  - User profiles (`profile.json`)
  - Chat history (`chat_history.json`)
  - Learning preferences
  - Personal documents

### **Scaling Considerations:**
- **Min Replicas**: 2 (for high availability)
- **Max Replicas**: 10 (auto-scaling)
- **CPU Target**: 70%
- **Memory Target**: 80%

## 🔧 **Configuration**

### **Environment Variables:**

```yaml
# Application Configuration
APP_HOST: "0.0.0.0"
APP_PORT: "8080"

# Qdrant Configuration
QDRANT_URL: "http://qdrant:6333"
QDRANT_COLLECTION: "rag_documents"

# OpenAI Configuration
OPENAI_API_KEY: "your-openai-api-key"
EMBEDDING_MODEL: "text-embedding-3-small"
LLM_MODEL: "gpt-4o-mini"
```

### **Resource Limits:**
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

## 🌐 **API Endpoints**

### **Personalized Coaching:**
- `POST /api/v1/personalized-coach` - Get personalized responses
- `GET /api/v1/users/{user_id}/profile` - Get user profile
- `PUT /api/v1/users/{user_id}/preferences` - Update preferences
- `PUT /api/v1/users/{user_id}/learning-goals` - Update goals
- `POST /api/v1/users/{user_id}/documents` - Add personal docs
- `GET /api/v1/users/{user_id}/context` - Get chat history

### **Document Management:**
- `POST /api/v1/index-sample-docs` - Index sample documents
- `POST /api/v1/index-document` - Index single document

## 🧪 **Testing the Deployment**

### **1. Get External IP:**
```bash
kubectl get service rag-demo-service -n rag-demo
```

### **2. Test Health Check:**
```bash
curl http://EXTERNAL_IP/health
```

### **3. Test Personalized Coaching:**
```bash
# Set up a user profile
curl -X PUT "http://EXTERNAL_IP/api/v1/users/test_user/preferences" \
  -H "Content-Type: application/json" \
  -d '{
    "learning_style": "visual",
    "subject_focus": "mathematics",
    "difficulty_level": "intermediate"
  }'

# Test personalized response
curl -X POST "http://EXTERNAL_IP/api/v1/personalized-coach" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "query": "Wie kann ich meine Mathematik-Fähigkeiten verbessern?",
    "context_limit": 3,
    "use_hybrid": true
  }'
```

## 📈 **Monitoring**

### **View Logs:**
```bash
# Application logs
kubectl logs -f deployment/rag-demo -n rag-demo

# Qdrant logs
kubectl logs -f deployment/qdrant -n rag-demo
```

### **Check Pod Status:**
```bash
kubectl get pods -n rag-demo
kubectl get pvc -n rag-demo
kubectl get hpa -n rag-demo
```

### **Access Grafana Dashboard:**
```bash
# Port forward to access locally
kubectl port-forward service/grafana 3000:80 -n monitoring
# Open http://localhost:3000
```

## 🔄 **Scaling**

### **Manual Scaling:**
```bash
kubectl scale deployment rag-demo --replicas=5 -n rag-demo
```

### **Auto-scaling:**
The HPA will automatically scale based on CPU and memory usage:
- **CPU**: 70% threshold
- **Memory**: 80% threshold
- **Min Replicas**: 2
- **Max Replicas**: 10

## 🛠️ **Troubleshooting**

### **Common Issues:**

1. **Pod CrashLoopBackOff:**
   ```bash
   kubectl describe pod <pod-name> -n rag-demo
   kubectl logs <pod-name> -n rag-demo
   ```

2. **Storage Issues:**
   ```bash
   kubectl get pvc -n rag-demo
   kubectl describe pvc rag-demo-user-data -n rag-demo
   ```

3. **Qdrant Connection Issues:**
   ```bash
   kubectl get svc -n rag-demo
   kubectl exec -it <rag-demo-pod> -n rag-demo -- curl http://qdrant:6333/collections
   ```

### **Debug Commands:**
```bash
# Check all resources
kubectl get all -n rag-demo

# Check events
kubectl get events -n rag-demo --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n rag-demo
```

## 🔒 **Security Considerations**

1. **API Keys**: Stored as Kubernetes secrets
2. **Network**: Internal communication between pods
3. **Storage**: Persistent volumes with access controls
4. **HTTPS**: Optional SSL certificate for external access

## 💰 **Cost Optimization**

### **Resource Tuning:**
- Adjust CPU/memory requests based on usage
- Use preemptible nodes for development
- Set appropriate HPA thresholds
- Monitor storage usage

### **Estimated Costs (US Central):**
- **GKE Cluster**: ~$50-100/month
- **Persistent Storage**: ~$5-10/month
- **Load Balancer**: ~$20/month
- **Total**: ~$75-130/month

## 🚀 **Production Recommendations**

1. **Use managed Qdrant** instead of self-hosted
2. **Implement proper backup** for user data
3. **Set up monitoring** with Prometheus/Grafana
4. **Configure proper ingress** with domain and SSL
5. **Use Cloud SQL** for user metadata (optional)
6. **Implement rate limiting** for API endpoints

## 📝 **Next Steps**

1. **Custom Domain**: Update ingress with your domain
2. **SSL Certificate**: Configure managed certificate
3. **Monitoring**: Set up alerts and dashboards
4. **Backup**: Implement user data backup strategy
5. **CI/CD**: Set up automated deployments

---

## 🎉 **Success!**

Your personalized coaching system is now running on GKE with:
- ✅ User-specific personalization
- ✅ Persistent data storage
- ✅ Auto-scaling capabilities
- ✅ Production-ready configuration

The system can now handle multiple users with personalized coaching experiences!
