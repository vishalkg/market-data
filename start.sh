#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Starting Enhanced Finance Data MCP Server in stdio mode..."

# Activate virtual environment and run the server
source "$DIR/../venv/bin/activate"

# Use the installed package entry point in stdio mode
exec python -m finance_data_server.server "$@"
