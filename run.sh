#!/bin/bash

# Start Redis (if not already running)
if ! pgrep -x "redis-server" > /dev/null; then
    echo "Starting Redis..."
    redis-server --daemonize yes
fi

# Start Dapr sidecar
echo "Starting Dapr sidecar..."
dapr run --app-id multi-agent-chat --app-port 6001 --dapr-http-port 3500 --dapr-grpc-port 50001 --config dapr-config.yaml python app/chat.py &

# Wait for Dapr to start
sleep 5

# Start Streamlit app
echo "Starting Streamlit application..."
streamlit run app/app.py --server.port 8501

# Cleanup on exit
trap 'kill $(jobs -p)' EXIT