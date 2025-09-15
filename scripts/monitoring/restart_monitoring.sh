#!/bin/bash

echo "🔄 Restarting monitoring stack..."

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Remove old volumes to ensure clean start
echo "Cleaning up old volumes..."
docker volume rm rag-demo_grafana_data 2>/dev/null || true
docker volume rm rag-demo_prometheus_data 2>/dev/null || true

# Start the stack
echo "Starting monitoring stack..."
docker-compose up --build -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check if services are running
echo "Checking service status..."
docker-compose ps

echo ""
echo "🎉 Monitoring stack restarted!"
echo ""
echo "📊 Access your monitoring tools:"
echo "   • Grafana: http://localhost:3000 (admin/admin)"
echo "   • Prometheus: http://localhost:9090"
echo "   • API Docs: http://localhost:8080/docs"
echo "   • Metrics: http://localhost:8080/metrics"
echo ""
echo "🔍 To check if dashboard is loaded:"
echo "   1. Go to http://localhost:3000"
echo "   2. Login with admin/admin"
echo "   3. Look for 'RAG Demo Dashboard' in the dashboard list"
echo "   4. If not there, check the 'Browse' section"
echo ""
echo "🧪 To generate some test data:"
echo "   python tests/integration/test_monitoring.py"
