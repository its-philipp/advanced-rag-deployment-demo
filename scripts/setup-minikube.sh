#!/bin/bash

# Setup script for RAG Demo on minikube

set -e

echo "🚀 Setting up RAG Demo on minikube..."

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ minikube is not installed. Please install it first:"
    echo "   brew install minikube"
    exit 1
fi

# Start minikube
echo "📦 Starting minikube..."
minikube start --memory=4096 --cpus=2

# Enable ingress addon
echo "🌐 Enabling ingress addon..."
minikube addons enable ingress

# Build Docker image in minikube
echo "🔨 Building Docker image in minikube..."
eval $(minikube docker-env)
docker build -t rag-demo:latest .

# Apply Kubernetes manifests
echo "📋 Applying Kubernetes manifests..."
kubectl apply -k k8s/

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/qdrant -n rag-demo
kubectl wait --for=condition=available --timeout=300s deployment/rag-demo -n rag-demo

# Get service URL
echo "🌍 Getting service URL..."
SERVICE_URL=$(minikube service rag-demo-service -n rag-demo --url)

echo "✅ Setup complete!"
echo "🔗 Service URL: $SERVICE_URL"
echo "📊 Dashboard: minikube dashboard"
echo "📝 Logs: kubectl logs -f deployment/rag-demo -n rag-demo"
echo "🔍 Status: kubectl get pods -n rag-demo"
