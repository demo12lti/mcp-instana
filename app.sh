#!/bin/bash
# Startup script for MCP Instana Server on Cirrus
# This script starts the MCP server in streamable-http mode

# Set default port if not provided
export PORT=${PORT:-8080}

# Start the MCP server
python -m src.core.server --transport streamable-http --port ${PORT}

# Made with Bob
