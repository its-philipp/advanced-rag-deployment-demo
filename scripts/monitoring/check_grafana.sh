#!/bin/bash

echo "🔍 Checking Grafana dashboard status..."

# Check if Grafana is accessible
echo "1. Checking Grafana accessibility..."
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "   ✅ Grafana is accessible"
else
    echo "   ❌ Grafana is not accessible"
    exit 1
fi

# Check if Prometheus datasource exists
echo "2. Checking Prometheus datasource..."
if curl -s -u admin:admin http://localhost:3000/api/datasources | grep -q "Prometheus"; then
    echo "   ✅ Prometheus datasource found"
else
    echo "   ⚠️  Prometheus datasource not found"
fi

# Check for existing dashboards
echo "3. Checking for existing dashboards..."
DASHBOARDS=$(curl -s -u admin:admin http://localhost:3000/api/search?query=RAG)
if echo "$DASHBOARDS" | grep -q "RAG Demo"; then
    echo "   ✅ RAG Demo Dashboard found!"
    echo "   📊 Dashboard details:"
    echo "$DASHBOARDS" | jq '.[] | select(.title | contains("RAG Demo")) | {title: .title, url: .url}'
else
    echo "   ❌ RAG Demo Dashboard not found"
    echo "   📋 Available dashboards:"
    echo "$DASHBOARDS" | jq '.[] | {title: .title, url: .url}' 2>/dev/null || echo "   (No dashboards found or jq not available)"
fi

echo ""
echo "🌐 Access Grafana at: http://localhost:3000"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "🔧 If dashboard is missing, try:"
echo "   1. Go to http://localhost:3000"
echo "   2. Click the '+' icon in the left sidebar"
echo "   3. Select 'Import'"
echo "   4. Copy the contents of monitoring/dashboards/rag-dashboard.json"
echo "   5. Paste and import"
