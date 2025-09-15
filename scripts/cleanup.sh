#!/bin/bash

# Cleanup script for RAG Demo on minikube

set -e

echo "🧹 Cleaning up RAG Demo from minikube..."

# Delete Kubernetes resources
echo "📋 Deleting Kubernetes resources..."
kubectl delete -k k8s/ --ignore-not-found=true

# Stop minikube (optional)
read -p "🛑 Do you want to stop minikube? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🛑 Stopping minikube..."
    minikube stop
fi

echo "✅ Cleanup complete!"
