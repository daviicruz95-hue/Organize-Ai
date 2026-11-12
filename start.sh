#!/bin/bash
set -e

echo "🚀 Iniciando Organize Aí..."

# Configuração de persistência para o WhatsApp e dados
if [ -n "$DATA_DIR" ] && [ -d "$DATA_DIR" ]; then
    echo "💾 Configurando persistência em $DATA_DIR..."
    mkdir -p "$DATA_DIR/auth_info_baileys"
    if [ -d "/app/whatsapp-service/auth_info_baileys" ] && [ -f "/app/whatsapp-service/auth_info_baileys/creds.json" ]; then
        if [ ! -f "$DATA_DIR/auth_info_baileys/creds.json" ]; then
            echo "📦 Migrando credenciais do WhatsApp para o volume persistente..."
            cp -r /app/whatsapp-service/auth_info_baileys/* "$DATA_DIR/auth_info_baileys/" 2>/dev/null || true
        fi
    fi
fi

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
