#!/bin/bash

# GKE Deployment Script
set -e

PROJECT_ID=${1:-"your-project-id"}
CLUSTER_NAME="rag-demo-cluster"
ZONE="us-central1-b"

echo "🚀 Deploying RAG Demo to Google GKE..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable dns.googleapis.com

# Create GKE cluster
echo "🏗️ Creating GKE cluster..."
gcloud container clusters create $CLUSTER_NAME \
    --zone=$ZONE \
    --num-nodes=2 \
    --machine-type=e2-medium \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=5 \
    --enable-autorepair \
    --enable-autoupgrade \
    --enable-ip-alias \
    --network="default" \
    --subnetwork="default"

# Get cluster credentials
echo "🔑 Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE

# Build and push Docker image
echo "🐳 Building and pushing Docker image..."
cd ../..
gcloud builds submit --tag gcr.io/$PROJECT_ID/rag-demo:latest .
cd cloud/gke

# Create namespace
echo "📦 Creating namespace..."
kubectl create namespace rag-demo

# Apply configurations
echo "📋 Applying configurations..."
kubectl apply -f ../../k8s/configmap.yaml
kubectl apply -f ../../k8s/secret.yaml
kubectl apply -f ../../k8s/qdrant-deployment.yaml

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/qdrant -n rag-demo

# Apply RAG demo deployment with personalized coaching
echo "🚀 Deploying personalized RAG demo..."
kubectl apply -f gke-deployment-personalized.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/rag-demo -n rag-demo

# Get external IP
echo "🌍 Getting external IP..."
EXTERNAL_IP=$(kubectl get service rag-demo-service -n rag-demo -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "✅ Deployment complete!"
echo "🔗 External IP: $EXTERNAL_IP"
echo "📊 Dashboard: gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE && kubectl proxy"
echo "📝 Logs: kubectl logs -f deployment/rag-demo -n rag-demo"
