#!/bin/bash
set -e

echo "🚀 Iniciando Organize Aí..."

# Start python server in background
python3 server.py &
PYTHON_PID=$!

# Wait 2 seconds for server to bind
sleep 2

# Start WhatsApp bot if configured
if [ -d "whatsapp-service" ]; then
    echo "🤖 Iniciando serviço do WhatsApp..."
    cd whatsapp-service
    node bot.js &
    BOT_PID=$!
    cd ..
fi

# Wait for both processes
wait -n $PYTHON_PID $BOT_PID
