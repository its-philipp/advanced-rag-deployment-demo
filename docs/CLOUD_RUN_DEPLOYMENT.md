# ☁️ Google Cloud Run Deployment Guide

This guide walks you through deploying your RAG application to Google Cloud Run.

## 🎯 Why Cloud Run?

- ✅ **No image size limits** (unlike Railway's 4GB limit)
- ✅ **Serverless** (pay only when processing requests)
- ✅ **Auto-scales to zero** (no cost when idle)
- ✅ **Generous free tier** (2 million requests/month)
- ✅ **Perfect for ML workloads** (can handle large dependencies)

## 📋 Prerequisites

### 1. Google Cloud Account
- Go to: https://console.cloud.google.com
- Sign up for free account
- Get $300 free credits for 90 days

### 2. Install Google Cloud CLI

**Option A: Homebrew (Recommended)**
```bash
brew install --cask google-cloud-sdk
```

**Option B: Manual Download**
- Go to: https://cloud.google.com/sdk/docs/install
- Download macOS installer

**Option C: Use Cloud Shell**
- Go to: https://console.cloud.google.com
- Click Cloud Shell icon (terminal) in top right

### 3. Enable Required APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## 🚀 Step-by-Step Deployment

### Step 1: Authenticate with Google Cloud
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Build and Push Docker Image
```bash
# Build the image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/rag-demo

# Or build locally and push
docker build -f docker/versions/Dockerfile.cloudrun -t gcr.io/YOUR_PROJECT_ID/rag-demo .
docker push gcr.io/YOUR_PROJECT_ID/rag-demo
```

### Step 3: Deploy to Cloud Run
```bash
gcloud run deploy rag-demo \
  --image gcr.io/YOUR_PROJECT_ID/rag-demo \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10
```

### Step 4: Set Environment Variables
```bash
gcloud run services update rag-demo \
  --region us-central1 \
  --set-env-vars="OPENAI_API_KEY=your_openai_key" \
  --set-env-vars="QDRANT_URL=https://your-qdrant-cluster.cloud.qdrant.io" \
  --set-env-vars="QDRANT_API_KEY=your_qdrant_key" \
  --set-env-vars="QDRANT_COLLECTION=rag_documents" \
  --set-env-vars="EMBEDDING_MODEL=text-embedding-3-small" \
  --set-env-vars="LLM_MODEL=gpt-4o-mini"
```

## 🧪 Testing Your Deployment

### 1. Get the Service URL
```bash
gcloud run services describe rag-demo --region us-central1 --format 'value(status.url)'
```

### 2. Test Endpoints
```bash
# Health check
curl https://YOUR_SERVICE_URL/health

# Metrics
curl https://YOUR_SERVICE_URL/metrics

# Index documents
curl -X POST https://YOUR_SERVICE_URL/api/v1/index-sample-docs

# RAG query
curl -X POST https://YOUR_SERVICE_URL/api/v1/coach \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "query": "Wie verbessere ich meine Lernroutine?", "context_limit": 3}'
```

## 💰 Cost Estimation

### Free Tier (First 90 days)
- **$300 free credits**
- **2 million requests/month**
- **1GB memory, 1 vCPU per request**
- **1GB network egress/month**

### After Free Tier
- **$0.40 per million requests**
- **$0.00002400 per vCPU-second**
- **$0.00000250 per GiB-second**
- **$0.12 per GB network egress**

### Your App Estimate
- **Idle time**: $0 (scales to zero)
- **Active time**: ~$0.01-0.05 per request
- **Monthly (1000 requests)**: ~$1-5

## 🔧 Configuration Options

### Memory and CPU
```bash
--memory 2Gi          # 2GB RAM
--cpu 2               # 2 vCPUs
--concurrency 80      # 80 concurrent requests per instance
```

### Scaling
```bash
--min-instances 0     # Scale to zero when idle
--max-instances 10    # Max 10 instances
```

### Timeout
```bash
--timeout 900         # 15 minutes max request time
```

## 🛠️ Useful Commands

### View Logs
```bash
gcloud run services logs read rag-demo --region us-central1
```

### Update Service
```bash
gcloud run services update rag-demo --region us-central1
```

### Delete Service
```bash
gcloud run services delete rag-demo --region us-central1
```

### List Services
```bash
gcloud run services list
```

## 🎯 Advantages Over Railway

1. **No Image Size Limits**: Can use full ML dependencies
2. **Better Scaling**: Scales to zero when idle
3. **More Generous Free Tier**: $300 vs $5
4. **Better for ML**: Designed for compute-intensive workloads
5. **Global CDN**: Faster response times worldwide

## 🚨 Important Notes

1. **Cold Starts**: First request after idle period takes 10-30 seconds
2. **Memory Limits**: Max 8GB per instance
3. **Timeout**: Max 60 minutes per request
4. **Concurrency**: Max 1000 concurrent requests per instance

## 🎉 Success!

Once deployed, you'll have:
- ✅ **Serverless RAG application**
- ✅ **Auto-scaling to zero**
- ✅ **Global HTTPS endpoint**
- ✅ **Full ML capabilities**
- ✅ **Cost-effective for sporadic usage**

Your RAG application will be accessible via a Cloud Run URL and ready for production use!
