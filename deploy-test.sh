#!/bin/bash
# Deployment test script for MCP Instana server
# This script can be used to validate the deployment before promoting to higher environments

set -e

echo "Starting MCP Instana deployment tests..."

# Check if required environment variables are set
if [ -z "$INSTANA_BASE_URL" ] || [ -z "$INSTANA_API_TOKEN" ]; then
    echo "Warning: INSTANA_BASE_URL and INSTANA_API_TOKEN should be set for full testing"
fi

# Function to kill server on exit
cleanup() {
    if [ ! -z "$SERVER_PID" ]; then
        echo "Cleaning up server process..."
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Test 1: Check if the server starts successfully
echo "Test 1: Checking server startup..."
python -m src.core.server --transport streamable-http > /tmp/mcp-server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start (max 10 seconds)
echo "Waiting for server to start..."
for i in {1..20}; do
    sleep 0.5
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        echo "✓ Server started successfully"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "✗ Server failed to start within 10 seconds"
        echo "Server logs:"
        cat /tmp/mcp-server.log
        exit 1
    fi
done

# Test 2: Check health endpoint
echo "Test 2: Checking health endpoint..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
    echo "Server logs:"
    cat /tmp/mcp-server.log
    exit 1
fi

echo "All deployment tests passed successfully!"
exit 0

# Made with Bob
