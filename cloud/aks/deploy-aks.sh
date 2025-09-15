#!/bin/bash

# AKS Deployment Script
set -e

RESOURCE_GROUP="rag-demo-rg"
CLUSTER_NAME="rag-demo-cluster"
LOCATION="eastus"
ACR_NAME="ragdemo"

echo "🚀 Deploying RAG Demo to Azure AKS..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure
echo "🔐 Logging into Azure..."
az login

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create ACR
echo "🐳 Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Create AKS cluster
echo "🏗️ Creating AKS cluster..."
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $CLUSTER_NAME \
    --node-count 2 \
    --node-vm-size Standard_B2s \
    --kubernetes-version 1.28 \
    --enable-addons monitoring,http_application_routing \
    --enable-managed-identity \
    --enable-azure-policy \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 5 \
    --attach-acr $ACR_NAME

# Get cluster credentials
echo "🔑 Getting cluster credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME

# Get ACR login server
echo "🔐 Logging into ACR..."
az acr login --name $ACR_NAME
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv)

# Build and push Docker image
echo "🐳 Building and pushing Docker image..."
docker build -t rag-demo:latest .
docker tag rag-demo:latest $ACR_LOGIN_SERVER/rag-demo:latest
docker push $ACR_LOGIN_SERVER/rag-demo:latest

# Update deployment with ACR URL
echo "📝 Updating deployment with ACR URL..."
sed -i.bak "s/ragdemo.azurecr.io/$ACR_LOGIN_SERVER/g" aks-deployment.yaml

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

# Apply RAG demo deployment
echo "🚀 Deploying RAG demo..."
kubectl apply -f aks-deployment.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/rag-demo -n rag-demo

# Get external IP
echo "🌍 Getting external IP..."
EXTERNAL_IP=$(kubectl get service rag-demo-service -n rag-demo -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "✅ Deployment complete!"
echo "🔗 External IP: $EXTERNAL_IP"
echo "📊 Dashboard: az aks browse --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME"
echo "📝 Logs: kubectl logs -f deployment/rag-demo -n rag-demo"
