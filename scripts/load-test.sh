#!/bin/bash

# Load testing script for RAG Demo

set -e

SERVICE_URL=${1:-"http://localhost:8080"}
CONCURRENT_USERS=${2:-5}
REQUESTS_PER_USER=${3:-10}

echo "🚀 Starting load test..."
echo "📊 Service URL: $SERVICE_URL"
echo "👥 Concurrent users: $CONCURRENT_USERS"
echo "📝 Requests per user: $REQUESTS_PER_USER"

# Function to make a single request
make_request() {
    local user_id=$1
    local request_num=$2
    
    curl -s -X POST "$SERVICE_URL/api/v1/coach" \
        -H "Content-Type: application/json" \
        -d "{
            \"user_id\": \"user_$user_id\",
            \"query\": \"Wie verbessere ich meine Lernroutine für Mathe? Request $request_num\",
            \"context_limit\": 3
        }" > /dev/null
    
    echo "✅ User $user_id completed request $request_num"
}

# Function to run requests for a single user
run_user_requests() {
    local user_id=$1
    for i in $(seq 1 $REQUESTS_PER_USER); do
        make_request $user_id $i
        sleep 0.5  # Small delay between requests
    done
}

echo "🔥 Starting load test with $CONCURRENT_USERS concurrent users..."

# Start background processes for each user
pids=()
for user in $(seq 1 $CONCURRENT_USERS); do
    run_user_requests $user &
    pids+=($!)
done

# Wait for all background processes to complete
echo "⏳ Waiting for all requests to complete..."
for pid in "${pids[@]}"; do
    wait $pid
done

echo "✅ Load test completed!"
echo "📊 Check HPA status: kubectl get hpa -n rag-demo"
echo "📈 Check pod scaling: kubectl get pods -n rag-demo -w"
