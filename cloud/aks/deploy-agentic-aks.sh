#!/bin/bash

# AKS Agentic RAG Deployment Script
set -e

RESOURCE_GROUP=${1:-"rag-demo-rg"}
CLUSTER_NAME=${2:-"agentic-rag-cluster"}
LOCATION=${3:-"eastus"}
ACR_NAME=${4:-"agenticragacr"}

echo "🚀 Deploying Agentic RAG to Azure Kubernetes Service (AKS)..."
echo "Resource Group: $RESOURCE_GROUP"
echo "Cluster Name: $CLUSTER_NAME"
echo "Location: $LOCATION"
echo "ACR Name: $ACR_NAME"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install it first:"
    echo "   https://kubernetes.io/docs/tasks/tools/install-kubectl/"
    exit 1
fi

# Login to Azure (if not already logged in)
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "Please log in to Azure..."
    az login
fi

# Set subscription (optional)
echo "📋 Setting Azure subscription..."
az account set --subscription $(az account show --query id -o tsv)

# Create resource group if it doesn't exist
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "🐳 Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
echo "ACR Login Server: $ACR_LOGIN_SERVER"

# Create AKS cluster
echo "🏗️ Creating AKS cluster..."
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $CLUSTER_NAME \
    --location $LOCATION \
    --node-count 3 \
    --node-vm-size Standard_D4s_v3 \
    --enable-addons monitoring \
    --enable-managed-identity \
    --attach-acr $ACR_NAME \
    --generate-ssh-keys

# Get cluster credentials
echo "🔑 Getting cluster credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME

# Install NGINX Ingress Controller
echo "🌐 Installing NGINX Ingress Controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller to be ready
echo "⏳ Waiting for NGINX Ingress Controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

# Build and push Docker image
echo "🐳 Building and pushing Docker image..."
cd ../..
az acr build --registry $ACR_NAME --image agentic-rag:latest .
cd cloud/aks

# Create namespace
echo "📦 Creating namespace..."
kubectl create namespace rag-demo

# Create secrets (you'll need to replace these with actual values)
echo "🔐 Creating secrets..."
kubectl create secret generic azure-secrets \
  --from-literal=openai-endpoint="your-openai-endpoint" \
  --from-literal=openai-key="your-openai-key" \
  --from-literal=qdrant-key="your-qdrant-key" \
  -n rag-demo

# Deploy Qdrant (if not already deployed)
echo "🗄️ Deploying Qdrant..."
kubectl apply -f ../../k8s/qdrant-deployment.yaml

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/qdrant -n rag-demo

# Deploy Agentic RAG
echo "🚀 Deploying Agentic RAG..."
kubectl apply -f agentic-rag-deployment.yaml

# Wait for deployment
echo "⏳ Waiting for Agentic RAG deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/agentic-rag -n rag-demo

# Get external IP
echo "🌍 Getting external IP..."
EXTERNAL_IP=$(kubectl get service agentic-rag-service -n rag-demo -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -z "$EXTERNAL_IP" ]; then
    echo "⏳ External IP not yet assigned. Waiting..."
    sleep 30
    EXTERNAL_IP=$(kubectl get service agentic-rag-service -n rag-demo -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
fi

echo "✅ Deployment complete!"
echo "🔗 External IP: $EXTERNAL_IP"
echo "📊 Dashboard: az aks browse --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME"
echo "📝 Logs: kubectl logs -f deployment/agentic-rag -n rag-demo"
echo "🧪 Test: curl -X GET http://$EXTERNAL_IP/health"

# Test the deployment
echo "🧪 Testing deployment..."
if [ ! -z "$EXTERNAL_IP" ]; then
    sleep 10
    curl -X GET "http://$EXTERNAL_IP/health" || echo "❌ Health check failed"
    echo ""
    echo "🧠 Test Agentic RAG:"
    echo "curl -X POST http://$EXTERNAL_IP/api/agentic/agentic-query \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"user_id\": \"test\", \"query\": \"Hello, can you help me learn?\"}'"
fi
