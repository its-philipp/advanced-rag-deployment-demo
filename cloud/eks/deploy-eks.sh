#!/bin/bash

# EKS Deployment Script
set -e

CLUSTER_NAME="rag-demo-cluster"
REGION="us-west-2"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Deploying RAG Demo to AWS EKS..."

# Check if required tools are installed
if ! command -v eksctl &> /dev/null; then
    echo "❌ eksctl is not installed. Please install it first:"
    echo "   https://eksctl.io/introduction/installation/"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   https://aws.amazon.com/cli/"
    exit 1
fi

# Create EKS cluster
echo "🏗️ Creating EKS cluster..."
eksctl create cluster -f eks-cluster.yaml

# Get cluster credentials
echo "🔑 Getting cluster credentials..."
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME

# Create ECR repository
echo "🐳 Creating ECR repository..."
aws ecr create-repository --repository-name rag-demo --region $REGION || true

# Get ECR login token
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and push Docker image
echo "🐳 Building and pushing Docker image..."
docker build -t rag-demo:latest .
docker tag rag-demo:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/rag-demo:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/rag-demo:latest

# Update deployment with ECR URL
echo "📝 Updating deployment with ECR URL..."
sed -i.bak "s/ACCOUNT_ID/$ACCOUNT_ID/g" eks-deployment.yaml

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
kubectl apply -f eks-deployment.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/rag-demo -n rag-demo

# Get external IP
echo "🌍 Getting external IP..."
EXTERNAL_IP=$(kubectl get service rag-demo-service -n rag-demo -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "✅ Deployment complete!"
echo "🔗 External URL: http://$EXTERNAL_IP"
echo "📊 Dashboard: aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME && kubectl proxy"
echo "📝 Logs: kubectl logs -f deployment/rag-demo -n rag-demo"
